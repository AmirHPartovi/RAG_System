from dotenv import load_dotenv
from elevenlabs import stream
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableMap, RunnableLambda
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
    print(f"Extracted text from {pdf_file}:\n{text}")

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

    # Split and chunk
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=300)

    text_chunks = []
    for page in all_pages:
        chunks = text_splitter.split_text(page.page_content)
        text_chunks.extend(chunks)

    print(f"Number of text chunks: {text_chunks}")

    # Create Metadata for Text Chunks
   


    def add_metadata(chunks, doc_title):
        metadata_chunks = []
        for chunk in chunks:
            metadata = {
                "title": doc_title,
                "author": "R. Zafarani, M. A. Abbasi, and H. Liu,",  # Update based on document data
                "date": str(datetime.date.today()),
            }
            metadata_chunks.append({"text": chunk, "metadata": metadata})
        return metadata_chunks


    # add metadata to text chunks
    metadata_text_chunks = add_metadata(text_chunks, "BOI US FinCEN")
    # print(f"metadata text chunks: {metadata_text_chunks}")

    #Create Embedding from Text Chunks
    ollama.pull("nomic-embed-text")


    # Function to generate embeddings for text chunks
    def generate_embeddings(text_chunks, model_name="nomic-embed-text"):
        embeddings = []
        for chunk in text_chunks:
            # Generate the embedding for each chunk
            embedding = ollama.embeddings(model=model_name, prompt=chunk)
            embeddings.append(embedding)
        return embeddings


    # example embeddings
    texts = [chunk["text"] for chunk in metadata_text_chunks]
    embeddings = generate_embeddings(texts)
    print(f"Embeddings: {embeddings}")

    # Add Embeddings to Vector Database Chromadb

    # Wrap texts with their respective metadata into Document objects
    docs = [
        Document(page_content=chunk["text"], metadata=chunk["metadata"])
        for chunk in metadata_text_chunks
    ]
    # Use fastEmbeddings model from Ollama
    # to add embeddings into the vector database
    # and have a better quality of the embeddings

    fastembedding = FastEmbedEmbeddings()
    # Also for performance improvement, persist the vector database
    vector_db_path = "./db/vector_db"

    vector_db = Chroma.from_documents(
        documents=docs,
        embedding=fastembedding,
        persist_directory=vector_db_path,
        # embedding=OllamaEmbeddings(model="nomic-embed-text"),
        collection_name="docs-local-rag",
    )


    # Implement a Query Processing Muliti-query Retriever

    # LLM from Ollama
    local_model = "llama3.2"
    llm = ChatOllama(model=local_model)

    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )


    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
    )

    # RAG prompt
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """
    chat_prompt = ChatPromptTemplate.from_template(template)


    chain = (
        RunnableMap({"context": retriever, "question": RunnablePassthrough()})
        | RunnableLambda(lambda inputs: chat_prompt.format(**inputs))
        | llm
        | StrOutputParser()
    )

    questions = """
    how to find communities in social media graph?"""
    print((chain.invoke(questions)))
    response = chain.invoke(questions)

    # === TALK TO THE MODEL ===

    load_dotenv()

    text_response = response

    api_key = os.getenv("ELEVENLABS_API_KEY")

    # Generate the audio stream
    client = ElevenLabs(api_key=api_key)
    audio_stream = client.generate(
        text=str(text_response), model="eleven_turbo_v2", stream=True)
    # play(audio_stream)
    stream(audio_stream)
