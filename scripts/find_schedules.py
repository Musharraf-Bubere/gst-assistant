import re
import pymupdf

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"
HEADING = re.compile(r"^Schedule\s*([IVX]+)\s*[\u2013\-]\s*([\d.]+)\s*%")

doc = pymupdf.open(PDF_PATH)

for page_number, page in enumerate(doc, start=1):
    for line in page.get_text().splitlines():
        match = HEADING.match(line.strip())
        if match:
            schedule, cgst_rate = match.groups()
            print(page_number, schedule, cgst_rate, float(cgst_rate) * 2)
