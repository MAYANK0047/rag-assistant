import chromadb

# 1. Connect to our saved database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="policy_collection")

# 2. The user's question
question = "How long do I have to wait for a refund if I got charged twice?"

# 3. Search the database
# We ask for the top 2 most relevant results (n_results=2)
results = collection.query(
    query_texts=[question],
    n_results=2
)

# 4. Print the results clearly
print(f"QUESTION: {question}\n")

# The results come back as nested lists, so we loop through the first list
for i, document in enumerate(results["documents"][0]):
    print(f"--- MATCH {i+1} ---")
    print(document)
    print(f"Source: {results['metadatas'][0][i]['source']}")
    print(f"Distance Score: {results['distances'][0][i]}") # Lower distance means a closer match
    print()