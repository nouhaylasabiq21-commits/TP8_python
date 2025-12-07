from datetime import datetime
from contextlib import ExitStack

class ConnectionManager:
    def __init__(self, service_name):
        self.service_name = service_name
    
    def __enter__(self):
        print(f"[{datetime.now()}] Connexion a {self.service_name} etablie.")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f"[{datetime.now()}] Deconnexion de {self.service_name}.")
        if exc_type:
            print(f"Erreur detectee : {exc_type.__name__} — {exc_value}")
        return False

print(" Partie 1: ConnectionManager")
with ConnectionManager("Service A") as conn:
    print(f"Utilisation du service: {conn.service_name}")
    print("Traitement en cours...")

print("\n Partie 2: Composition avec ExitStack ")
with ExitStack() as stack:
    log = stack.enter_context(open("log.txt", "a"))
    conn = stack.enter_context(ConnectionManager("Serveur X"))
    log.write(f"[{datetime.now()}] Tache effectuee sur {conn.service_name}\n")
    print("Opérations normales terminees")

print("\n Partie 3: Simulation d'erreur ")
try:
    with ExitStack() as stack:
        log = stack.enter_context(open("log.txt", "a"))
        conn = stack.enter_context(ConnectionManager("Base Y"))
        log.write(f"[{datetime.now()}] Debut du traitement sur {conn.service_name}\n")
        raise RuntimeError("Erreur de traitement")
        log.write(f"[{datetime.now()}] Fin du traitement\n")
except RuntimeError as e:
    print(f"Exception attrapee a l'exterieur: {e}")

print("\n Verification du fichier log ")
try:
    with open("log.txt", "r") as f:
        print("Contenu du fichier log:")
        print(f.read())
except FileNotFoundError:
    print("Fichier log.txt non trouve")

print("\n Nettoyage ")
import os
if os.path.exists("log.txt"):
    os.remove("log.txt")
    print("Fichier log.txt supprime")