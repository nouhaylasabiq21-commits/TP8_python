import csv
from datetime import datetime
from contextlib import ExitStack
import os

class BatchProcessor:
    def __init__(self, input_csv, log_file="journal.log"):
        self.input_csv = input_csv
        self.log_file = log_file
        self.csv_file = None
        self.log_file_obj = None
    
    def __enter__(self):
        self.csv_file = open(self.input_csv, 'r', newline='', encoding='utf-8')
        self.log_file_obj = open(self.log_file, 'a', encoding='utf-8')
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file_obj.write(f"[{timestamp}] Début du traitement batch\n")
        print(f"Debut du traitement batch a {timestamp}")
        
        return self
    
    def process_line(self, line_data):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operation = line_data.get('operation', '')
        value = line_data.get('value', '')
        
        log_msg = f"[{timestamp}] Traitement: {operation} avec valeur: {value}\n"
        self.log_file_obj.write(log_msg)
        
        print(f"Traitement: {operation} - {value}")
        
        if operation == "erreur":
            raise ValueError("Erreur simulee dans le traitement")
        
        return f"{operation}_traite"
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if exc_type:
            error_msg = f"[{timestamp}] ERREUR: {exc_type.__name__} - {exc_val}\n"
            self.log_file_obj.write(error_msg)
            print(f"Erreur pendant le traitement: {exc_val}")
        else:
            success_msg = f"[{timestamp}] Traitement terminé avec succès\n"
            self.log_file_obj.write(success_msg)
            print("Traitement termine avec succes")
        
        if self.csv_file:
            self.csv_file.close()
        if self.log_file_obj:
            self.log_file_obj.close()
        
        return True

print(" Test 1: Traitement normal ")
with open("operations.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['operation', 'value'])
    writer.writeheader()
    writer.writerow({'operation': 'addition', 'value': '5'})
    writer.writerow({'operation': 'multiplication', 'value': '3'})
    writer.writerow({'operation': 'division', 'value': '2'})

try:
    with BatchProcessor("operations.csv") as processor:
        reader = csv.DictReader(processor.csv_file)
        for row in reader:
            result = processor.process_line(row)
except Exception as e:
    print(f"Exception: {e}")

print("\nTest 2: Avec erreur dans le traitement ")
with open("operations_erreur.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['operation', 'value'])
    writer.writeheader()
    writer.writerow({'operation': 'addition', 'value': '10'})
    writer.writerow({'operation': 'erreur', 'value': '0'})
    writer.writerow({'operation': 'multiplication', 'value': '4'})

try:
    with BatchProcessor("operations_erreur.csv", "journal_erreur.log") as processor:
        reader = csv.DictReader(processor.csv_file)
        for row in reader:
            result = processor.process_line(row)
except Exception as e:
    print(f"Exception attrapee: {e}")

print("\n Test 3: Avec ExitStack pour gestion multiple ")
class EnhancedBatchProcessor:
    def __init__(self, input_csv, log_file="journal.log", output_file="resultats.csv"):
        self.input_csv = input_csv
        self.log_file = log_file
        self.output_file = output_file
    
    def __enter__(self):
        self.stack = ExitStack()
        self.input_file = self.stack.enter_context(open(self.input_csv, 'r', encoding='utf-8'))
        self.output_file_obj = self.stack.enter_context(open(self.output_file, 'w', newline='', encoding='utf-8'))
        self.log_file_obj = self.stack.enter_context(open(self.log_file, 'a', encoding='utf-8'))
        
        self.writer = csv.writer(self.output_file_obj)
        self.writer.writerow(['operation', 'valeur', 'resultat', 'timestamp'])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file_obj.write(f"[{timestamp}] Début traitement avancé\n")
        
        return self
    
    def process(self):
        reader = csv.DictReader(self.input_file)
        for row in reader:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            operation = row.get('operation', '')
            value = row.get('value', '')
            
            try:
                if operation == "division" and float(value) == 0:
                    raise ZeroDivisionError("Division par zéro")
                
                result = f"{operation}_{value}"
                self.writer.writerow([operation, value, result, timestamp])
                
                log_msg = f"[{timestamp}] Succès: {operation}({value}) -> {result}\n"
                self.log_file_obj.write(log_msg)
                
            except Exception as e:
                error_log = f"[{timestamp}] Échec: {operation}({value}) - {str(e)}\n"
                self.log_file_obj.write(error_log)
                self.writer.writerow([operation, value, "ÉCHEC", timestamp])
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if exc_type:
            self.log_file_obj.write(f"[{timestamp}] ERREUR GLOBALE: {exc_type.__name__} - {exc_val}\n")
        else:
            self.log_file_obj.write(f"[{timestamp}] Traitement terminé\n")
        
        self.stack.close()
        return True

with open("operations_complexe.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['operation', 'value'])
    writer.writeheader()
    writer.writerow({'operation': 'addition', 'value': '10'})
    writer.writerow({'operation': 'division', 'value': '0'})
    writer.writerow({'operation': 'multiplication', 'value': '7'})

with EnhancedBatchProcessor("operations_complexe.csv", "journal_complet.log") as processor:
    processor.process()

print("\n Affichage des journaux ")
for log_file in ["journal.log", "journal_erreur.log", "journal_complet.log"]:
    if os.path.exists(log_file):
        print(f"\n--- {log_file} ---")
        with open(log_file, 'r', encoding='utf-8') as f:
            print(f.read())

print("\n  Nettoyage ")
files_to_remove = [
    "operations.csv", "operations_erreur.csv", "operations_complexe.csv",
    "journal.log", "journal_erreur.log", "journal_complet.log",
    "resultats.csv"
]
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Supprime: {file}")