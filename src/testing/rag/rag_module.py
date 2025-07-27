import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class RAGModule:
    def __init__(self, persist_directory="./src/testing/rag/chroma_db", collection_name="rag_collection"):
        """
        Initialize RAG module with sentence transformer and ChromaDB
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.Client(Settings(persist_directory=self.persist_directory))
        self.collection = self.client.get_or_create_collection(self.collection_name)

    def add_documents(self, documents, ids=None):
        """
        Add documents to the RAG collection
        
        Args:
            documents: List of document texts to add
            ids: Optional list of document IDs
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Generate embeddings for documents
        embeddings = self.model.encode(documents).tolist()
        self.collection.add(documents=documents, embeddings=embeddings, ids=ids)

    def query(self, query_text, n_results=3):
        """
        Query the RAG collection for similar documents
        
        Args:
            query_text: Query text to search for
            n_results: Number of results to return
            
        Returns:
            Dictionary containing query results with documents and distances
        """
        # Generate embedding for query
        query_embedding = self.model.encode([query_text]).tolist()[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return results

    def count(self):
        """
        Get the number of documents in the collection
        
        Returns:
            Number of documents in the collection
        """
        return self.collection.count()

    def clear_collection(self):
        """
        Clear all documents from the collection
        """
        self.collection.delete(where={})

    def get_document_by_id(self, doc_id):
        """
        Retrieve a specific document by ID
        
        Args:
            doc_id: Document ID to retrieve
            
        Returns:
            Document content if found, None otherwise
        """
        try:
            result = self.collection.get(ids=[doc_id])
            if result['documents']:
                return result['documents'][0]
            return None
        except Exception:
            return None

if __name__ == "__main__":
    # Example usage
    rag = RAGModule()
    
    # Sample documents for testing
    docs = [
        "AI Manual Assistant is a multi-module AI vision processing system.",
        "SmolVLM2-MLX is the best performing model for vision-language tasks.",
        "Moondream2 supports both image and text input for comprehensive analysis.",
        "LLaVA-MLX provides efficient vision-language understanding capabilities.",
        "The system uses dual-loop memory architecture for real-time task tracking.",
        "RAG knowledge base enables intelligent step matching and progress tracking."
    ]
    
    # Add documents to the collection
    rag.add_documents(docs)
    print(f"Number of documents in database: {rag.count()}")
    
    # Test queries
    test_queries = [
        "Which model has the best performance?",
        "What is the system architecture?",
        "How does the memory system work?",
        "What are the vision processing capabilities?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = rag.query(query, n_results=2)
        print("Results:")
        for doc, score in zip(results['documents'][0], results['distances'][0]):
            print(f"  Content: {doc} | Distance: {score:.4f}") 