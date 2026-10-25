import sys

from gst_assistant.core.llm import get_llm
from gst_assistant.core.search import KeywordIndex
from gst_assistant.domains.gst.answer import answer_question, card_text, load_records

records = load_records()
index = KeywordIndex(records, card_text)
llm = get_llm()

question = " ".join(sys.argv[1:]) or "What is the GST on fresh ginger?"
answer, retrieved_ids = answer_question(question, index, llm)

print("QUESTION:", question)
print()
print(answer)
print()
print("RETRIEVED:", ", ".join(retrieved_ids))
