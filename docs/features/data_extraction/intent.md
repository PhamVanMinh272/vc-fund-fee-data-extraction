# Intent: AWS Lambda Data Extraction for Fee Management from LPAs using Ollama (llama3.2)

## 1. Overview & Problem Statement
* **Context**: We need to extract structured fee management data from complex, unstructured Limited Partner Agreements (LPAs) text documents.
* **Problem**: Extracting these financial terms manually is slow, error-prone, and doesn't scale with the volume of incoming LPA agreements.
* **Goal**: Build a new AWS Lambda function that leverages an Ollama tool running the `llama3.2` model to automate this extraction process accurately.

## 2. Proposed Outcome
* A serverless AWS Lambda function capable of taking a target `.txt` file path as an input payload/argument.
* The function will retrieve the specific LPA text file from an internal/local `resources` folder or designated storage path.
* It will combine a predefined system prompt with the raw LPA document content and send it to the local or hosted `llama3.2` instance via Ollama.
* It will return a clean, structured payload containing the extracted fee management terms.

## 3. Scope & Boundaries
* **In Scope**:
  * Input handler for the file path string.
  * Logic to fetch the target `.txt` file from the `resources` directory.
  * Construction of the structured system prompt + user content payload for Ollama.
  * Integration call to the Ollama client/tool using the `llama3.2` model.
  * Error handling for missing files, malformed text, or LLM response timeouts/failures.
* **Out of Scope**:
  * PDF-to-text conversion (assumes input is pre-cleaned `.txt`).
  * Permanent database persistence layer for the extracted data (will output JSON response/logs).
  * Production infrastructure provisioning (Terraform/CDK scripts are secondary/future specs).

## 4. Affected Systems & Dependencies
* **Core Components**: New AWS Lambda function handler module.
* **AI Tooling**: Ollama API client running `llama3.2`.
* **Data Source**: Local/bundled `resources/` folder containing sample or target LPA text files.

## 5. Constraints & Non-Functional Requirements
* **Payload Size**: Must handle typical LPA text length limits gracefully or chunk content if it exceeds `llama3.2` context limits.
* **Timeout Configurations**: AWS Lambda timeout limits must account for LLM inference latency.
* **Environment Configuration**: Ollama endpoint URL must be configurable via environment variables (`OLLAMA_HOST`).

## 6. Open Questions / Next Steps
* Where is the `resources` folder hosted relative to the Lambda execution environment (bundled in deployment package vs mounted EFS/S3)?
* What is the precise JSON schema required for the fee management output data?
