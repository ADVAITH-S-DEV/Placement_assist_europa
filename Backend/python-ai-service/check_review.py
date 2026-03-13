import json
with open("test_scorer_out.json", "r", encoding="utf-16le") as f:
    data = json.load(f)
    for i, line in enumerate(data.get("detailed_review", [])):
        print(f"{i+1}. {line}")
