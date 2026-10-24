import json
import re

from gst_assistant.domains.gst.parse_rate_notification import clean_rows, parse_notification

OUT_PATH = "data/processed/records.json"

DOCUMENTS = [
    {
        "pdf": "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf",
        "id_prefix": "CT-09-2025",
        "options": {},
        "treatment": "taxable",
        "meta": {
            "notification": "09/2025-Central Tax (Rate)",
            "supersedes": "01/2017-Central Tax (Rate)",
        },
    },
    {
        "pdf": "data/raw/CT-Rate_10-2025_goods-exemptions_2025-09-17.pdf",
        "id_prefix": "CT-10-2025",
        "options": {"table_start": re.compile(r"^\(3\)\s*$")},
        "treatment": "exempt",
        "meta": {
            "notification": "10/2025-Central Tax (Rate)",
            "supersedes": "02/2017-Central Tax (Rate)",
        },
    },
]

COMMON = {
    "tax_type": "CGST",
    "notification_date": "2025-09-17",
    "effective_from": "2025-09-22",
    "status": "active",
    "corrigenda_applied": False,
}

records = []
for doc in DOCUMENTS:
    rows, trailers = parse_notification(doc["pdf"], **doc["options"])
    for record in clean_rows(rows):
        record["id"] = doc["id_prefix"] + ":" + record["schedule"] + ":" + str(record["serial"])
        record["treatment"] = doc["treatment"]
        if doc["treatment"] == "exempt":
            record["cgst_rate"] = None
            record["gst_rate"] = None
        record["source_file"] = doc["pdf"].split("/")[-1]
        record.update(doc["meta"])
        record.update(COMMON)
        records.append(record)
    print(doc["id_prefix"], "->", len(rows), "records")

with open(OUT_PATH, "w", encoding="utf-8") as file:
    json.dump(records, file, ensure_ascii=False, indent=2)

print("saved", len(records), "records to", OUT_PATH)
