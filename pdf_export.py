from fpdf import FPDF

def export_to_pdf(disease, symptoms, remedy_text):
    pdf = FPDF()
    pdf.add_page()

    # Register Tamil-compatible Unicode font
    pdf.add_font("Latha", "", "Latha.ttf", uni=True)
    pdf.set_font("Latha", size=12)

    pdf.multi_cell(0, 10, f"Disease: {disease}\nSymptoms: {symptoms}\n\nRemedy:\n{remedy_text}")

    filename = f"{disease}_diagnosis.pdf"
    pdf.output(filename)