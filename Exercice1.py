from pathlib import Path
from contextlib import contextmanager, ExitStack
import logging
import os

logging.basicConfig(level=logging.INFO)

class TempFileWriter:
    def __init__(self, filename="temp.txt"):
        self.filepath = Path(filename)
        self.f = None
        
    def __enter__(self):
        logging.info(f"Ouverture du fichier temporaire: {self.filepath}")
        self.f = self.filepath.open("w")
        return self.f
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info(f"Fermeture et suppression de: {self.filepath}")
        if self.f and not self.f.closed:
            self.f.close()
        if self.filepath.exists():
            self.filepath.unlink()
        if exc_type is not None:
            logging.error(f"Exception: {exc_type.__name__}: {exc_val}")
        return True

@contextmanager
def temp_file_writer(filename="temp.txt", mode="w"):
    path = Path(filename)
    f = None
    try:
        logging.info(f"[contextmanager] Ouverture de {filename}")
        f = path.open(mode)
        yield f
        logging.info(f"[contextmanager] Bloc with terminé")
    except Exception as e:
        logging.error(f"[contextmanager] Erreur: {e}")
        raise
    finally:
        logging.info(f"[contextmanager] Nettoyage")
        if f and not f.closed:
            f.close()
        if path.exists():
            path.unlink()

@contextmanager
def temp_file_reader_writer():
    path = Path("data.txt")
    with path.open("w") as f:
        f.write("Données initiales\n")
    with path.open("r") as f:
        content = f.read()
        yield content
    if path.exists():
        path.unlink()

class DatabaseConnection:
    def __init__(self, name):
        self.name = name
        self.connected = False
    
    def connect(self):
        logging.info(f"Connexion a la base '{self.name}'")
        self.connected = True
        return self
    
    def disconnect(self):
        logging.info(f"Déconnexion de la base '{self.name}'")
        self.connected = False
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

@contextmanager
def managed_lock(lock_name):
    import time
    logging.info(f"Acquisition du verrou: {lock_name}")
    yield lock_name
    logging.info(f"Liberation du verrou: {lock_name}")

def write_to_multiple_files(file_list, content):
    with ExitStack() as stack:
        files = []
        for filepath in file_list:
            try:
                f = stack.enter_context(open(filepath, "w"))
                files.append(f)
                logging.info(f"Fichier ouvert: {filepath}")
            except Exception as e:
                logging.error(f"Erreur ouverture {filepath}: {e}")
                raise
        for i, f in enumerate(files):
            f.write(f"{content} - fichier {i+1}\n")
            logging.info(f"Ecriture dans: {file_list[i]}")
        print(f"✓ {len(files)} fichiers ecrits")

class LoggingContextManager:
    def __enter__(self):
        import datetime
        self.start_time = datetime.datetime.now()
        print(f"[{self.start_time}] ENTREE dans le contexte")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import datetime
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        print(f"[{end_time}] SORTIE du contexte (duree: {duration.total_seconds():.2f}s)")
        if exc_type:
            print(f"   Exception: {exc_type.__name__}: {exc_val}")
        return True

class DatabaseTransaction:
    def __init__(self, db_name):
        self.db_name = db_name
        self.transaction_open = False
    
    def __enter__(self):
        print(f"Debut transaction sur {self.db_name}")
        self.transaction_open = True
        return self
    
    def execute(self, query):
        if not self.transaction_open:
            raise Exception("Transaction non ouverte")
        print(f"Execution: {query}")
        return "Resultat simulé"
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(f"COMMIT transaction sur {self.db_name}")
            self.commit()
        else:
            print(f"ROLLBACK transaction sur {self.db_name} (raison: {exc_val})")
            self.rollback()
        self.transaction_open = False
    
    def commit(self):
        print("Operations validees")
    
    def rollback(self):
        print("Opérations annulees")

print("=== Partie 1: TempFileWriter ===")
try:
    with TempFileWriter("test_temp.txt") as f:
        f.write("Ligne 1: Contenu temporaire\n")
        f.write("Ligne 2: Autre contenu\n")
    if not Path("test_temp.txt").exists():
        print(" Fichier temporaire correctement supprimé")
except Exception as e:
    print(f"Exception: {e}")

print("\n Partie 2: contextmanager ")
with temp_file_writer("temp2.txt") as f:
    f.write("Test avec contextmanager\n")
    f.write("Ligne supplémentaire\n")

with temp_file_reader_writer() as data:
    print(f"Données lues: {data.strip()}")

print("\n Partie 3: ExitStack ")
try:
    files_to_create = ["doc_a.txt", "doc_b.txt", "doc_c.txt"]
    write_to_multiple_files(files_to_create, "Contenu de test")
except Exception as e:
    print(f"Erreur: {e}")

for f in files_to_create:
    try:
        with open(f, "r") as test_file:
            print(f"Contenu de {f}: {test_file.read().strip()}")
    except:
        print(f"Fichier {f} correctement fermé")

print("\n--- Exemple avec ressources heterogenes ---")
with ExitStack() as stack:
    file1 = stack.enter_context(open("log1.txt", "w"))
    file2 = stack.enter_context(open("log2.txt", "w"))
    db1 = stack.enter_context(DatabaseConnection("users_db"))
    db2 = stack.enter_context(DatabaseConnection("products_db"))
    lock = stack.enter_context(managed_lock("resource_lock"))
    file1.write("Log: Début opération\n")
    file2.write("Backup: Données importantes\n")
    print(" Toutes les ressources acquises")
    print(" Les ressources seront libérées automatiquement")

print("\n Extensions ")
print("\n Test transaction base de données ")
try:
    with DatabaseTransaction("ma_base") as db:
        db.execute("INSERT INTO users VALUES ('john')")
        db.execute("UPDATE stats SET count = count + 1")
except Exception as e:
    print(f"Transaction echouee: {e}")

print("\n Nettoyage final ")
for f in ["temp.txt", "temp2.txt", "data.txt", "log1.txt", "log2.txt"] + \
         ["doc_a.txt", "doc_b.txt", "doc_c.txt"] + ["test_temp.txt"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"Supprime: {f}")