"""Split a CBIC goods rate notification (Central Tax Rate) into rows.

Output:
  rows     - one dict per entry in a rate schedule
  trailers - annexure lists and closing explanations, kept separate from rows
"""
import re

import pymupdf

HEADING = re.compile(r"^Schedule\s*([IVX]+)\s*[\u2013\-]\s*([\d.]+)\s*%")
SERIAL = re.compile(r"^(\d+)\.(?:\s+(.*))?$")
LIST_START = re.compile(r"^List\s*(\d+)\s*\[\s*See\s+S\.\s*No\.\s*(\d+)")
EXPLANATION_START = re.compile(
    r"^Explanation\.\s*[\u2014\u2013\-]\s*For the purposes? of this notification"
)


def read_lines(pdf_path):
    """All non-empty lines of the PDF, in order, pages joined together."""
    doc = pymupdf.open(pdf_path)
    lines = []
    for page in doc:
        for line in page.get_text().splitlines():
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def split_rows(lines):
    """Walk the lines once and group them into rows and trailers."""
    rows = []
    trailers = []
    schedule = None
    cgst_rate = None
    current = None
    trailer = None
    expected = 1
    for line in lines:
        heading = HEADING.match(line)
        if heading:
            schedule = heading.group(1)
            cgst_rate = float(heading.group(2))
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
            current = {
                "schedule": schedule,
                "cgst_rate": cgst_rate,
                "serial": expected,
                "parts": [],
            }
            if serial.group(2):
                current["parts"].append(serial.group(2))
            rows.append(current)
            expected += 1
        elif current is not None:
            current["parts"].append(line)
    return rows, trailers


def parse_notification(pdf_path):
    return split_rows(read_lines(pdf_path))


CODE_WORDS = {"or", "and", "to", "any", "other", "chapter", "heading", "except"}


def is_code_line(line):
    """True if the line only contains numbers and code words like 'or'."""
    line = re.sub(r"\[[^\]]*\]?", "", line)
    tokens = re.findall(r"\([^)]*\)|[A-Za-z]+|\d+|[,.\-]", line)
    if not tokens:
        return False
    for token in tokens:
        if token.isdigit() or token.lower() in CODE_WORDS:
            continue
        if token in ",.-" or token.startswith("("):
            continue
        return False
    return True


def join_lines(parts):
    """Glue wrapped lines into one text, repairing words split with a hyphen."""
    text = ""
    for part in parts:
        if text.endswith("-"):
            text += part
        else:
            text += (" " if text else "") + part
    return re.sub(r"\s+", " ", text).strip()


def clean_row(row):
    """Turn raw lines of one row into a record with a code and a description."""
    parts = row["parts"]
    split_at = 0
    in_bracket = False
    while split_at < len(parts):
        line = parts[split_at]
        if in_bracket:
            in_bracket = "]" not in line
        elif is_code_line(line):
            in_bracket = line.count("[") > line.count("]")
        else:
            break
        split_at += 1
    hsn_text = join_lines(parts[:split_at])
    hsn_text = re.sub(r"\b(or|and|to)(?=\d)", r"\1 ", hsn_text)
    return {
        "schedule": row["schedule"],
        "serial": row["serial"],
        "cgst_rate": row["cgst_rate"],
        "gst_rate": round(row["cgst_rate"] * 2, 3),
        "hsn_text": hsn_text,
        "description": join_lines(parts[split_at:]),
    }


def clean_rows(rows):
    return [clean_row(row) for row in rows]
