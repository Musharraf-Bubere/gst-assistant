import re
import pymupdf

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"
HEADING = re.compile(r"^Schedule\s*([IVX]+)\s*[\u2013\-]\s*([\d.]+)\s*%")

doc = pymupdf.open(PDF_PATH)

lines = []
for page in doc:
    for line in page.get_text().splitlines():
        if line.strip():
            lines.append(line)

for index, line in enumerate(lines):
    match = HEADING.match(line.strip())
    if match and match.group(1) == "II":
        for offset in range(25):
            print(repr(lines[index + offset]))
        break
