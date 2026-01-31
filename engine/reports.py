from fpdf import FPDF
from datetime import datetime

class Auditor:
    def __init__(self):
        pass

    def generate_report(self, history_df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Header
        pdf.cell(200, 10, txt="VELOMA COGNITIVE AUDIT", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        
        # Data Summary
        avg_risk = history_df['Market Risk'].mean()
        avg_quality = history_df['Decision Quality'].mean()
        
        pdf.cell(200, 10, txt=f"Average Market Stress: {avg_risk:.2f}%", ln=True)
        pdf.cell(200, 10, txt=f"Average Decision Quality: {avg_quality:.2f}%", ln=True)
        
        if avg_quality > 80:
            conclusion = "Verdict: High Agency Maintained. Decisions were optimal."
        else:
            conclusion = "Verdict: Cognitive Degradation Detected. Caution advised."
            
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 12)
        pdf.multi_cell(0, 10, txt=conclusion)
        
        return pdf.output(dest='S').encode('latin-1') # Return as bytes for Streamlit