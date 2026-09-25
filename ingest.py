import chromadb
import os

def ingest_data():
    # 1. Read the full policy document
    if not os.path.exists("policy.txt"):
        print("Error: policy.txt not found.")
        return
        
    with open("policy.txt", "r", encoding="utf-8") as f:
        full_text = f.read()

    # 2. Semantic Chunking: Split by double newlines (paragraphs/sections)
    # This ensures no sentences or clauses are ever cut in half.
    chunks = [chunk.strip() for chunk in full_text.split('\n\n') if chunk.strip()]

    # 3. Initialize ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # 4. Reset collection if it exists to ensure a clean slate
    try:
        client.delete_collection(name="policy_collection")
    except:
        pass
        
    collection = client.create_collection(name="policy_collection")

    # 5. Load chunks into the vector database
    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({"source": "policy.txt"})
        ids.append(f"chunk_{i}")

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully ingested {len(chunks)} intact sections into ChromaDB!")

if __name__ == "__main__":
    ingest_data()