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
- Decision: (fill in after testing, with the evidence)

## D10. Documents stored in the repository (Oct 2026)
- Chose: commit the public PDFs to GitHub.
- Why: small public documents, and anyone can run the project after cloning.
- Revisit: if the document set grows too large.
