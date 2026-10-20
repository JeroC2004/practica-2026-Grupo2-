import os
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "tpi.db"))

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ContribuyenteORM(Base):
    __tablename__ = "contribuyentes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cuit = Column(String(13), unique=True, nullable=False)
    razon_social = Column(String(200), nullable=False)
    condicion_iva = Column(String(30), nullable=False)
    password_hash = Column(String(200), nullable=False)


class ComprobanteORM(Base):
    __tablename__ = "comprobantes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cuit_contribuyente = Column(String(13), nullable=False, index=True)
    tipo = Column(String(2), nullable=False)
    punto_venta = Column(Integer, nullable=False)
    numero = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)
    cuit_contraparte = Column(String(13), nullable=False)
    neto_gravado = Column(Float, nullable=False, default=0.0)
    neto_exento = Column(Float, nullable=False, default=0.0)
    iva = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    condicion = Column(String(10), nullable=False)
    origen = Column(String(10), nullable=False, default="manual")
    numero_arca = Column(Integer, nullable=True)
    cae = Column(String(20), nullable=True)
    cae_vencimiento = Column(Date, nullable=True)


_COLUMNAS_NUEVAS_COMPROBANTES = {
    "numero_arca": "INTEGER",
    "cae": "VARCHAR(20)",
    "cae_vencimiento": "DATE",
}


def crear_esquema():
    Base.metadata.create_all(engine)
    _migrar_columnas_nuevas()


def _migrar_columnas_nuevas():
    """
    create_all() crea tablas que faltan, pero no agrega columnas nuevas a una
    tabla que ya existe de una versión anterior. Este ALTER TABLE evita tener
    que borrar la base de datos cada vez que el modelo gana un campo.
    """
    inspector = inspect(engine)
    if "comprobantes" not in inspector.get_table_names():
        return
    columnas_existentes = {columna["name"] for columna in inspector.get_columns("comprobantes")}
    with engine.begin() as conexion:
        for nombre, tipo_sql in _COLUMNAS_NUEVAS_COMPROBANTES.items():
            if nombre not in columnas_existentes:
                conexion.execute(text(f"ALTER TABLE comprobantes ADD COLUMN {nombre} {tipo_sql}"))


@contextmanager
def obtener_sesion():
    sesion = SessionLocal()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()
