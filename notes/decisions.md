# Decision log (GST Assistant)

Format for every entry: what I chose, what else I considered, why, the trade-off, and when I would revisit it.
Add a new entry whenever I choose between options or change a decision.

## D1. Problem: GST rates assistant (Oct 2026)
- Chose: a Q&A assistant over Indian GST documents.
- Considered: annual report assistant; my own idea.
- Why: I studied tax and GST for CMA and felt the pain of constant amendments. I know the domain, so I can judge whether answers are right.
- Trade-off: tax answers must be accurate, so I need guardrails and a disclaimer.
- Revisit: if I can't build a reliable test set.

## D2. Scope: goods only for version 1 (Oct 2026, tentative)
- Chose: start with goods rates and exemptions. Services in version 2.
- Considered: goods and services together.
- Why: 9/2025 and 10/2025 are complete replacement notifications. 15/2025 and 16/2025 only amend the older 11/2017 and 12/2017, so services need "base notification plus all amendments", which is harder.
- Trade-off: version 1 covers fewer questions.
- Revisit: once the goods pipeline and evaluation work.

## D3. Sources: official CBIC notifications only (Oct 2026)
- Chose: official notifications. I store the source link and download date for each document.
- Considered: blogs and summary sites.
- Why: sites disagree on how to describe the slabs. A tax tool must cite official text.
- Trade-off: the CBIC site was down once, so I used another government department site and checked the notification number and date inside each PDF.
- Revisit: if I need a document that is only available elsewhere. Then I mark it as unofficial in the metadata.

## D4. Tooling: uv instead of pip (Oct 2026)
- Chose: uv for Python, virtual environment and dependencies.
- Considered: pip with venv.
- Why: faster, and it records exact versions in uv.lock so anyone can reproduce my setup.
- Trade-off: less familiar to some teams.

## D5. Plain Python first, frameworks later (Oct 2026)
- Chose: build version 1 without LangChain. Add LangGraph and LangSmith in version 2.
- Considered: LangChain from the start.
- Why: I must be able to explain every step. Frameworks hide loading, chunking, retrieval and prompting behind function calls.
- Trade-off: more code to write myself.
- Revisit: when I need branching logic, such as routing goods vs services questions.

## D6. LLM behind one interface, Gemini first (Oct 2026)
- Chose: a small LLM interface. Gemini is the first implementation. Keys live in .env, which is in .gitignore.
- Considered: calling Gemini directly everywhere.
- Why: switching provider means one new class and one setting, not edits across many files.
- Trade-off: a little extra structure at the start.

## D7. Search: hybrid (vector + keyword) (Oct 2026, planned)
- Chose: combine embeddings with keyword search.
- Why: tax questions contain exact tokens like HSN codes and notification numbers.
- Revisit: after evaluation. If keyword search adds nothing, simplify.

## D8. Rate source: IGST notification as primary (Oct 2026, planned)
- Chose: use the Integrated Tax (Rate) notification for "GST rate" answers. Use CGST to cross-check.
- Why: CGST lists half rates (2.5%, 9%, 20%). Users ask for full rates (5%, 18%, 40%).
- Status: IGST notification not downloaded yet.

## D9. PDF parser: PyMuPDF vs Docling (Oct 2026, OPEN)
- Plan: test PyMuPDF on real table pages. If rows break, test Docling on the same pages and compare.
- Decision: PyMuPDF. On notification 9/2025 it keeps rows in order, and with my splitter all 7 schedules match the verified row counts (1,195 rows). I did not need Docling. Revisit if other notifications (services, IGST) come out scrambled.

## D10. Documents stored in the repository (Oct 2026)
- Chose: commit the public PDFs to GitHub.
- Why: small public documents, and anyone can run the project after cloning.
- Revisit: if the document set grows too large.

## D11. Keep core pipeline separate from GST-specific parts (Oct 2026)
- Chose: reusable code in core/, GST parsers, metadata, prompts, guardrails and test questions in domains/gst/.
- Considered: one flat codebase, or building a fully generic tool first.
- Why: lets me swap in other documents later without rewriting retrieval, API or evaluation.
- Trade-off: slightly more folders now. I will not generalise further until the GST version is working and measured.

## D12. Roadmap beyond version 1 (Oct 2026)
- v1: single-question RAG over goods, with guardrails, evaluation, deployment.
- v1.5: chatbot with conversation memory and clarifying questions.
- v2: services (base notification + amendments), LangGraph routing, LangSmith tracing.
- v3: agent with tools (rate lookup, calculator, "what changed between dates").
- v4: scale, with a watcher that ingests new notifications and flags changes.
- Rule: add agent behaviour only where a fixed workflow is not enough.

## D13. MCP: not in version 1 (Oct 2026)
- Chose: plain Python functions for retrieval and calculation in v1.
- Considered: building an MCP server from the start.
- Why: only my own app calls these functions, so MCP would add a server to build and run without solving a problem.
- Revisit: in v3, expose search_rates, calculate_gst and compare-dates as an MCP server so other AI apps can use them.

## D14. Schedule headings detected with a regex (Oct 2026)
- Chose: a line is a schedule heading only if it has "Schedule", a Roman numeral, a dash and a percentage. This ignores in-text references like "Schedule I of this notification".
- Why: a plain "starts with Schedule" check found 11 lines, only 7 were real headings.
- Note: the heading rate is the CGST rate, so the GST rate is 2x (stored as a separate field, with the source noted).

## D15. Validate the parser with counts, not by eye (Oct 2026)
- Chose: after splitting rows, check that serial numbers in each schedule run 1..n with no gaps, and read the last row of each schedule.
- Why: a parser can look right on one page and silently lose or merge rows elsewhere.

## D16. Row counts verified two ways (Oct 2026)
- Chose: split rows by schedule, then cross-checked counts with a second tool and a manual check of the last serial numbers.
- Result: 1,195 rows in 9/2025 (516, 640, 13, 15, 3, 2, 6), matching in both tools.
- Known remaining issue: annexure lists and the closing Explanation get attached to the last row of a schedule. They must be separated.

## D17. Annexures and closing explanations are separate chunks (Oct 2026)
- Chose: when a line starts "List n [See S. No. n" or "Explanation.—", stop the current row and store the text separately.
- Why: annexure lists belong to a specific entry (for example List 1 belongs to S. No. 478), and the closing explanation applies to the whole notification, so neither is part of the last rate row.
- Safety net: the script checks row counts per schedule against known totals (516, 640, 13, 15, 3, 2, 6) and prints MISMATCH if they change.
- Bug found by my own check: my first pattern treated every "Explanation.-" as the end of the rows. Many entries have their own explanation ("For the purposes of this entry"), so rows were swallowed and the counts dropped (I: 441 instead of 516). Fixed by matching only "For the purposes of this notification".
- Lesson: the expected-count check caught it within seconds. Without it, the data would have looked fine and been silently wrong.

## D18. Own row parser instead of a generic loader and splitter (Oct 2026)
- Chose: PyMuPDF for text, my own code for rows, schedules and annexures.
- Considered: LangChain document loader plus a character-based text splitter.
- Why: the rate lives in the schedule heading, rows continue across pages, and annexures belong to specific entries. A generic splitter cuts by length and loses all three.
- Trade-off: more code to write and test, covered by the row-count checks.
- Revisit: use a generic splitter only for very long explanation text, after rate and code are attached.
- Correction (Oct 2026): LangChain is not limited to generic splitters. Header-based splitting after a Markdown conversion, or LLM extraction, could also work. I chose my own parser because it is deterministic, free, verifiable with row counts, and explainable.
- Experiment to run later: Markdown conversion + MarkdownHeaderTextSplitter on the same PDF, compared on row counts and whether the rate and [other than ...] notes survive.

## D19. Keep "[other than ...]" notes in the code field as written (Oct 2026)
- Chose: the bracket note stays inside hsn_text, exactly as in the notification.
- Why: it limits the entry. 0910 [other than 0910 11 10, 0910 30 10] does not cover fresh ginger or turmeric. Dropping it would give wrong answers.
- Revisit: extract exclusions into their own field so search can filter on them.

## D20. Exempt is stored as a treatment, not as a 0% rate (Oct 2026)
- Chose: every record has treatment = taxable or exempt. For exempt records the rate fields are empty.
- Why: exempt, nil-rated and zero-rated differ in input tax credit. Showing "0%" for an exemption would be wrong and would mislead.
- Revisit: when the nil-rated entries in 9/2025 and zero-rated supplies (exports) are added, they will need their own treatment values.

## D21. Build the pipeline manually first, then a LangChain twin (Oct 2026)
- Chose: version 1 by hand; after evaluation and deployment, rebuild the retrieval and answer pipeline with LangChain and compare on the same evaluation set.
- Why: I understand each step because I wrote it. The comparison gives evidence, not opinion, about what the framework saves and hides.
- Plan (revised): build the twin from the loader onward, compare stage by stage (parse/chunk, retrieval, answer), then end to end. Freeze the evaluation set first. Same documents, embedding model, LLM settings, prompt and top-k on both sides. Pin versions. Record effort as well as accuracy.
- Rules: finish and deploy v1 first, start from the same records.json, keep the twin in experiments/langchain/, time-box to about a week.

## D22. Guardrails and evaluation built by hand first (Oct 2026)
- Chose: rule-based input checks, not-found guard, strict prompt, citation check, number check and disclaimer. Evaluation with 30-50 questions: lookups, traps, exclusions, not-found, off-topic and injection attempts. Exact-match scoring first.
- Why: I can explain every check. Tax answers need deterministic checks.
- Later: try Ragas/DeepEval and a guardrails library on the same questions and compare with my own.

## D23. Observability and monitoring (Oct 2026)
- Chose: log every request to SQLite (question, retrieved ids and scores, guards fired, answer, citations, latency, tokens, cost, errors, feedback). A Streamlit page shows volume, latency, cost, not-found rate, refusals, thumbs-down and errors. Plus a document-freshness check.
- Later: try a tracing tool (LangSmith, Langfuse or Phoenix) after reading its current documentation.

## D24. No fine-tuning in version 1 (Oct 2026)
- Chose: RAG for knowledge. Rules change often and answers need citations, which fine-tuning cannot give.
- Revisit: if evaluation shows a behavior or classification gap, or if retrieval needs better embeddings. Candidates are a small question classifier and an embedding model. Compare on the same evaluation set.

## D25. Baseline: keyword search only (Oct 2026)
- Retrieval hit rate on the first 7 lookup questions: 6 of 7 (BM25 keyword search, top 5).
- Miss: "spaceship" never matches "spacecraft" (10/2025 entry 159), because keyword search compares exact words.
- Next: add semantic search with local embeddings and compare on the same questions.

## D26. Local embeddings first (fastembed, bge-small), compare with Gemini later (Oct 2026)
- Chose: BAAI/bge-small-en-v1.5 through fastembed for version 1 retrieval.
- Why: free, no rate limits, reproducible (the model file does not change under me), no network dependency for search, light to deploy, easy to explain.
- Trade-offs: possibly lower quality than a hosted model, short input window, English only.
- Rule: cards and queries must use the same embedding model, so switching means rebuilding the vectors.
- Plan: put embeddings behind a small interface, add a Gemini embedder, and compare hit rate, speed and cost on the same evaluation set.

## D27. First comparison: keyword 6/7, vector 7/7 (Oct 2026)
- On the first 7 questions, vector search fixed "spaceship" vs "spacecraft" and lost nothing.
- Limit: 7 easy questions cannot separate the methods. Extended to 20 lookup questions with everyday wording, an exact code, and a typo.
- Rule: expected ids come from the PDF, not from the app's own search, to avoid testing the search against itself.
- Note: fastembed downloaded the quantized (smaller) ONNX version of bge-small-en-v1.5.

## D28. Hybrid search with Reciprocal Rank Fusion (Oct 2026)
- Evidence before: on 19 lookup questions keyword scored 15 and vector 16, and they missed different questions. Keyword failed on different wording (spaceship/spacecraft, electricity/electrical energy, prasad/prasadam). Vector failed on an exact code and on one card with many items (roti and chapati).
- Chose: combine both rankings with RRF (1 / (60 + rank)), taking the top 20 from each.
- Why: rank positions are comparable, but BM25 and similarity scores are not.
- Known gap: typos (q22). Fix later with fuzzy matching or query rewriting.
- Result on 19 lookup questions: keyword 15, vector 16, hybrid 17. Hybrid fixed 5 questions one method had missed, but missed q19 (electricity), which vector had found.
- My prediction was 18 of 19. It was wrong. RRF rewards cards that appear on both lists, so two weak votes can outrank one strong vote.
- Next: look at the position of the right card for the misses, then try weights, more cards to the LLM, a re-ranker or query rewriting, and compare on the same set.

## D29. Stop words in keyword search (Oct 2026)
- Problem: for "tax on electricity" the right card was 2nd for vector and not in the keyword top 50, and hybrid pushed it to 7th. Common words ("tax", "on") made the keyword list full of junk that also scored slightly in the vector list.
- Chose: remove ordinary stop words and GST words that appear in every query ("gst", "tax", "rate") before keyword search, in both the cards and the question. Kept "other" and "than", which change meaning.
- Checked: re-run the same 19 questions and compare per question, not only the total.

## D30. Practice set and held-out set (Oct 2026)
- After tuning on q19 (stop words), the 19-question set was no longer a fair test: hybrid 18 of 19.
- Chose: keep eval/questions.json for tuning and eval/heldout.json (10 taxable-item questions, ids verified in the PDF) for milestone checks only.
- Rule: do not tune on held-out failures. If one fails, write new practice questions about that area and fix those.
- Result after stop words on the practice set: keyword 15, vector 16, hybrid 18 of 19 (only the typo "gingr" missed).

## D31. Held-out result and a hypothesis (Oct 2026)
- Held-out (10 simple lookups): keyword 10, vector 7, hybrid 10. Hybrid held up; no sign of overfitting from the stop-words change.
- Limit: these questions use words that appear in the notification, so they are easy for keyword search. They do not test synonyms, typos or Hindi words. A harder held-out set is needed.
- Vector misses (vermicelli, motorcycles up to 350cc, refrigerators) were all long multi-item cards. Hypothesis: split long descriptions into one card per item. Test with new practice questions, not by tuning on these three.

## D32. Typo tolerance in keyword search (Oct 2026)
- Chose: replace a query word that appears in no card with the closest card word (difflib, similarity at least 0.8). Skip numbers and words under 4 letters.
- Why: "gingr" was missed by all three methods (hybrid position 19).
- Risk: a real but missing word may be changed into a wrong word. Checked by re-running both evaluation sets.
- Limit: only the keyword side is corrected. The vector side still sees the typo.

## D33. Retrieval results after typo tolerance (Oct 2026)
- Practice set: keyword 17, vector 16, hybrid 19 of 19. Held-out: keyword 10, vector 7, hybrid 10 of 10.
- Caveat: the practice set was tuned on twice, so 19 of 19 is optimistic. Held-out is easy (words appear in the notification). Next: harder questions and a harder held-out set.
- Next: calibrate a "not found" threshold on the similarity score of the best card, using eval/guards.json, instead of guessing a number.

## D34. Layered guards, because one similarity threshold cannot work (Oct 2026)
- Measured top similarity: real questions 0.614 to 0.789, refuse or not-found questions 0.487 to 0.679. They overlap between about 0.61 and 0.68. The attack "ignore your rules ... exempt" scored 0.679 because its words are close to real cards.
- Chose: (1) regex rules for attacks, (2) a low threshold of 0.55 only for clearly unrelated text, (3) the LLM with a strict prompt decides not-found for the rest, then citation and number checks on its answer.
- Caveat: 0.55 rests on about 26 real questions and belongs to this embedding model. Re-measure if either changes.
- Check: no real question may be blocked (wrongly blocked = 0).

## D35. Output inspector: citation and rate checks (Oct 2026)
- Chose: after the LLM answers, check (1) at least one card id is cited, (2) every cited id was actually retrieved, (3) every percentage in the answer appears in the cited cards (their GST rate or numbers in their text). A failed answer is replaced with "I found related notifications but could not verify an answer".
- Tested offline with 8 fake answers (4 good, 4 bad), no LLM calls.
- Limits: it cannot detect a real but wrong card. Numbers in card text count as allowed, so a coincidence is possible. The answer evaluation (expected ids) must catch wrong-card answers.

## D36. First full-pipeline evaluation (Oct 2026)
- Practice set: 22 of 22 (doorman, hybrid search, Gemini, inspector). About 730 tokens in and 45 out per question.
- Caveat: the practice set was tuned on and is now saturated, so it can no longer find problems.
- Fair tests: eval/heldout.json (10 simple lookups) and eval/guards.json (not-found, off-topic, attack). Next: a harder held-out set (conditions, exclusions, everyday Indian words, two-card answers, questions the notifications cannot answer).

## D37. Request logging and the first monitoring report (Oct 2026)
- Chose: log every request to SQLite (question, status, answer, retrieved and cited ids, tokens, search, Gemini and total time, feedback column for thumbs up and down). Evaluation runs write to a separate file so test runs never mix with real usage. Log files are in .gitignore because they hold user questions.
- Report: counts by status, average and slowest response time, average Gemini time, token totals. Cost = tokens x the provider's current price, looked up when needed.
- Next: the thumbs up and down button in the UI, and a freshness check for the documents.

## D38. Hard evaluation set (Oct 2026)
- 16 questions: packaged vs loose (rice, atta, honey, jaggery), everyday Indian words (moong dal, supari, kumkum, rakhi, papad), an exclusion (plastic bangles), two services questions the data cannot answer yet, a wrong-premise question and a CGST question.
- Ids were taken from the PDFs with a separate reading tool, not from the app, and I spot-checked them in the PDFs.
- k16 (CGST rate) is expected to fail because the cards show only the total rate. k13 and k14 should become answerable when services are parsed.
- Rule: sort failures into kinds before fixing anything, and re-run all sets after each change.
