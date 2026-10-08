from langchain_core.documents import Document
from rag_service import LocalRAGService

# 1. Instantiate the service
rag = LocalRAGService(llm_model="llama3.2", embedding_model="nomic-embed-text")

# 2. Prepare sample documents
raw_docs = [
    Document(page_content="Ollama allows you to run large language models locally."),
    Document(page_content="LangChain is a framework for developing applications powered by language models."),
    Document(page_content="RAG combines search retrieval with text generation for grounded answers.")
]

# 3. Load documents into the service
rag.initialize_knowledge_base(raw_docs)

# 4. Ask questions
answer = rag.query("What does Ollama allow you to do?")
print(f"\nAI Answer:\n{answer}")
