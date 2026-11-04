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
RETRYABLE = (429, 503)

def read_env(name, default=""):
    """Read a setting and remove spaces and stray quote marks (a common copy and paste mistake)."""
    return os.environ.get(name, default).strip().strip("\"'")

@dataclass
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int


def is_retryable(error):
    """True for rate limits (429) and temporary outages (503)."""
    code = getattr(error, "code", None)
    return code in RETRYABLE or any(str(number) in str(error) for number in RETRYABLE)


class GeminiLLM:
    def __init__(self, retries=RETRIES, wait_seconds=WAIT_SECONDS):
        from google import genai

        api_key = read_env("GEMINI_API_KEY")
        self.model = read_env("GEMINI_MODEL")
        if not api_key or not self.model:
            raise RuntimeError("GEMINI_API_KEY and GEMINI_MODEL must be set")
        self.client = genai.Client(api_key=api_key)
        self.retries = retries
        self.wait_seconds = wait_seconds

    def generate(self, system, prompt):
        from google.genai import types

        config = types.GenerateContentConfig(system_instruction=system, temperature=0)
        for attempt in range(self.retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt, config=config
                )
                break
            except Exception as error:
                if not is_retryable(error) or attempt == self.retries:
                    raise
                time.sleep(self.wait_seconds)
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


def get_llm(**options):
    """options (for example retries=1) are passed to the provider's class."""
    name = read_env("LLM_PROVIDER", "gemini")
    return PROVIDERS[name](**options)
