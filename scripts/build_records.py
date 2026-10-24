import json

from gst_assistant.domains.gst.parse_rate_notification import clean_rows, parse_notification

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"
OUT_PATH = "data/processed/rates_09-2025.json"

NOTIFICATION = {
    "notification": "09/2025-Central Tax (Rate)",
    "tax_type": "CGST",
    "notification_date": "2025-09-17",
    "effective_from": "2025-09-22",
    "supersedes": "01/2017-Central Tax (Rate)",
    "source_file": "CT-Rate_09-2025_goods-rates_2025-09-17.pdf",
    "status": "active",
    "corrigenda_applied": False,
}

rows, trailers = parse_notification(PDF_PATH)
records = clean_rows(rows)

for record in records:
    record["id"] = "CT-09-2025:" + record["schedule"] + ":" + str(record["serial"])
    record.update(NOTIFICATION)

with open(OUT_PATH, "w", encoding="utf-8") as file:
    json.dump(records, file, ensure_ascii=False, indent=2)

print("saved", len(records), "records to", OUT_PATH)
