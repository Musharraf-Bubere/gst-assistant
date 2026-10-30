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

**Q: PyMuPDF or LangChain loaders?**
A: They aren't alternatives. PyMuPDF reads the PDF, and LangChain's loader can wrap it. The real choice was between my own structure-aware splitting and a generic character splitter. The rate is in the schedule heading, far from the row, so a generic splitter would lose it. I wrote my own row parser and verified it with row counts.

**Q: Why isn't the HSN code enough to find the rate?**
A: The same heading can have different rates depending on the description. In notification 9/2025, heading 2401 appears at 5% for tobacco leaves (Schedule I) and at 28% for unmanufactured tobacco (Schedule VII). Matching on the code alone gives the wrong rate, so retrieval returns candidates and the answer step compares descriptions and conditions.

**Q: What are the limits of keyword search?**
A: It matches words, not meaning. For "ginger" it returned the row "Ginger other than fresh ginger" at 5%. Fresh ginger is actually exempt under notification 10/2025. That is why I am adding the exemption notification, semantic search, guardrails and trap questions in my evaluation set.

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

**Q: What does your app say for "GST on ginger"?**
A: There isn't one answer. Fresh ginger is exempt (notification 10/2025, entry 60) and other ginger is 5% (9/2025, entry 42). Retrieval returns both rows, and the answer step explains the difference and cites each. Keyword search alone also matched "Grapes, fresh" because of the word "fresh", which is why I plan semantic search and a re-check on the final answer.

**Q: Have you used LangChain?**
A: Yes, after building the pipeline by hand. I rebuilt retrieval and answer generation with LangChain and compared both on the same evaluation set. (Fill in the numbers once measured.) Building it manually first meant I knew what each LangChain component was replacing.

**Q: RAG or fine-tuning?**
A: RAG for knowledge, because tax rules change and every answer needs a source. Fine-tuning changes behavior, not facts that stay current, and it cannot cite. I would fine-tune only a small classifier or the embedding model, and only after the evaluation shows a gap.

**Q: How do you monitor it?**
A: Every request is logged with the retrieved cards, guards, latency, tokens, cost and feedback. A dashboard shows volume, latency, cost, not-found and thumbs-down rates, plus a document-freshness check, because stale documents are the biggest risk for a tax assistant.

**Q: How would you switch from Gemini to another model?**
A: All model calls go through one small interface, generate(system, prompt), which returns the text and token counts. Switching means writing one new class for the provider and changing LLM_PROVIDER in .env. Retrieval, API and evaluation don't change.

**Q: Tell me about a failure of your system.**
A: A user asked about the GST on a "spaceship". The notification says "spacecraft", so keyword search found nothing and the app answered "not found", when the real answer is exempt (10/2025, entry 159). It didn't invent an answer, but it missed one. I added it to my evaluation set as a failing case and I'm fixing it with semantic search, then measuring the hit rate before and after.

**Q: Why a local embedding model and not an API?**
A: For version 1 I wanted reproducible evaluation and zero cost. A local model file doesn't change, so my retrieval scores stay comparable over time. I plan to compare it with a hosted embedding model on the same test set and choose by the numbers. Queries and documents must use the same model, so switching means re-embedding everything.

**Q: Why hybrid search?**
A: On my evaluation set the two methods failed on different questions. Keyword search missed synonyms (spaceship vs spacecraft), while vector search missed an exact HSN code. I combined them with Reciprocal Rank Fusion, which uses rank positions because BM25 and cosine scores are on different scales. (Fill in the hybrid score once measured.)

**Q: Did hybrid search improve things?**
A: Yes, from 15 (keyword) and 16 (vector) to 17 of 19 on my test set. But it made one question worse than vector alone: "tax on electricity". With RRF two weak votes for a wrong card can beat one strong vote for the right card. I'm measuring weights, more retrieved cards and re-ranking rather than guessing. The test set is small, so a one-question change is 5%, and I'm growing it.

**Q: How do you know your results are not overfitted?**
A: I keep a held-out question set that I never tune on and run only at milestones. After I changed stop words to fix one practice question, hybrid went from 17 to 18 of 19, but that set was no longer fair, because I had studied for it. The held-out score tells me how much of the gain is real.

**Q: How do you stop the model from inventing a rate?**
A: Gemini must cite card ids. After it answers, a checker verifies that each cited id was among the retrieved cards and that every percentage in the answer appears on the cited cards. If not, the user sees "could not verify" instead of Gemini's text. It can't catch citing a real but wrong card, so I also evaluate answers against the expected card.

**Q: How do you evaluate the whole system, not only search?**
A: An answer passes only if the status is right, the cited card is the expected card, and the stated value (exempt or the rate) matches. Questions that should be refused must come back as refused or not found. I keep a practice set, a held-out set and a guard set, because once a set is tuned on, a perfect score on it no longer finds problems.

**Q: How would you know in production that something is going wrong?**
A: Every request is logged with its status, the cards retrieved and cited, tokens, and search, model and total time. A report counts refusals, "not found" and "could not verify" answers and shows latency and token use. A rise in "unverified" or "not found" would be my first signal, and the log lets me replay the exact question and cards.
