import os
import json
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Lambda function to evaluate the consistency of LLM responses across multiple JSON files.

    Args:
        event (dict): Contains the 'file_name' key specifying the base file name to compare.
        context: AWS Lambda context object (not used).

    Returns:
        dict: A dictionary containing the consistency evaluation results.
    """
    logger.info("Lambda function invoked with event: %s", event)

    # Extract the base file name from the event
    base_file_name = event.get('file_name')
    if not base_file_name:
        logger.error("File name is missing in the event.")
        return {"statusCode": 400, "body": "File name is required."}

    # Define the resources folder path relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resources_folder = os.path.join(script_dir, '..', 'resources')

    # Find all JSON files matching the pattern "base_file_name_*"
    json_files = [
        os.path.join(resources_folder, f) for f in os.listdir(resources_folder)
        if f.startswith(base_file_name) and f.endswith('.json')
    ]

    if not json_files:
        logger.error("No JSON files found matching the pattern: %s_*", base_file_name)
        return {"statusCode": 404, "body": f"No JSON files found for {base_file_name}."}

    logger.info("Found JSON files: %s", json_files)

    # Load and parse all JSON files
    responses = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                responses.append(data)
        except Exception as e:
            logger.error("Failed to load JSON file %s: %s", file_path, str(e))

    if not responses:
        logger.error("No valid JSON data found in the files.")
        return {"statusCode": 500, "body": "No valid JSON data found."}

    # Compare the responses for consistency
    benchmark = responses[0]  # Use the first file as the benchmark
    inconsistencies = []

    for idx, response in enumerate(responses[1:], start=1):
        if response != benchmark:
            inconsistencies.append({
                "file": json_files[idx],
                "difference": {
                    "benchmark": benchmark,
                    "current": response
                }
            })

    # Log and return the results
    if inconsistencies:
        logger.warning("Inconsistencies found: %s", inconsistencies)
        return {
            "statusCode": 200,
            "body": {
                "message": "Inconsistencies found.",
                "details": inconsistencies
            }
        }
    else:
        logger.info("All responses are consistent.")
        return {
            "statusCode": 200,
            "body": {
                "message": "All responses are consistent."
            }
        }

if __name__ == "__main__":
    logger.info("Starting local testing of the Lambda function.")
    # Example event for local testing
    test_event = {
        "file_name": "lpa_1"  # Replace with your base file name
    }
    response = lambda_handler(test_event, None)
    body = response.get("body")
    if isinstance(body, dict):
        logger.info("Final response: %s", json.dumps(body, indent=4))
        print(json.dumps(body, indent=4))
    else:
        logger.error("Response body is not a dictionary: %s", body)
        print(body)
