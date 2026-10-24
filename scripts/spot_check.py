import json

with open("data/processed/rates_09-2025.json", encoding="utf-8") as file:
    records = json.load(file)

print("SCHEDULE VII (all rows)")
for record in records:
    if record["schedule"] == "VII":
        print(record["serial"], "|", record["hsn_text"], "|", record["description"][:70])

print()
print("LONGEST CODES")
longest = sorted(records, key=lambda r: len(r["hsn_text"]), reverse=True)
for record in longest[:5]:
    print(record["schedule"], record["serial"], len(record["hsn_text"]), "|", record["hsn_text"][:90])
