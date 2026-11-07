"""A simple web page for the GST assistant."""
import logging

import streamlit as st

from gst_assistant.core.llm import get_llm
from gst_assistant.core.logbook import LogBook
from gst_assistant.core.ratelimit import RateLimiter
from gst_assistant.domains.gst.answer import Searcher, answer_question, load_records

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)

st.set_page_config(page_title="GST Assistant", page_icon="🧾")


@st.cache_resource
def load_app():
    records = load_records()
    by_id = {record["id"]: record for record in records}
    llm = get_llm(retries=1, wait_seconds=3)
    return Searcher(records), llm, LogBook(), by_id, RateLimiter(120, 3600)


searcher, llm, logbook, by_id, global_limiter = load_app()

st.title("GST Assistant")
st.caption(
    "Answers from the official CBIC notifications 9/2025 and 10/2025 (goods). "
    "This is information from the notifications, not tax advice."
)
st.info("Please do not type client names or other private details. Questions are logged to improve the tool.")

question = st.text_input(
    "Ask about the GST on a product",
    placeholder="for example: GST on paan leaves",
)

if st.button("Ask") and question.strip():
    session_limiter = st.session_state.setdefault("limiter", RateLimiter(10, 600))
    if not session_limiter.allow() or not global_limiter.allow():
        st.session_state.pop("answer", None)
        st.warning("Too many questions right now. Please wait a few minutes and try again.")
    else:
        with st.spinner("Looking through the notifications..."):
            st.session_state["answer"] = answer_question(question, searcher, llm, logbook=logbook)
        st.session_state["feedback_given"] = False

answer = st.session_state.get("answer")
if answer:
    if answer.status == "answered":
        st.success(answer.text)
    elif answer.status == "not_found":
        st.warning(
            answer.text
            + "\n\nI currently cover goods only (notifications 9/2025 and 10/2025). "
            "Services are not included yet."
        )
    elif answer.status == "refused":
        st.warning(answer.text)
    else:
        st.error(answer.text)

    if answer.cited_ids:
        with st.expander("Sources used"):
            for card_id in dict.fromkeys(answer.cited_ids):
                record = by_id.get(card_id)
                if record:
                    st.markdown(
                        "**" + card_id + "**: notification " + record["notification"]
                        + ", effective " + record["effective_from"]
                        + "\n\n" + record["hsn_text"] + ": " + record["description"][:300]
                    )

    if answer.request_id and answer.status != "error":
        if st.session_state.get("feedback_given"):
            st.caption("Thank you for the feedback.")
        else:
            st.caption("Was this answer helpful?")
            thumbs_up, thumbs_down, _ = st.columns([1, 1, 4])
            if thumbs_up.button("👍"):
                logbook.set_feedback(answer.request_id, 1)
                st.session_state["feedback_given"] = True
                st.rerun()
            if thumbs_down.button("👎"):
                logbook.set_feedback(answer.request_id, -1)
                st.session_state["feedback_given"] = True
                st.rerun()
