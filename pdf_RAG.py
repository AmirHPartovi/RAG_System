# Dirty Code
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
import ollama
import nltk
import certifi
import ssl
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
import glob


# 0-nltk Issue Solved
ssl._https_verify_context = ssl.create_default_context(cafile=certifi.where())
nltk.download('wordnet')

# 1-Ingest PDF files
doc_path = "./data/*.pdf"
pdf_files = glob.glob(doc_path)
model = "llama3.2"

# Load Local PDF files

if pdf_files:
    data = []
    for pdf_file in pdf_files:
        loader = UnstructuredPDFLoader(file_path=pdf_file)
        data.extend(loader.load())
    print("Loading DONE ...")
else:
    print("No PDF files found in the specified path.")

    # Preview first page
# content = data[0].page_content
# print(content[:100])

# END OF PART ====> #1-Ingest PDF files

# 2-Extract text from PDF and convert to small chunks

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200, chunk_overlap=300)
chunks = text_splitter.split_documents(data)
print("Splitting DONE ...")

# print(f"Number of chunks: {len(chunks)}")
# print(f"Example chunk : {chunks[0]}")

# END OF PART ====> #2-Extract text from PDF and convert to small chunks

# 3- Add to vectorDB

ollama.pull("nomic-embed-text")

vector_DB = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="simple-RAG"
)

print("Adding to vectorDB DONE ...")
# END OF PART ====> #3- Add to vectorDB

# 4- Retrieval

# set up model
llm = ChatOllama(model=model)
# llm = ChatOllama(model="llama3.2")

# a simple technique to generate multiple questions from a single question and then retrieve documents
# based on those questions, getting the best of both worlds.
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
    vector_DB.as_retriever(), llm, prompt=QUERY_PROMPT
)
# RAG prompt
template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)


chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# res = chain.invoke(input=("what is the document about?",))
# res = chain.invoke(
#     input=("what are the main points as a business owner I should be aware of?",)
# )
res = chain.invoke(input=("how to find communities in social media graph?",))

print(res)
