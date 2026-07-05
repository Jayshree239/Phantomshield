import sys
from pathlib import Path
pdf_path = Path('Phishing_website_detection_project_report (1).pdf')
out_dir = Path('analysis')
out_dir.mkdir(exist_ok=True)
out_file = out_dir / 'Phishing_website_detection_project_report_1.txt'
try:
    from PyPDF2 import PdfReader
except Exception as e:
    print('MISSING_PYPDF2')
    sys.exit(2)
try:
    reader = PdfReader(str(pdf_path))
    text = []
    for i, page in enumerate(reader.pages):
        t = page.extract_text() or ''
        text.append(f"\n\n--- PAGE {i+1} ---\n\n")
        text.append(t)
    all_text = '\n'.join(text)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    print('OK', len(reader.pages))
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
