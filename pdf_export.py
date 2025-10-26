import os
import re
from datetime import datetime
from fpdf import FPDF

def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def export_to_pdf(disease, symptoms, remedy_text):
    # Folder path
    folder_path = r"C:\Users\admin\Desktop\Reports\Medical natural remedies report"
    os.makedirs(folder_path, exist_ok=True)

    # Timestamp for versioning
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Clean text to avoid encoding errors
    clean_text = remove_emojis(f"Disease: {disease}\nSymptoms: {symptoms}\n\nRemedy:\n{remedy_text}")

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.multi_cell(0, 10, clean_text)

    # Save with timestamped filename
    filename = os.path.join(folder_path, f"{disease}_diagnosis_{timestamp}.pdf")
    pdf.output(filename)