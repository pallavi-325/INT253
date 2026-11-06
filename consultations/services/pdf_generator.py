import io
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def render_consultation_pdf(consultation):
    """
    Renders styled HTML template into high-fidelity PDF bytes using xhtml2pdf.
    """
    context = {
        'consultation': consultation,
        'appointment': consultation.appointment,
        'child': consultation.appointment.child,
        'doctor': consultation.doctor,
        'doctor_profile': getattr(consultation.doctor, 'doctor_profile', None),
        'treatment_plan': getattr(consultation, 'treatment_plan', None),
    }
    
    html_content = render_to_string('consultations/pdf_report_template.html', context)
    pdf_buffer = io.BytesIO()
    
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        raise RuntimeError("PDF generation encountered errors during document compilation.")
    
    return pdf_buffer.getvalue()

