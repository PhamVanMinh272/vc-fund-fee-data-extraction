from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


class LocalRAGService:
    def __init__(self, llm_model: str = "llama3:8b", embedding_model: str = "nomic-embed-text"):
        """Initializes the Ollama models, text splitter, and vector store configuration."""
        print(f"Initializing RAG Service with LLM: {llm_model} and Embeddings: {embedding_model}...")

        # 1. Setup Models
        self.llm = ChatOllama(model=llm_model, temperature=0)
        self.embeddings = OllamaEmbeddings(model=embedding_model)

        # 2. Setup Text Splitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        # 3. Setup Vector Store (In-memory for now, can be persisted to a path)
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None

    def _format_docs(self, docs):
        """Helper method to format retrieved documents for the prompt context."""
        return "\n\n".join(doc.page_content for doc in docs)

    def initialize_knowledge_base(self, documents: list[Document]):
        """Splits documents, creates embeddings, and builds the execution chain."""
        print(f"Processing {len(documents)} documents...")

        # Split text into chunks
        splits = self.text_splitter.split_documents(documents)

        # Build Chroma database
        self.vectorstore = Chroma.from_documents(documents=splits, embedding=self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})

        # Build Prompt
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)

        # Construct the final LCEL Chain
        self.rag_chain = (
                {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
        )
        print("Knowledge base successfully initialized.")

    def query(self, question: str) -> str:
        """Queries the RAG chain and returns the answer string."""
        if not self.rag_chain:
            raise ValueError("Knowledge base not initialized. Please call initialize_knowledge_base() first.")

        return self.rag_chain.invoke(question)
