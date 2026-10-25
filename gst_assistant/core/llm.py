"""A small interface for language models.

The rest of the app calls get_llm().generate(...) and never imports Gemini directly.
To add another provider, write one more class and add it to PROVIDERS.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int


class GeminiLLM:
    def __init__(self):
        from google import genai

        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = os.environ["GEMINI_MODEL"]

    def generate(self, system, prompt):
        from google.genai import types

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system, temperature=0),
        )
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
