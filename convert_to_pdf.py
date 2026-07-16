#!/usr/bin/env python3
import os
from xhtml2pdf import pisa

def link_callback(uri, rel):
    """
    Convert HTML images/links to absolute local system paths for xhtml2pdf.
    """
    project_dir = '/Users/edouard/Documents/Antigravity/immo'
    
    # Clean up the uri path
    if uri.startswith('.'):
        # e.g. ./screenshots/01_dashboard.png -> /Users/edouard/Documents/Antigravity/immo/screenshots/01_dashboard.png
        normalized = uri.lstrip('.')
        if normalized.startswith('/'):
            normalized = normalized[1:]
        path = os.path.join(project_dir, normalized)
    else:
        path = os.path.join(project_dir, uri)
        
    if not os.path.exists(path):
        print(f"Warning: file not found at {path}")
    return path

def generate_pdf():
    html_path = '/Users/edouard/Documents/Antigravity/immo/DOCUMENTATION_UTILISATEUR.html'
    pdf_path = '/Users/edouard/Documents/Antigravity/immo/DOCUMENTATION_UTILISATEUR.pdf'
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found. Please compile HTML first.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Open PDF file for writing binary
    with open(pdf_path, "w+b") as result_file:
        # Convert HTML to PDF
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=result_file,
            link_callback=link_callback
        )
        
    if pisa_status.err:
        print(f"Error occurred during PDF generation: {pisa_status.err}")
    else:
        print(f"Successfully generated PDF guide at {pdf_path}")

if __name__ == '__main__':
    generate_pdf()
