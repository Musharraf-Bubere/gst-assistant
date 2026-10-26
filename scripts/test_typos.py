from gst_assistant.domains.gst.answer import build_keyword_index, load_records

index = build_keyword_index(load_records())
for word in ["gingr", "prasad", "electricity", "spaceship", "tomatos", "ginger", "3306", "cryptocurrency"]:
    print(word, "->", index.correct(word))
