# Intent for RAG Service

The purpose of this service is to implement a Retrieval-Augmented Generation (RAG) pipeline for processing Limited Partnership Agreements (LPAs) documents. This service will:

1. **Ingest LPA Documents**: Accept text formats of LPA documents from `extract_pdf_text_lambda`.
2. **Index and Retrieve Relevant Data**: Use a vector database or other retrieval mechanism to index the processed LPA text and retrieve relevant sections based on user queries.
3. **Generate Contextual Responses**: Leverage a language model to generate responses augmented with the retrieved context.
4. **Prepare Data for Fee Extraction**: Format the output to be compatible with the `extract_fee_data_lambda` function for downstream processing.

This service aims to enhance the accuracy and efficiency of extracting and analyzing fee-related data from LPAs.

## Technical Requirements
- **Input**: Text content of LPA documents.
- **Output**: Structured data ready for fee extraction, including relevant sections and context.
- **Dependencies**: Using LangChain for RAG implementation, a vector database for indexing, and a language model for response generation. Use ollama for llm (same as extract_fee_data_lambda).