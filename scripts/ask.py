import sys

from gst_assistant.core.llm import get_llm
from gst_assistant.core.logbook import LogBook
from gst_assistant.domains.gst.answer import Searcher, answer_question, load_records

searcher = Searcher(load_records())
llm = get_llm()
logbook = LogBook()

question = " ".join(sys.argv[1:]) or "What is the GST on fresh ginger?"
answer = answer_question(question, searcher, llm, logbook=logbook)

print("QUESTION:", question)
print("STATUS:  ", answer.status)
print()
print(answer.text)
print()
print("RETRIEVED:", ", ".join(answer.retrieved_ids))
print("CITED:    ", ", ".join(answer.cited_ids))
print("TOKENS:    in", answer.tokens_in, "| out", answer.tokens_out)
print("TIME:      total", round(answer.total_ms), "ms | search", round(answer.search_ms), "ms | Gemini", round(answer.llm_ms), "ms")
print("SEARCHED:  ", answer.search_query)
