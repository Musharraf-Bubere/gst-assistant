from gst_assistant.domains.gst.guards import check_output

cards = [
    {"id": "CT-10-2025:-:60", "treatment": "exempt", "gst_rate": None,
     "hsn_text": "0910 11 10", "description": "Fresh ginger, other than in processed form"},
    {"id": "CT-09-2025:I:42", "treatment": "taxable", "gst_rate": 5.0,
     "hsn_text": "0910 [other than 0910 11 10, 0910 30 10]", "description": "Ginger other than fresh ginger"},
    {"id": "CT-09-2025:VII:1", "treatment": "taxable", "gst_rate": 28.0,
     "hsn_text": "2106 90 20", "description": "Pan masala"},
]

tests = [
    ("good: exempt, cited", "Fresh ginger is exempt [CT-10-2025:-:60].", False),
    ("good: two cards", "Fresh ginger is exempt [CT-10-2025:-:60]. Other ginger is taxed at 5% [CT-09-2025:I:42].", False),
    ("good: rate written as 28.0%", "Pan masala is taxed at 28.0% [CT-09-2025:VII:1].", False),
    ("good: honest not found", "I could not find this in the notifications I have.", False),
    ("bad: no citation", "Fresh ginger is exempt.", True),
    ("bad: invented card id", "Fresh ginger is exempt [CT-10-2025:-:999].", True),
    ("bad: wrong rate", "Pan masala is taxed at 18% [CT-09-2025:VII:1].", True),
    ("bad: exempt called 0%", "Fresh ginger has 0% GST [CT-10-2025:-:60].", True),
]

for name, answer, should_fail in tests:
    problem = check_output(answer, cards)
    correct = (problem is not None) == should_fail
    print("PASS" if correct else "FAIL", "|", name, "|", problem or "no problem")
