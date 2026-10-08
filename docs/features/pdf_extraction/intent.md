# Intent: Extract Text from PDF

## Overview
This feature involves creating an AWS Lambda function that takes a PDF file name as input, retrieves the PDF file from the `resources` folder, extracts its text content, and saves the extracted text to a `.txt` file.

## Goals
1. Create an AWS Lambda function in Python.
2. Accept a PDF file name as input.
3. Retrieve the specified PDF file from the `resources` folder.
4. Extract text content from the PDF file.
5. Save the extracted text to a `.txt` file in the same directory.

## Requirements
- Use Python for the Lambda function.
- Utilize a library like `PyPDF2` or `pdfplumber` for text extraction.
- Ensure error handling for cases where the PDF file does not exist or is unreadable.
- Save the extracted text in a `.txt` file with the same name as the PDF file (but with a `.txt` extension).

## Steps
1. **Input Handling**: Accept the PDF file name as input to the Lambda function.
2. **File Retrieval**: Locate the PDF file in the `resources` folder.
3. **Text Extraction**: Use a Python library to extract text from the PDF.
4. **Save Output**: Write the extracted text to a `.txt` file in the `resources` folder.
5. **Error Handling**: Implement error handling for missing files, unreadable PDFs, and other potential issues.

## Deliverables
- A Python script for the AWS Lambda function.
- Documentation on how to deploy and test the Lambda function.
- Unit tests for the Lambda function.

## Notes
- Ensure the Lambda function is stateless and idempotent.
- Follow best practices for Python development and AWS Lambda deployment.
