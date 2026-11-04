import os

key = os.environ.get("GEMINI_API_KEY", "")
model = os.environ.get("GEMINI_MODEL", "")
quotes = ('"', "'")

print("key length:", len(key))
print("key starts with a quote:", key.startswith(quotes))
print("key ends with a quote:", key.endswith(quotes))
print("model:", repr(model))
print("provider:", repr(os.environ.get("LLM_PROVIDER")))
