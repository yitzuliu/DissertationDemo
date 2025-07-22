# RAG Module Guide

This module provides a simple Retrieval-Augmented Generation (RAG) testing environment, combining ChromaDB vector database and the all-MiniLM-L6-v2 embedding model for semantic knowledge retrieval.

---

## Features
- Converts multiple texts into embeddings and stores them in a local ChromaDB
- Supports semantic search, returning the most relevant documents and their distance scores
- Can serve as a foundation for RAG systems

---

## Installation Steps

1. **Activate Python virtual environment**
   ```bash
   source ai_vision_env/bin/activate
   ```
2. **Install required packages**
   ```bash
   pip install chromadb sentence-transformers
   ```

---

## Usage

1. **Run the example script**
   ```bash
   python RAG/rag_module.py
   ```
   Expected output:
   ```
   Number of documents in database: 4
   Query results:
   Content: SmolVLM2-MLX is the best performing model. | Distance: 0.1234
   Content: LLaVA-MLX requires reloading the model each time, resulting in poor performance. | Distance: 0.2345
   ...
   ```

2. **Customize documents and queries**
   - Edit the `docs` and `query` variables in `rag_module.py` to add your own test content.

3. **Modular usage**
   - You can also use it in other Python scripts:
     ```python
     from RAG.rag_module import RAGModule
     rag = RAGModule()
     rag.add_documents(["Your document..."])
     results = rag.query("Your query...", n_results=3)
     ```

---

## Directory Structure
```
RAG/
  ├── rag_module.py   # Main RAG module
  └── README.md       # Usage guide
```

---

## FAQ
- **Model download failed**: Ensure you have a stable internet connection, or manually download all-MiniLM-L6-v2 locally.
- **ChromaDB startup failed**: Check the permissions and path for `RAG/chroma_db` directory.
- **Unsatisfactory query results**: Make sure the document language, content, and query semantics are aligned.

---

## Further Reading
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 Model Card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) 