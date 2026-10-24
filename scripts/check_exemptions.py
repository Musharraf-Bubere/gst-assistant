import re

from gst_assistant.domains.gst.parse_rate_notification import parse_notification

PDF_PATH = "data/raw/CT-Rate_10-2025_goods-exemptions_2025-09-17.pdf"

rows, trailers = parse_notification(PDF_PATH, table_start=re.compile(r"^\(3\)\s*$"))

print("rows:", len(rows), "| expected 172 |", "OK" if len(rows) == 172 else "MISMATCH")
print("first row:", rows[0]["parts"])
print("last row:", " ".join(rows[-1]["parts"])[:120])
print("trailers:")
for t in trailers:
    print("  ", t["kind"], "|", len(t["parts"]), "lines |", t["parts"][0][:60])
