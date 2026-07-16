#!/usr/bin/env python3
import markdown
import os

def generate_html():
    md_path = '/Users/edouard/Documents/Antigravity/immo/DOCUMENTATION_UTILISATEUR.md'
    html_path = '/Users/edouard/Documents/Antigravity/immo/DOCUMENTATION_UTILISATEUR.html'
    
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc', 'nl2br'])

    # Static CSS styling (no variables for xhtml2pdf compatibility)
    css_styles = """
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #333333;
        background-color: #ffffff;
        line-height: 1.6;
        margin: 0;
        padding: 0;
    }
    
    .container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #0f2a4a;
        font-weight: bold;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    
    h1 {
        font-size: 28pt;
        border-bottom: 3px solid #c5a059;
        padding-bottom: 10px;
        margin-top: 0;
        text-transform: uppercase;
    }
    
    h2 {
        font-size: 18pt;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 8px;
        margin-top: 1.8em;
    }
    
    h3 {
        font-size: 14pt;
        margin-top: 1.5em;
    }
    
    p {
        margin-bottom: 1.2em;
    }
    
    a {
        color: #c5a059;
        text-decoration: none;
        font-weight: bold;
    }
    
    ul, ol {
        margin-bottom: 1.5em;
        padding-left: 20px;
    }
    
    li {
        margin-bottom: 0.5em;
    }
    
    /* Tables styling */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 10pt;
        border: 1px solid #e9ecef;
    }
    
    th {
        background-color: #0f2a4a;
        color: #ffffff;
        text-align: left;
        font-weight: bold;
        padding: 10px;
    }
    
    td {
        padding: 10px;
        border-bottom: 1px solid #e9ecef;
    }
    
    tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    
    /* Code and pre blocks */
    code {
        font-family: monospace;
        background-color: #f8f9fa;
        color: #d63384;
        padding: 2px 4px;
        font-size: 9pt;
    }
    
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 12px;
        margin-bottom: 1.5em;
    }
    
    pre code {
        background-color: transparent;
        color: #333333;
        padding: 0;
        font-size: 9pt;
    }
    
    /* Blockquotes (Alerts) */
    blockquote {
        background-color: #eef3f7;
        border-left: 5px solid #0f2a4a;
        margin: 20px 0;
        padding: 12px 15px;
    }
    
    blockquote p {
        margin: 0;
        font-weight: bold;
    }
    
    /* Image styling */
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 25px auto;
        border: 1px solid #e9ecef;
    }
    """

    # Wrapper HTML (no external stylesheet calls for xhtml2pdf compatibility)
    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Guide Utilisateur — MILA Gestion Immobilière</title>
    <style>
        {css_styles}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""

    # Post-processing to add page break before key sections
    sections_to_break = [
        "<h2>1. Tableau de bord</h2>",
        "<h2>2. Patrimoine</h2>",
        "<h2>3. Baux (Locations)</h2>",
        "<h2>4. Configuration</h2>",
        "<h2>5. Conseils pratiques</h2>",
        "<h2>6. Questions fréquentes</h2>",
        "<h2>7. Nouveautés de la Version 4.1 (Juillet 2026)</h2>",
        "<h2>8. Scénarios de Test Recommandés (Version 4.1)</h2>",
        "<h2>Comptes d'accès pour les tests</h2>"
    ]
    
    for section in sections_to_break:
        full_html = full_html.replace(section, f'<div style="page-break-before: always;"></div>{section}')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"Successfully generated clean HTML guide at {html_path}")

if __name__ == '__main__':
    generate_html()
