from gst_assistant.core.llm import get_llm

llm = get_llm()
result = llm.generate(
    system="You answer in one short sentence.",
    prompt="What is input tax credit in GST?",
)
print(result.text)
print("tokens in:", result.tokens_in, "| tokens out:", result.tokens_out)
