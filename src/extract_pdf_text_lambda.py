import os
from PyPDF2 import PdfReader


def lambda_handler(event, context):
    # Extract the PDF file name from the event
    pdf_file_name = event.get("pdf_file_name")
    if not pdf_file_name:
        return {"statusCode": 400, "body": "PDF file name is required."}

    # Define the resources folder path relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resources_folder = os.path.join(script_dir, "..", "resources")
    pdf_file_path = os.path.join(resources_folder, pdf_file_name)

    # Check if the PDF file exists
    if not os.path.exists(pdf_file_path):
        return {"statusCode": 404, "body": f"File {pdf_file_name} not found."}

    try:
        # Read the PDF file
        reader = PdfReader(pdf_file_path)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()

        # Save the extracted text to a .txt file
        txt_file_name = os.path.splitext(pdf_file_name)[0] + ".txt"
        txt_file_path = os.path.join(resources_folder, txt_file_name)
        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(extracted_text)

        return {
            "statusCode": 200,
            "body": f"Text extracted and saved to {txt_file_name}.",
        }

    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    # Example event for local testing
    test_event = {
        "pdf_file_name": "lpa_1.pdf"  # Replace with your PDF file name in the resources folder
    }
    response = lambda_handler(test_event, None)
    print(response)
