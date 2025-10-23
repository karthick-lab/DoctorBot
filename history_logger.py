import datetime

def log_history(disease, symptoms, remedy_text):
    with open("diagnosis_history.txt", "a", encoding="utf-8") as file:
        file.write("=== Diagnosis Entry ===\n")
        file.write(f"Date: {datetime.datetime.now()}\n")
        file.write(f"Disease: {disease}\n")
        file.write(f"Symptoms: {symptoms}\n")
        file.write(f"Remedy:\n{remedy_text}\n\n")