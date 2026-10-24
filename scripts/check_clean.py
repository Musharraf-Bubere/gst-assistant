from gst_assistant.domains.gst.parse_rate_notification import clean_rows, parse_notification

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"

rows, trailers = parse_notification(PDF_PATH)
records = clean_rows(rows)
print("records:", len(records))

print()
print("SAMPLES")
for record in records[:2] + records[516:518]:
    print(record)

flagged = [r for r in records if not r["hsn_text"] or not r["description"]]
print()
print("flagged (empty code or empty description):", len(flagged))

raw = {(r["schedule"], r["serial"]): r for r in rows}
for record in flagged:
    print(record["schedule"], record["serial"], raw[(record["schedule"], record["serial"])]["parts"][:4])
