import datetime
import os
import json
import requests
import ollama
import logging
from fund_economics_schemas import FundFeeSchedule
from utils import clean_json_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_to_json_with_fix(extracted_data):
    """
    Converts a string to JSON. If the string is not valid JSON, attempts to fix it using LLM.
    """
    try:
        extracted_data_json = json.loads(extracted_data)
        return extracted_data_json
    except json.JSONDecodeError as e:
        logger.error("Failed to decode extracted data as JSON: %s", str(e))
        logger.info("Attempting to fix JSON format using LLM.")

        # Construct a prompt to fix the JSON format
        fix_json_prompt = f"The following text is not valid JSON. Fix it and return valid JSON only:\n{extracted_data}"

        try:
            fix_response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that fixes JSON formatting.",
                    },
                    {"role": "user", "content": fix_json_prompt},
                ],
                format="json",
            )
            logger.info(fix_response)
            fixed_data = fix_response.get("response", "No response received")
            return json.loads(fixed_data)
        except Exception as fix_error:
            logger.error("Failed to fix JSON format using LLM: %s", str(fix_error))
            raise ValueError("Failed to decode and fix extracted data as JSON.")

def curate_prompt_with_context(lpa_content):
    """
    Curates the prompt by combining the LPA content with the system prompt.
    """
    system_prompt = """
        You are an expert venture capital legal auditor extracting fund economics into structured JSON from the provided LPA document.
        
        The extracted data must be a single JSON object containing an array of fee entries under the key "fees". Each entry in the array must strictly contain ONLY these fields:
        - fund_name: Name of the venture fund entity (string, or null if not found).
        - fee_type: Must be one of ["MANAGEMENT_FEE", "CARRIED_INTEREST", "ORGANIZATIONAL_EXPENSES", "TRANSACTION_FEE_OFFSET", "OTHER"].
        - phase: Applicable period of the fund. Must be one of ["INVESTMENT_PERIOD", "POST_INVESTMENT_PERIOD", "EXTENSION_PERIOD", "ENTIRE_TERM"].
        - rate_percentage: Annual rate as an absolute float number (e.g., 2.0 for 2.0%, 0.75 for 75 bps, 20.0 for 20% carry). Null if not applicable.
        - calculation_basis: Must be one of ["COMMITTED_CAPITAL", "INVESTED_CAPITAL", "NET_INVESTED_CAPITAL", "NET_ASSET_VALUE", "OTHER"]. Null if not applicable.
        - hurdle_rate_percentage: Preferred return rate applicable to carried interest as a float (e.g., 8.0). Null if not applicable.
        - frequency: How often the fee is charged/paid (e.g., "Quarterly", "Annually"). Null if not applicable.
        - source_clause: The section number or page reference from the source agreement.
        - raw_text_citation: The exact verbatim sentence excerpt from the LPA document where this information is found.
        - additional_notes: Any additional notes, caps, or complex conditions related to the fee.
        
        No other text, markdown formatting blocks (except valid JSON syntax), or explanations should be included in the output. Only return the raw JSON object.
        
        Adhere strictly to the following resolution rules:
        
        1. Step-Down Periods:
           - If management fees step down (e.g., "2.0% during the Investment Period, and 1.5% of Net Invested Capital thereafter"), output TWO separate entries under fee_type="MANAGEMENT_FEE".
           - Assign the first entry phase="INVESTMENT_PERIOD" and the subsequent entry phase="POST_INVESTMENT_PERIOD".
        
        2. Numeric Percentages:
           - Normalize all rates to standard human percentages (e.g., write 2.0, NOT 0.02; write 20.0 for 20% carry).
           - If basis points are cited (e.g., "75 bps"), convert to decimal percentages ("0.75").
        
        3. Basis Classification:
           - Distinguish carefully between "COMMITTED_CAPITAL" (total commitment) and "NET_INVESTED_CAPITAL" (drawn capital minus write-offs/realizations). Do not default to COMMITTED_CAPITAL if the text specifies Net Invested Capital.
        
        4. Carried Interest / Waterfall:
           - Extract Carried Interest as fee_type="CARRIED_INTEREST".
           - Capture preferred returns (hurdle rate) directly into "hurdle_rate_percentage". If a GP catch-up is stated, reflect only the core carry rate in "rate_percentage".
        
        5. Fact Grounding & Absences:
           - Do not hallucinate or assume a default 2/20 structure. If a field (such as a hurdle rate or cap) is unmentioned in the text, return null.
           - Always populate "source_clause" and "raw_text_citation". Do not leave them empty.
    """
    return f"{lpa_content}\n\n{system_prompt}"

def read_file_content(file_path):
    """
    Reads the content of a file and returns it as a string.
    """
    logger.info("Reading content from file: %s", file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        logger.info("Successfully read content from file.")
        return content
    except Exception as e:
        logger.error("Failed to read file content: %s", str(e))
        raise

def validate_and_format_extracted_data(extracted_data):
    """
    Validates and formats the extracted data using the FundFeeSchedule schema.
    """
    try:
        extracted_data = clean_json_string(extracted_data)
        extracted_data_json = convert_to_json_with_fix(extracted_data)
        validated_data = FundFeeSchedule(**extracted_data_json)
        return validated_data.json(indent=4)
    except Exception as schema_error:
        logger.warning("Schema validation failed: %s", str(schema_error))
        # Proceed with the unvalidated data
        return json.dumps(extracted_data_json, indent=4)

def extract_fee_data_by_llm(txt_file_path):
    """
    Extracts fee data from the given text file path.
    """
    try:
        # Read the content of the .txt file using the helper function
        lpa_content = read_file_content(txt_file_path)

        # Curate the prompt using the helper function
        prompt = curate_prompt_with_context(lpa_content)

        logger.info("Sending prompt to Ollama model.")

        # Use Ollama in local mode with JSON format enabled
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "You are an expert venture capital legal auditor."},
                {"role": "user", "content": prompt},
            ],
            format="json",
        )

        logger.info("Received response from Ollama model.")

        extracted_data = response.get("message", {}).get("content", "")

        logger.info("Extracted data: %s", extracted_data)

        # Validate and format the extracted data
        return validate_and_format_extracted_data(extracted_data)

    except Exception as e:
        logger.exception("An error occurred during extraction.")
        raise

def extract_fee_data_by_llm_rag(txt_file_path):
    """
    Extracts fee data from the given text file path using RAG approach.
    """
    try:
        # Read the content of the .txt file using the helper function
        lpa_content = read_file_content(txt_file_path)

        # Initialize RAG service
        from rag_service import LocalRAGService
        rag_service = LocalRAGService(llm_model="llama3.2", embedding_model="nomic-embed-text")

        # Prepare document for RAG
        from langchain_core.documents import Document
        document = Document(page_content=lpa_content)

        # Load document into RAG knowledge base
        rag_service.initialize_knowledge_base([document])

        # Curate the prompt using the helper function
        prompt = curate_prompt_with_context(lpa_content)

        logger.info("Querying RAG service with prompt.")

        # Query the RAG service
        extracted_data = rag_service.query(prompt)

        logger.info("Received response from RAG service.")

        # Validate and format the extracted data
        return validate_and_format_extracted_data(extracted_data)

    except Exception as e:
        logger.exception("An error occurred during extraction with RAG.")
        raise

def lambda_handler(event, context):
    logger.info("Lambda function invoked with event: %s", event)

    # Extract the .txt file path from the event
    txt_file_name = event.get("txt_file_name")
    tool = event.get("tool", "llm")  # Default to "llm" if not specified
    if not txt_file_name:
        logger.error("Text file name is missing in the event.")
        return {"statusCode": 400, "body": "Text file name is required."}

    # Define the resources folder path relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resources_folder = os.path.join(script_dir, "..", "resources")
    txt_file_path = os.path.join(resources_folder, txt_file_name)

    logger.info("Looking for text file at path: %s", txt_file_path)

    # Check if the .txt file exists
    if not os.path.exists(txt_file_path):
        logger.error("File not found: %s", txt_file_path)
        return {"statusCode": 404, "body": f"File {txt_file_name} not found."}

    try:
        # Extract fee data
        if tool == "rag":
            logger.info("Using RAG approach for extraction.")
            extracted_data = extract_fee_data_by_llm_rag(txt_file_path)
        else:
            logger.info("Using LLM approach for extraction.")
            extracted_data = extract_fee_data_by_llm(txt_file_path)

        # Add datetime to the JSON file name
        current_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        json_file_name = (
            f"{os.path.splitext(txt_file_name)[0]}_{current_datetime}_extracted.json"
        )
        json_file_path = os.path.join(resources_folder, json_file_name)

        logger.info("Saving extracted data to file: %s", json_file_path)
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(json.loads(extracted_data), json_file, indent=4)

        logger.info("Successfully saved extracted data to file.")

        return {"statusCode": 200, "body": extracted_data}

    except Exception as e:
        logger.exception("An error occurred during processing.")
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    logger.info("Starting local testing of the Lambda function.")
    # Example event for local testing
    test_event = {
        "txt_file_name": "lpa_1.txt",  # Replace with your .txt file name in the resources folder,
        "tool": "rag"  # Change to "rag" to test the RAG approach
    }
    response = lambda_handler(test_event, None)

    try:
        body = json.loads(response["body"])  # Parse the JSON string to a Python object
        logger.info("Final response: %s", json.dumps(body, indent=4))
        print(json.dumps(body, indent=4))  # Pretty-print the JSON object
    except json.JSONDecodeError:
        logger.error("Response body is not valid JSON: %s", response["body"])
        print(response["body"])
