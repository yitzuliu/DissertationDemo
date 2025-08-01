import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class RAGModule:
    def __init__(self, persist_directory="./src/testing/RAG/chroma_db", collection_name="rag_collection"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.Client(Settings(persist_directory=self.persist_directory))
        self.collection = self.client.get_or_create_collection(self.collection_name)

    def add_documents(self, documents, ids=None):
        # Process documents for storage (example: text normalization)
        processed_documents = [doc.strip() for doc in documents]
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(processed_documents))]
        embeddings = self.model.encode(processed_documents).tolist()
        self.collection.add(documents=processed_documents, embeddings=embeddings, ids=ids)

    def query(self, query_text, n_results=3):
        # Process query text for search (example: text normalization)
        processed_query = query_text.strip()
        query_embedding = self.model.encode([processed_query]).tolist()[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return results

    def count(self):
        return self.collection.count()

if __name__ == "__main__":
    # Example usage
    rag = RAGModule()
    docs = [
        "AI Manual Assistant is a multi-module AI vision processing system.",
        "SmolVLM2-MLX is the best performing model.",
        "Moondream2 only supports image input.",
        "LLaVA-MLX requires reloading the model each time, resulting in poor performance."
    ]
    rag.add_documents(docs)
    print(f"Number of documents in database: {rag.count()}")
    query = "Which model has the best performance?"
    results = rag.query(query)
    print("Query results:")
    for doc, score in zip(results['documents'][0], results['distances'][0]):
        print(f"Content: {doc} | Distance: {score:.4f}") 