"""A small web API around the GST assistant."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gst_assistant.core.llm import get_llm
from gst_assistant.core.logbook import LogBook
from gst_assistant.domains.gst.answer import Searcher, answer_question, load_records

app = FastAPI(title="GST Assistant")

searcher = Searcher(load_records())
llm = get_llm()
logbook = LogBook()


class AskRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    request_id: int
    value: int  # 1 for thumbs up, -1 for thumbs down


@app.get("/health")
def health():
    return {"status": "ok", "records": len(searcher.records)}


@app.post("/ask")
def ask(request: AskRequest):
    answer = answer_question(request.question, searcher, llm, logbook=logbook)
    return {
        "request_id": answer.request_id,
        "status": answer.status,
        "answer": answer.text,
        "retrieved_ids": answer.retrieved_ids,
        "cited_ids": answer.cited_ids,
        "total_ms": round(answer.total_ms),
    }


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    if request.value not in (1, -1):
        raise HTTPException(status_code=422, detail="value must be 1 or -1")
    if not logbook.set_feedback(request.request_id, request.value):
        raise HTTPException(status_code=404, detail="unknown request_id")
    return {"saved": True}
