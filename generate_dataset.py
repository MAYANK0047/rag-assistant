import json

# The Golden Dataset: Questions and their perfect human-verified answers
golden_data = [
    {
        "question": "Am I allowed to accept a $100 gift from a client?",
        "ground_truth": "No, you cannot accept a gift valued at more than $75 without written approval from your department head."
    },
    {
        "question": "How many vacation days can I carry over into the next year?",
        "ground_truth": "You can carry over a maximum of 5 unused vacation days into the next calendar year. Any excess is forfeited."
    },
    {
        "question": "What is the severance pay if I am terminated without cause after my probation?",
        "ground_truth": "You are entitled to severance pay equal to 2 weeks of salary per completed year of service, capped at a maximum of 26 weeks."
    },
    {
        "question": "How long do I have to report a data breach?",
        "ground_truth": "Any suspected data breach must be reported to the IT Security team within 4 hours of discovery."
    },
    {
        "question": "Does the company cover my full health insurance premium?",
        "ground_truth": "No, the company covers 80% of the premium, and the remaining 20% is deducted from your monthly pay."
    }
]

# Save to a JSON file
with open("golden_dataset.json", "w") as f:
    json.dump(golden_data, f, indent=4)

print("Golden Dataset saved as 'golden_dataset.json'")