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
