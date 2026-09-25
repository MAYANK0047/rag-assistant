import json
import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Configuration
API_URL = "http://127.0.0.1:8000/cases/policy-assistant"
DATASET_PATH = "golden_dataset.json"

client_judge = Groq()

def run_evaluation():
    # 1. Load the Golden Dataset
    if not os.path.exists(DATASET_PATH):
        print(f"Error: {DATASET_PATH} not found. Run generate_dataset.py first.")
        return

    with open(DATASET_PATH, "r") as f:
        test_cases = json.load(f)

    scorecard = []

    print(f"\n--- Starting Evaluation on {len(test_cases)} Test Cases ---\n")

    for idx, case in enumerate(test_cases, 1):
        question = case["question"]
        ground_truth = case["ground_truth"]

        print(f"[{idx}/{len(test_cases)}] Evaluating: {question}")

        # 2. Query your live FastAPI RAG pipeline
        payload = {"case_id": idx, "question": question}
        try:
            res = requests.post(API_URL, json=payload)
            res.raise_for_status()
            api_data = res.json()
            generated_answer = api_data.get("answer", "")
            distance_score = api_data.get("distance_score", 0.0)
        except Exception as e:
            print(f"  -> Failed to reach FastAPI endpoint: {e}")
            continue

        # 3. LLM-as-a-Judge Evaluation Prompt
        judge_prompt = f"""
        You are an impartial auditor evaluating an AI policy assistant.
        Compare the Generated Answer against the Ground Truth answer.

        CRITERIA:
        1. Factual Alignment: Does the Generated Answer agree with the Ground Truth facts?
        2. Citation Compliance: Does the Generated Answer cite a section number and verbatim text?

        QUESTION: {question}
        GROUND TRUTH: {ground_truth}
        GENERATED ANSWER: {generated_answer}

        OUTPUT FORMAT:
        Reply ONLY with valid JSON with this exact schema:
        {{
            "verdict": "PASS" or "FAIL",
            "factual_score": 1-5,
            "has_citation": true or false,
            "feedback": "Short 1-sentence assessment"
        }}
        """

        try:
            eval_res = client_judge.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": judge_prompt}],
                response_format={"type": "json_object"},
                max_tokens=300
            )
            eval_data = json.loads(eval_res.choices[0].message.content)
        except Exception as e:
            eval_data = {
                "verdict": "ERROR",
                "factual_score": 0,
                "has_citation": False,
                "feedback": f"Evaluation error: {e}"
            }

        scorecard.append({
            "test_case": idx,
            "question": question,
            "distance": round(distance_score, 4),
            "verdict": eval_data.get("verdict"),
            "score": eval_data.get("factual_score"),
            "citation": eval_data.get("has_citation"),
            "feedback": eval_data.get("feedback")
        })

    # 4. Display the Evaluation Scorecard
    print("\n" + "="*80)
    print(f"{'#':<3} | {'Verdict':<7} | {'Score':<5} | {'Citation':<8} | {'Distance':<8} | Feedback")
    print("="*80)

    total_score = 0
    passed = 0

    for item in scorecard:
        v = item['verdict']
        if v == "PASS":
            passed += 1
        total_score += item['score'] if isinstance(item['score'], (int, float)) else 0

        print(f"{item['test_case']:<3} | {v:<7} | {item['score']:<5} | {str(item['citation']):<8} | {item['distance']:<8} | {item['feedback']}")

    print("="*80)
    pass_rate = (passed / len(test_cases)) * 100 if test_cases else 0
    avg_score = (total_score / len(test_cases)) if test_cases else 0
    print(f"Overall Pass Rate: {pass_rate:.1f}% ({passed}/{len(test_cases)})")
    print(f"Average Factual Score: {avg_score:.2f} / 5.0")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_evaluation()