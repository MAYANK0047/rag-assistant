from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from groq import Groq
import os
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# 2. Connect to the Vector Database
client_db = chromadb.PersistentClient(path="./chroma_db")
collection = client_db.get_collection(name="policy_collection")

# 3. Connect to the Groq API (automatically uses GROQ_API_KEY from .env)
client_llm = Groq() 

class AIRequest(BaseModel):
    case_id: int
    question: str

@app.post("/cases/policy-assistant")
def ask_ai(request: AIRequest):
    
    # 4. Top-K Retrieval: Grab the top 3 closest chunks 
    results = collection.query(
        query_texts=[request.question],
        n_results=3  
    )
    
    # Join the top 3 chunks into a single text block
    best_match_text = "\n\n".join(results["documents"][0])
    
    # Track the best match's source and distance for our guardrails
    best_match_source = results["metadatas"][0][0]["source"]
    best_match_distance = results["distances"][0][0]
    
    # 5. Guardrail: Check the distance score
    if best_match_distance > 1.2:
        return {
            "case_id": request.case_id,
            "question": request.question,
            "answer": "System: Query blocked. No relevant policy found in the database.",
            "distance_score": best_match_distance
        }

    # 6. Build the Combined Prompt with Strict Citation Rules & Context Boundaries
    combined_prompt = f"""
    You are a professional policy assistant for a case management system.
    Answer the user's question using ONLY the provided policy text below.
    
    POLICY TEXT:
    {best_match_text}

    INSTRUCTIONS:
    - If the policy text answers the question, write it clearly.
    - COMPLETENESS RULE: You must include all relevant conditions, limits, and exceptions found in the text (e.g., maximum caps or time limits). Do not shorten or summarize away important legal details.
    - CITATION RULE: You MUST append the exact Section Number and Section Title where you found the answer, followed by a verbatim quote of the relevant sentence enclosed in quotation marks.
    - BOUNDARY RULE: Do not mix section numbers/titles with text from different sections. Ensure your citation exactly matches the section the text was pulled from.
    - Example Output: Yes, refunds take 5 to 10 days. (Source: SECTION 2.3 - Refund Processing: "Refunds will be issued to the original payment method within 5-10 business days...")
    - If the policy text answers ONE part of the question but not the other, provide what you can and clearly state that the remaining information is missing from the policy.
    - If the policy text does not contain the answer at all, you must output exactly: 'I cannot answer this based on the current policy.'

    USER QUESTION: {request.question}
    """

    try:
        # 7. Generate the response using Groq's active free-tier model
        response = client_llm.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=3000
        )
        final_answer = response.choices[0].message.content
        
    except Exception as e:
        final_answer = f"LLM Connection Error: {str(e)}"
    
    # 8. Return the final formatted JSON package
    return {
        "case_id": request.case_id,
        "question": request.question,
        "answer": final_answer.strip(),
        "citation": best_match_source,
        "distance_score": best_match_distance
    }