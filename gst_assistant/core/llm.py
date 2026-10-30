"""A small interface for language models.

The rest of the app calls get_llm().generate(...) and never imports Gemini directly.
To add another provider, write one more class and add it to PROVIDERS.
"""
import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

RETRIES = 2
WAIT_SECONDS = 20


@dataclass
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int


def is_rate_limit(error):
    return getattr(error, "code", None) == 429 or "429" in str(error)


class GeminiLLM:
    def __init__(self):
        from google import genai

        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = os.environ["GEMINI_MODEL"]

    def generate(self, system, prompt):
        from google.genai import types

        config = types.GenerateContentConfig(system_instruction=system, temperature=0)
        for attempt in range(RETRIES + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt, config=config
                )
                break
            except Exception as error:
                if not is_rate_limit(error) or attempt == RETRIES:
                    raise
                time.sleep(WAIT_SECONDS)
        usage = response.usage_metadata
        tokens_in = getattr(usage, "prompt_token_count", 0) or 0
        answer_tokens = getattr(usage, "candidates_token_count", 0) or 0
        thinking_tokens = getattr(usage, "thoughts_token_count", 0) or 0
        return LLMResponse(
            text=response.text,
            tokens_in=tokens_in,
            tokens_out=answer_tokens + thinking_tokens,
        )


PROVIDERS = {"gemini": GeminiLLM}


def get_llm():
    name = os.environ.get("LLM_PROVIDER", "gemini")
    return PROVIDERS[name]()
