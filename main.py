import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from remedy_generator import generate_remedy_local
from speech_input import record_and_transcribe
from tamil_speech import speak_bilingual
from pdf_export import export_to_pdf
from history_logger import log_history
from disease_predictor import predict_disease

diagnosing = False
cancel_requested = False
diagnosis_thread = None

def update_status_loop(start_time):
    if diagnosing and not cancel_requested:
        elapsed = int(time.time() - start_time)
        status_label.config(text=f"🩺 Diagnosing… {elapsed}s elapsed")
        root.after(5000, lambda: update_status_loop(start_time))

def diagnose_thread(symptoms, mode):
    global diagnosing, cancel_requested
    start_time = time.time()
    update_status_loop(start_time)
    progress_bar.start()

    try:
        disease = predict_disease(symptoms)
        if cancel_requested:
            reset_ui("❌ Diagnosis cancelled.")
            return

        result = generate_remedy_local(disease, symptoms, mode=mode)
        if cancel_requested:
            reset_ui("❌ Diagnosis cancelled.")
            return

        display_result(result["text"])
        speak_bilingual(result["text"])
        log_history(disease, symptoms, result["text"])
        export_to_pdf(disease, symptoms, result["text"])
        status_label.config(text="✅ Diagnosis complete.")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="❌ Diagnosis failed.")

    progress_bar.stop()
    diagnosing = False
    cancel_requested = False

def diagnose_and_generate():
    global diagnosing, cancel_requested, diagnosis_thread
    symptoms = symptom_entry.get()
    mode = mode_var.get()
    if not symptoms.strip():
        messagebox.showerror("Error", "Please enter symptoms.")
        return

    diagnosing = True
    cancel_requested = False
    diagnosis_thread = threading.Thread(target=diagnose_thread, args=(symptoms, mode), daemon=True)
    diagnosis_thread.start()

def cancel_diagnosis():
    global cancel_requested, diagnosing, diagnosis_thread
    cancel_requested = True
    status_label.config(text="⏳ Cancelling…")
    progress_bar.stop()
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)

    # Wait for thread to finish
    def wait_for_thread():
        if diagnosis_thread and diagnosis_thread.is_alive():
            root.after(500, wait_for_thread)
        else:
            status_label.config(text="❌ Diagnosis fully cancelled.")
            diagnosing = False

    wait_for_thread()

def reset_ui(message=""):
    progress_bar.stop()
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)
    status_label.config(text=message)
    diagnosing = False
    cancel_requested = False

def display_result(text):
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, text)
    result_text.config(state=tk.DISABLED)

def record_speech():
    status_label.config(text="🎙️ Listening… Speak now")
    root.update_idletasks()

    transcript = record_and_transcribe()
    status_label.config(text="")

    if not transcript.strip():
        messagebox.showerror("Error", "Could not understand speech.")
        return

    symptom_entry.delete(0, tk.END)
    symptom_entry.insert(0, transcript)
    diagnose_and_generate()

# UI Setup
root = tk.Tk()
root.title("🩺 Doctor Bot")
root.geometry("850x800")
root.configure(bg="#E3F2FD")

# Header
header = tk.Label(root, text="🩺 Doctor Bot – AI Health Assistant", font=("Helvetica", 20, "bold"), bg="#2196F3", fg="white", pady=10)
header.pack(fill=tk.X)

# Input Frame
input_frame = tk.Frame(root, bg="#BBDEFB", padx=20, pady=20)
input_frame.pack(fill=tk.X, padx=20, pady=10)

ttk.Label(input_frame, text="Enter Symptoms:", font=("Helvetica", 14)).grid(row=0, column=0, sticky="w")
symptom_entry = ttk.Entry(input_frame, width=70, font=("Helvetica", 12))
symptom_entry.grid(row=1, column=0, pady=10)

# Mode Toggle
mode_var = tk.StringVar(value="basic")
mode_frame = tk.Frame(input_frame, bg="#BBDEFB")
mode_frame.grid(row=2, column=0, pady=5, sticky="w")
ttk.Label(mode_frame, text="Choose Output Mode:", font=("Helvetica", 12)).pack(side=tk.LEFT)
ttk.Radiobutton(mode_frame, text="Basic", variable=mode_var, value="basic").pack(side=tk.LEFT, padx=10)
ttk.Radiobutton(mode_frame, text="Detailed", variable=mode_var, value="detailed").pack(side=tk.LEFT)

# Buttons
button_frame = tk.Frame(input_frame, bg="#BBDEFB")
button_frame.grid(row=3, column=0, pady=10)

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=6)
ttk.Button(button_frame, text="🎙️ Speak Now", command=record_speech).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="🧠 Diagnose & Generate", command=diagnose_and_generate).grid(row=0, column=1, padx=5)
ttk.Button(button_frame, text="❌ Cancel Diagnosis", command=cancel_diagnosis).grid(row=0, column=2, padx=5)

# Status Label
status_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#E3F2FD", fg="#D32F2F")
status_label.pack(pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300)
progress_bar.pack(pady=5)

# Output Frame
output_frame = tk.LabelFrame(root, text="📝 Diagnosis & Remedy", font=("Helvetica", 14, "bold"), bg="#F1F8E9", padx=10, pady=10)
output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_text = tk.Text(output_frame, wrap=tk.WORD, font=("Helvetica", 12), bg="#FFFFFF", yscrollcommand=scrollbar.set)
result_text.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=result_text.yview)
result_text.config(state=tk.DISABLED)

root.mainloop()