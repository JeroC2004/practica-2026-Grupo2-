import os
import tempfile

# Se fija ANTES de que cualquier test importe datos.db (que lee DB_PATH al
# definir el engine): así ningún test, sea de este proyecto o uno que se
# agregue después, puede terminar escribiendo en TPI/back/tpi.db por error.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(prefix="tpi_tests_"), "test.db")
