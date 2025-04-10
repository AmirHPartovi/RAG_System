import os
import ollama
import datetime

from langchain_community.document_loaders import PDFPlumberLoader

model = "llama3.2"

# Load the PDF file
pdf_files = [f for f in os.listdir("./data") if f.endswith('.pdf')]

all_pages = []

for pdf_file in pdf_files:
    file_path = os.path.join("./data", pdf_file)
    print(f"Processing PDF file : {pdf_file}")

    loader = PDFPlumberLoader(file_path)
    pages = loader.load_and_split()
    print(f"Number of pages: {len(pages)}")

    all_pages.extend(pages)

    # Extract text from pdf
    text = pages[0].page_content
    print(f"Extracted text from {pdf_file}:/n{text}")

    # Prepare the prompt for the model
    prompt = f"""
    You are an AI assistant that helps with summarizing PDF documents.
    
    Here is the content of the PDF file '{pdf_file}':
    
    {text}
    
    Please summarize the content of this document in a few sentences.
    """

    # Send the prompt and get the response
    try:
        response = ollama.generate(model=model, prompt=prompt)
        summary = response.get("response", "")

        # print(f"Summary of the PDF file '{pdf_file}':\n{summary}\n")
    except Exception as e:
        print(
            f"An error occurred while summarizing the PDF file '{pdf_file}': {str(e)}"
        )
