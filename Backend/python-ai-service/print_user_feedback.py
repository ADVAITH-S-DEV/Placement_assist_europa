import json
with open("user_test_out.json", "r", encoding="utf-16le") as f:
    data = json.load(f)
    print("ATS Score:", data["ats_score"])
    print("\nDetailed Review:")
    for r in data["detailed_review"]:
        print(f"- {r}")
    print("\nBreakdown:", json.dumps(data["breakdown"], indent=2))
    print("\nScoring Methodology Summary:")
    for k, v in data["methodology"].items():
        print(f"{k.replace('_', ' ').capitalize()}: {v}")
