import pymupdf

PDF_PATH = "data/raw/CT-Rate_10-2025_goods-exemptions_2025-09-17.pdf"

doc = pymupdf.open(PDF_PATH)
lines = []
for page in doc:
    for line in page.get_text().splitlines():
        if line.strip():
            lines.append(line)

print("total lines:", len(lines))
for line in lines[22:62]:
    print(repr(line))
