from gst_assistant.domains.gst.parse_rate_notification import parse_notification

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"
EXPECTED = {"I": 516, "II": 640, "III": 13, "IV": 15, "V": 3, "VI": 2, "VII": 6}

rows, trailers = parse_notification(PDF_PATH)

for name, want in EXPECTED.items():
    got = len([r for r in rows if r["schedule"] == name])
    status = "OK" if got == want else "MISMATCH, expected " + str(want)
    print(name, "|", got, "rows |", status)

print("annexures and explanations:", len(trailers))


for row in rows[:3]:
    print(row)
