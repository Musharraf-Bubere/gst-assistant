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

## D39. Hard-set failures sorted by root cause, then fixed (Oct 2026)

- Hard set: answers 11 of 16, retrieval (hybrid) 10 of 14. Five failures, two root causes: (1) vocabulary gap between everyday words and notification words (atta, moong dal, supari, branded, loose), (2) cards showed only the total rate, so a CGST question could not be answered.
- No failure was a wrong answer. Gemini said "not found", so the safe layers worked, but recall was low.
- Fixes: a glossary that adds notification words to the search query (the user's question is unchanged for Gemini), and a CGST, SGST and IGST split on taxable cards, with the CGST number accepted by the inspector.
- Fairness: the glossary was written after seeing these failures. A new set (eval/hard_own.json) with words outside the glossary is the real test.
- Observation to check: the same short generic cards (CT-10-2025:-:131, I:507, I:437, I:514, VI:1) keep appearing in vector results for unrelated questions.

## D40. Rate limits and graceful failure (Oct 2026)

- Problem: the evaluation hit Gemini 429 RESOURCE_EXHAUSTED. Errors were counted as failures and the app would have crashed.
- Chose: retry twice with a 20 second wait on 429 only (other errors raise at once), a new status "error" with a polite message, a 4 second pause in the exam, and errors reported separately from failures.
- Observed: refused and not-found questions never call Gemini, so the guards keep working when the model is unavailable.
- Production note: a free quota will limit real users. Options to evaluate later: answer caching for repeated questions, a per-user request limit, a paid plan.

## D41. Generalization test for the glossary (Oct 2026)

- After the glossary and CGST fix: practice 22 of 22, held-out 10 of 10, guards 6 of 6, hard 16 of 16 (retrieval 14 of 14). No errors.
- Because the glossary was written after seeing the hard-set failures, those scores are not a fair test of it. eval/hard_own.json uses 8 everyday words outside the glossary (paan, chai patti, anda, murmura, patang, incense sticks, sabudana, jhadu).
- Rule: record the first score before changing anything. Fixing failures by extending the glossary is allowed, but then the set is used up and a new one is needed.
- Idea to compare later: let the LLM rewrite the query instead of a hand-made glossary (more flexible, but costs a call and adds latency).

## D42. The fair test showed weak generalization (Oct 2026)

- On eval/hard_own.json (8 everyday words not in the glossary) retrieval was 1 of 8 and answers 1 of 8. The earlier 100 percent scores were on sets we had tuned on.
- 6 of 7 failures were an honest "not found". One (jhadu) cited the card for the raw material and said exempt, right by luck and wrong in reasoning. The inspector cannot catch a real but wrong card; the expected-id check did.
- Causes: the English-only embedding model does not understand these words (0 of 8 on vector search), keyword search needs identical words, the glossary only covers the words I wrote. The same generic cards (CT-10-2025:-:131, I:437, I:514, VI:1, VI:2) appear when the model does not understand the question.
- Plan: compare A (extended glossary), B (LLM query rewriting) and both on a frozen set, eval/fresh.json, run once per approach.

## D43. Query rewriting by the LLM, compared on a frozen set (Oct 2026)

- Chose: four modes (none, glossary, rewrite, both). Attack rules run before the rewrite, the rewrite output is only used as search text, and a failed rewrite falls back to the original question.
- Fair test: eval/fresh.json (10 everyday words in neither the glossary nor hard_own), run once per mode. Examples in the rewrite prompt use words that appear in no test set.
- Measure: answers passed, tokens (cost of the extra call), and what the search was fed on failures.
- Decision rule: adopt rewrite only if it clearly beats the glossary on the fresh set, and keep the glossary if the two together are best.

## D44. Query rewriting adopted, pending regression (Oct 2026)

- Frozen fresh set (10 unseen everyday words): glossary 0 of 10, rewrite 10 of 10, both 10 of 10. hard_own with rewrite: 6 of 8 (was 1 of 8).
- Caveats: small set, written by me, mostly produce; the set is now used and a new one is needed for future claims.
- Bugs and noise seen: Gemini copied the "Question:" label into the search text; it also invented a non-word ("porita"). Labels are stripped; noise is tolerated because search plus answer checks follow.
- Open problems (development items, not for the fresh set): (1) RRF let cards found by both lists beat the exact "agarbatti" card; (2) the answering step does not know that murmura means puffed rice because it sees only the original question.
- Next: regression runs in "both" mode, then make "both" the default if the old scores hold.

## D45. Default search mode is "both"; cost measured (Oct 2026)

- Regression in both mode: practice 22/22, hard 16/16, guards 6/6, held-out 10/10, same as before.
- Cost of the extra rewrite call: about 15 to 20 percent more input tokens (roughly 130 to 170 per question). Time per question not measured yet.
- Why "both": the glossary is free and exact and still works when the rewrite call fails or is rate limited.

## D46. Web API with FastAPI (Oct 2026)

- Windows: /health, /ask (status, answer, cards, time, request_id) and /feedback (thumbs up or down).
- The searcher, model and logbook are built once at start-up. The logbook connection is shared across threads with a lock, tested with 4 threads and 200 writes.
- Not yet: authentication, request limits, CORS settings. Local use only until they are added.

## D47. Latency measured and first fixes (Oct 2026)

- Typical question: about 1.7 to 2.1 s. Rewrite 0.8 to 1.0 s (40 to 50 percent), Gemini answer 0.8 to 1.3 s, own search 17 to 42 ms. One earlier request took 9.5 s because a Gemini call was slow, so latency varies and the slowest requests must be watched, not just the average.
- A refused off-topic question still pays one rewrite call (about 160 tokens in, under 20 out), because the rewrite comes before the similarity check.
- Fixes: label cleaning (take text after the last "Rewrite:"), an in-memory cache of rewrites (search words only, never answers, so it cannot serve stale tax answers), no duplicated "exempt" in card text.
- Still to decide with data: skipping the rewrite when plain search is confident, a faster model for the rewrite, a request timeout and a shorter retry in the API.

## D48. The rewrite step is not deterministic (Oct 2026)

- "GST on nimbu" gave two different rewrites in two runs with temperature 0 ("lemons fresh lemons" vs "lemons limes"). The first run missed the fresh lemon card, because the doubled word "fresh" pulled in other fresh-fruit cards.
- The cache lives in one program's memory, so it does not help between separate command runs. It helps inside a running server.
- A single exam run can pass by luck. Added scripts/stability.py: repeat the rewrite and search 5 times per question with the cache cleared, and count how often the right card is in the top 5.
- Options to test afterwards: two separate searches (original and rewrite) fused by the vote, top 8 cards to the LLM, a persistent rewrite cache.

## D49. Stability measured: 44 of 50 (Oct 2026)

- On eval/fresh.json with 5 repeats per question, the right card was in the top 5 in 44 of 50 runs (88 percent). Unstable: nimbu 2/5 and nariyal 2/5. Both sit among near-identical "fresh fruit" cards.
- The earlier 10 of 10 was optimistic. Quote about 88 percent for retrieval on this kind of question, not 100.
- Rewrites varied for 6 of 10 questions but only the crowded ones failed, so variation alone is not the problem.
- Hypothesis: extra words like "fresh" or "fruit" in the rewrite make many similar cards compete and push the right one past rank 5.
- eval/fresh2.json is frozen (7 of 10 in the crowded produce group). Experiments in this order: top 8 cards, then a rewrite prompt that adds product names only, then run fresh2 once.

## D50. Top 8 cards fixes crowding in retrieval (Oct 2026)

- Stability at top 8 instead of top 5: fresh 44/50 to 50/50 (nimbu and nariyal now 5/5), hard_own 35/40 (incense and murmura now 5/5).
- Cost: roughly 300 to 450 more input tokens per question. Adoption waits for an answer-level check of accuracy and tokens.
- Jhadu stays 0/5 with a single search, so it is a fixed retrieval problem, not variability.

## D51. Stemming in keyword search (Oct 2026)

- Hypothesis: "broom" (from the rewrite) does not match "brooms" (the card), so the raw-material card with "broom sticks" wins. Fix: Snowball stemmer on both cards and queries, applied after stop-word removal.
- Check: retrieval_summary before and after on five sets (no LLM calls); any older set that gets worse blocks adoption until the changed question is understood.

## D52. Stemming fixed the jhadu failure (Oct 2026)

- Before: jhadu 0/5 with one fixed search. After stemming: hard_own stability 40 of 40 at top 8.
- Free retrieval summary before and after on five sets: unchanged for practice, held-out, hard and fresh. Keyword alone lost one question on hard_own (2 to 1, cause not yet identified); hybrid unchanged.
- hard_own is a development set; the generalization check is the frozen fresh2, run once at the end.
- Next: answer-level check of top 8 (accuracy and tokens), then fresh2 once, then stop tuning retrieval and build the UI and deployment.

## D53. Keep 8 cards (Oct 2026)

- Answers: hard_own 6/8 to 8/8, hard 15/15 scored, practice 22/22. Input tokens per question rose about 30 to 45 percent (roughly 300 to 400 tokens); output unchanged.
- hard_own is a development set; the frozen fresh2 gives the unbiased number.

## D54. Transient provider errors (Oct 2026)

- A 503 UNAVAILABLE (service briefly down) appeared during evaluation. It was reported as an error, not a failure. Retry now covers 429 and 503 with a wait; other errors fail at once.
