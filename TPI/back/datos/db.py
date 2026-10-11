import os
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, Date
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


def crear_esquema():
    Base.metadata.create_all(engine)


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
