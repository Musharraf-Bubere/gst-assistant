import re
import pymupdf

PDF_PATH = "data/raw/CT-Rate_09-2025_goods-rates_2025-09-17.pdf"
HEADING = re.compile(r"^Schedule\s*([IVX]+)\s*[\u2013\-]\s*([\d.]+)\s*%")
SERIAL = re.compile(r"^(\d+)\.(?:\s+(.*))?$")
LIST_START = re.compile(r"^List\s*(\d+)\s*\[\s*See\s+S\.\s*No\.\s*(\d+)")
EXPLANATION_START = re.compile(r"^Explanation\.\s*[\u2014\u2013\-]\s*For the purposes? of this notification")
EXPECTED = {"I": 516, "II": 640, "III": 13, "IV": 15, "V": 3, "VI": 2, "VII": 6}

doc = pymupdf.open(PDF_PATH)

lines = []
for page in doc:
    for line in page.get_text().splitlines():
        line = line.strip()
        if line:
            lines.append(line)

rows = []
trailers = []
schedule = None
current = None
trailer = None
expected = 1
for line in lines:
    heading = HEADING.match(line)
    if heading:
        schedule = heading.group(1)
        current = None
        trailer = None
        expected = 1
        continue
    if schedule is None:
        continue
    list_start = LIST_START.match(line)
    if list_start or EXPLANATION_START.match(line):
        kind = "annexure" if list_start else "explanation"
        trailer = {"schedule": schedule, "kind": kind, "parts": [line]}
        trailers.append(trailer)
        current = None
        continue
    if trailer is not None:
        trailer["parts"].append(line)
        continue
    serial = SERIAL.match(line)
    if serial and int(serial.group(1)) == expected:
        current = {"schedule": schedule, "serial": expected, "parts": []}
        if serial.group(2):
            current["parts"].append(serial.group(2))
        rows.append(current)
        expected += 1
    elif current is not None:
        current["parts"].append(line)

print("ROWS")
for name, want in EXPECTED.items():
    sched_rows = [r for r in rows if r["schedule"] == name]
    status = "OK" if len(sched_rows) == want else "MISMATCH, expected " + str(want)
    print(name, "|", len(sched_rows), "rows |", status)
    print("   last row:", " ".join(sched_rows[-1]["parts"])[:100])

print()
print("ANNEXURES AND EXPLANATIONS")
for t in trailers:
    print(t["schedule"], "|", t["kind"], "|", len(t["parts"]), "lines |", t["parts"][0][:60])
