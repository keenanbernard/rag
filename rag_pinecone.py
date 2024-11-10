import os
import PyPDF2
import textwrap
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore # requires python 3.11 or lower


# Load environment variables
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
environment = os.getenv("PINECONE_ENV")

if not api_key or not environment:
    print("Error: Missing Pinecone API Key or Environment in .env file.")
    exit()

print("Pinecone and OpenAI API keys loaded successfully.")

# Initialize Pinecone
pinecone_client = Pinecone(
    api_key=api_key
)

# Define Pinecone index name
INDEX_NAME = "pdf-policies"

# Step 1: Extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Step 2: Split text into chunks
def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_text(text)

# Step 3: Create or Connect to a Pinecone Index
def create_or_connect_pinecone_index():
    # Check if the index exists, create it if not
    if INDEX_NAME not in [Index.name for Index in pinecone_client.list_indexes()]:
        print(f"Creating Pinecone index '{INDEX_NAME}'...")
        pinecone_client.create_index(
            name=INDEX_NAME,
            dimension=1536,  # Dimensionality of OpenAI embeddings
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=environment
            )
        )
    else:
        print(f"Pinecone index '{INDEX_NAME}' already exists.")

    # Return the connected index
    return pinecone_client.Index(INDEX_NAME)

# Step 4: Embed and Upload Text Chunks to Pinecone
def upload_chunks_to_pinecone(directory_path, index):
    embeddings = OpenAIEmbeddings()

    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing {pdf_path}...")
            pdf_text = extract_text_from_pdf(pdf_path)
            text_chunks = split_text_into_chunks(pdf_text)

            # Embed and upsert into Pinecone
            for i, chunk in enumerate(text_chunks):
                vector = embeddings.embed_query(chunk)
                index.upsert([(f"{filename}_{i}", vector, {"text": chunk})])

    print(f"All embeddings uploaded to Pinecone index '{INDEX_NAME}'.")

# Step 5: Answer questions using Retrieval-Augmented Generation
def answer_question(pinecone_index, question):
    # Initialize the Pinecone vector store
    vector_store = PineconeVectorStore(
        index=pinecone_index,
        embedding=OpenAIEmbeddings()
    )

    # Set up the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        retriever=vector_store.as_retriever()
    )

    # Run the chain with the query
    response = qa_chain.invoke({"query": question})

    # Extract the raw answer to string
    raw_answer = response.get("result", "") if isinstance(response, dict) else response

    # Wrap the output for readability
    wrapped_answer = textwrap.fill(raw_answer, width=80)
    return wrapped_answer


if __name__ == "__main__":
    # Path to the directory containing PDF files
    policies_directory = "policies"

    # Ensure the directory exists
    if not os.path.exists(policies_directory):
        print(f"Error: Directory not found at {policies_directory}")
        exit()

    # Create or connect to the Pinecone index
    pinecone_index = create_or_connect_pinecone_index()

    # Upload embeddings to Pinecone
    upload_chunks_to_pinecone(policies_directory, pinecone_index)

    # Ask questions
    while True:
        question = input("Enter your question (or 'exit' to quit): ")
        if question.lower() == "exit":
            break
        answer = answer_question(pinecone_index, question)
        print(f"Answer:\n{answer}")