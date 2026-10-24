import pymupdf

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"

doc = pymupdf.open(PDF_PATH)
print("Pages:", len(doc))

page = doc[1] # page numbers start at 0, so this is page 2
print(page.get_text())
