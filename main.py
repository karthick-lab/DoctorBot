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
from medical_advice import generate_medical_advice

diagnosing = False
cancel_requested = False
advice_generating = False
diagnosis_thread = None
advice_thread = None

import os, sys, json

# If a config path is passed as an argument, use it
if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    # fallback: look in the script/exe folder
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_file = os.path.join(exe_dir, "config.json")

with open(config_file, "r") as f:
    CONFIG = json.load(f)

def update_status_loop(start_time, mode):
    if mode == "diagnosis" and diagnosing and not cancel_requested:
        elapsed = int(time.time() - start_time)
        status_label.config(text=f"🩺 Diagnosing… {elapsed}s elapsed")
        root.after(1000, lambda: update_status_loop(start_time, mode))
    elif mode == "advice" and advice_generating:
        elapsed = int(time.time() - start_time)
        status_label.config(text=f"💬 Advice generation in progress… {elapsed}s elapsed")
        root.after(1000, lambda: update_status_loop(start_time, mode))

def diagnose_thread(symptoms, mode):
    global diagnosing, cancel_requested
    start_time = time.time()
    update_status_loop(start_time, "diagnosis")
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
    global cancel_requested, diagnosing
    cancel_requested = True
    status_label.config(text="⏳ Cancelling diagnosis…")
    progress_bar.stop()
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)

def cancel_advice():
    global advice_generating
    advice_generating = False
    status_label.config(text="⏳ Cancelling advice…")
    progress_bar.stop()
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)

def reset_ui(message=""):
    progress_bar.stop()
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)
    status_label.config(text=message)
    diagnosing = False
    cancel_requested = False
    advice_generating = False

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

def record_medical_question():
    status_label.config(text="🎙️ Listening for medical question…")
    root.update_idletasks()
    transcript = record_and_transcribe()
    status_label.config(text="")
    if not transcript.strip():
        messagebox.showerror("Error", "Could not understand speech.")
        return
    question_entry.delete(0, tk.END)
    question_entry.insert(0, transcript)
    ask_medical_doubt()

def ask_medical_doubt():
    global advice_generating, advice_thread
    question = question_entry.get()
    if not question.strip():
        messagebox.showerror("Error", "Please enter a medical question.")
        return

    advice_generating = True
    start_time = time.time()
    update_status_loop(start_time, "advice")
    progress_bar.start()

    def run_advice():
        global advice_generating
        try:
            result = generate_medical_advice(question)
            if advice_generating:
                display_result(result["text"])
                speak_bilingual(result["text"])
                status_label.config(text="✅ Advice generation complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            status_label.config(text="❌ Advice generation failed.")
        progress_bar.stop()
        advice_generating = False

    advice_thread = threading.Thread(target=run_advice, daemon=True)
    advice_thread.start()

# UI Setup
root = tk.Tk()
root.title("🩺 Doctor Bot")
root.geometry("850x1000")
root.configure(bg="#E3F2FD")

header = tk.Label(root, text="🩺 Doctor Bot – AI Health Assistant", font=("Helvetica", 20, "bold"), bg="#2196F3", fg="white", pady=10)
header.pack(fill=tk.X)

input_frame = tk.Frame(root, bg="#BBDEFB", padx=20, pady=20)
input_frame.pack(fill=tk.X, padx=20, pady=10)

ttk.Label(input_frame, text="Enter Symptoms:", font=("Helvetica", 14)).grid(row=0, column=0, sticky="w")
symptom_entry = ttk.Entry(input_frame, width=70, font=("Helvetica", 12))
symptom_entry.grid(row=1, column=0, pady=10)

mode_var = tk.StringVar(value="basic")
mode_frame = tk.Frame(input_frame, bg="#BBDEFB")
mode_frame.grid(row=2, column=0, pady=5, sticky="w")
ttk.Label(mode_frame, text="Choose Output Mode:", font=("Helvetica", 12)).pack(side=tk.LEFT)
ttk.Radiobutton(mode_frame, text="Basic", variable=mode_var, value="basic").pack(side=tk.LEFT, padx=10)
ttk.Radiobutton(mode_frame, text="Detailed", variable=mode_var, value="detailed").pack(side=tk.LEFT)

button_frame = tk.Frame(input_frame, bg="#BBDEFB")
button_frame.grid(row=3, column=0, pady=10)
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=6)
ttk.Button(button_frame, text="🎙️ Speak Now", command=record_speech).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="🧠 Diagnose & Generate", command=diagnose_and_generate).grid(row=0, column=1, padx=5)
ttk.Button(button_frame, text="❌ Cancel Diagnosis", command=cancel_diagnosis).grid(row=0, column=2, padx=5)

doubt_frame = tk.LabelFrame(root, text="❓ Medical Doubts & Advice", font=("Helvetica", 14, "bold"), bg="#FFF3E0", padx=10, pady=10)
doubt_frame.pack(fill=tk.X, padx=20, pady=10)

ttk.Label(doubt_frame, text="Ask your medical question:", font=("Helvetica", 12)).pack(anchor="w")
question_entry = ttk.Entry(doubt_frame, width=80, font=("Helvetica", 12))
question_entry.pack(pady=5)





doubt_button_frame = tk.Frame(doubt_frame, bg="#FFF3E0")
doubt_button_frame.pack(fill=tk.X, pady=5)

# Configure 3 columns with equal weight for balanced layout
doubt_button_frame.columnconfigure(0, weight=1)
doubt_button_frame.columnconfigure(1, weight=1)
doubt_button_frame.columnconfigure(2, weight=1)

# Left button
ttk.Button(doubt_button_frame, text="🎙️ Speak Medical Question", command=record_medical_question)\
    .grid(row=0, column=0, padx=5, sticky="e")

# Center button
ttk.Button(doubt_button_frame, text="💬 Ask Medical Doubt", command=ask_medical_doubt)\
    .grid(row=0, column=1, padx=5)

# Right button
ttk.Button(doubt_button_frame, text="❌ Cancel Medical Advice", command=cancel_advice)\
    .grid(row=0, column=2, padx=5, sticky="w")



status_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#E3F2FD", fg="#D32F2F")
status_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300)
progress_bar.pack(pady=5)

output_frame = tk.LabelFrame(root, text="📝 Diagnosis & Advice Output", font=("Helvetica", 14, "bold"), bg="#F1F8E9", padx=10, pady=10)
output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_text = tk.Text(output_frame, wrap=tk.WORD, font=("Helvetica", 12), bg="#FFFFFF", yscrollcommand=scrollbar.set)
result_text.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=result_text.yview)
result_text.config(state=tk.DISABLED)

# Start the application
root.mainloop()