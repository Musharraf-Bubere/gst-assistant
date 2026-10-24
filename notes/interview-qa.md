# Interview Q&A (GST Assistant)

Rewrite each answer in your own words before an interview. Say it out loud.

## Project
**Q: Why did you build this?**
A: I studied for CMA for 3 years, and tax and GST rules kept changing through amendments, so keeping up was hard. I built an assistant that answers GST questions with the latest rule, source notification and date.

**Q: Why RAG and not fine-tuning?**
A: Rules change often. With RAG I update the documents, not the model. It also lets me show the source for every answer.

## Design decisions
**Q: How does it handle rule changes?**
A: Every chunk has metadata: notification number, effective date, status (active or superseded). Search filters to active rules and prefers the newest. Example: GST 2.0 took effect on 22 Sept 2025 and replaced the old rate structure.

**Q: Why hybrid search?**
A: Tax questions contain exact tokens like HSN codes and notification numbers. Embeddings alone are weak at exact matches, so I combine vector search with keyword search.

**Q: Why didn't you use LangChain?**
A: I built version 1 in plain Python so I understand every step: loading, chunking, retrieval, prompting. I plan to add LangGraph in version 2 for a routing step.

**Q: How is the LLM swappable?**
A: All LLM calls go through one small interface. Switching providers means writing one new class and changing one setting.

**Q: Why PyMuPDF (or Docling)?**
A: (Fill in after testing both parsers on the real notifications.)

**Q: Couldn't you just use a database of rates instead of RAG?**
A: For exact lookups a table is more reliable, and I may add one in version 2. But the notifications also contain conditions, exceptions and cross-references, for example a rate that is 2.5% only if input credit is not taken. That is text, so retrieval plus an LLM with citations fits it. The best design combines both.

## Domain gotchas I found
**Q: What surprised you in the source documents?**
A: The CGST notification lists half rates (2.5%, 9%, 20%), while users ask for the full GST rate (5%, 18%, 40%). The IGST notification has the full rate, so I use it as the main source and CGST to cross-check.

**Q: Which documents are complete and which are amendments?**
A: 9/2025 and 10/2025 are complete replacements of the 2017 goods notifications. 15/2025 and 16/2025 only amend the older service notifications 11/2017 and 12/2017, so services need base plus amendments. Corrigenda are also part of the legal text.

## Quality and safety
**Q: How do you reduce wrong answers?**
A: Guardrails: refuse out-of-scope questions, say "I couldn't find this" when nothing relevant is retrieved, require a citation, and check that any rate in the answer appears in the retrieved text.

**Q: How do you evaluate it?**
A: A test set of 30-50 questions with correct answers and sources, including questions that should get "I don't know". I measure retrieval hit rate, answer correctness and citation correctness after every change.

## Bugs and fixes
**Q: Tell me about something that broke.**
A: Pushing to GitHub failed with a 403 error. I had two GitHub accounts logged in and the wrong one was active. Checking `gh auth status` showed it, and `gh auth switch` fixed it.

**Q: Any bug that taught you something?**
A: My script couldn't find a PDF because I wrote the Windows path with backslashes in a Python string, and `\r` was read as a carriage return. Using forward slashes (or pathlib) fixed it.

**Q: Tell me about a parsing problem you found.**
A: My row splitter found 516 rows in Schedule I but 0 in Schedule II. I printed the raw lines with repr() and saw Schedule II puts the serial number and HSN code on the same line, while Schedule I puts them on separate lines. I changed the pattern and added a rule that a new row must have the next expected serial number.

**Q: How do you know your parsing is correct?**
A: I compare row counts per schedule against totals verified with a second tool and a manual check of the last serial numbers. This caught a bug in my own pattern, where entry-level explanations were treated as the end of the table and 75 rows in one schedule disappeared. The check printed MISMATCH, so I found it immediately.
