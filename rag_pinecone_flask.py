import os
import PyPDF2
import textwrap
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore  # Requires Python 3.11 or lower

# Load environment variables
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
environment = os.getenv("PINECONE_ENV")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests
api = Api(app, doc="/docs")

if not api_key or not environment:
    raise RuntimeError("Error: Missing Pinecone API Key or Environment in .env file.")

# Initialize Pinecone
pinecone_client = Pinecone(api_key=api_key)
INDEX_NAME = ''
chat_history = []  # To store previous questions and answers


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    """Split text into chunks for embedding."""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_text(text)


def create_or_connect_pinecone_index(directory):
    """Create or connect to a Pinecone index."""
    global INDEX_NAME
    INDEX_NAME = "pdf-policies" if directory == "policies" else "pdf-products"

    if INDEX_NAME not in [Index.name for Index in pinecone_client.list_indexes()]:
        pinecone_client.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=environment)
        )
    return pinecone_client.Index(INDEX_NAME)


def upload_chunks_to_pinecone(directory_path, index):
    """Embed and upload text chunks to Pinecone."""
    embeddings = OpenAIEmbeddings()

    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            pdf_text = extract_text_from_pdf(pdf_path)
            text_chunks = split_text_into_chunks(pdf_text)

            # Embed and upsert into Pinecone
            for i, chunk in enumerate(text_chunks):
                vector = embeddings.embed_query(chunk)
                index.upsert([(f"{filename}_{i}", vector, {"text": chunk})])


def answer_question(pinecone_index, question):
    # Combine history and current question
    history_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in chat_history])
    combined_query = f"{history_text}\nQ: {question}"

    """Answer a question using the RAG pipeline."""
    vector_store = PineconeVectorStore(
        index=pinecone_index,
        embedding=OpenAIEmbeddings()
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        retriever=vector_store.as_retriever()
    )

    # Run the chain with the combined query
    response = qa_chain.invoke({"query": combined_query})

    # Extract the raw answer to string
    raw_answer = response.get("result", "") if isinstance(response, dict) else response

    # Wrap the output for readability
    wrapped_answer = textwrap.fill(raw_answer, width=80)

    # Save the current interaction to chat history
    chat_history.append((question, wrapped_answer))

    return wrapped_answer


# Flask Endpoints
@app.route("/api/v1/heartbeat", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/v1/initialize", methods=["POST"])
def initialize():
    """Initialize the Pinecone index and upload embeddings."""
    data = request.json
    directory = data.get("directory")
    if not directory or not os.path.exists(directory):
        return jsonify({"error": f"Directory '{directory}' not found"}), 400

    pinecone_index = create_or_connect_pinecone_index(directory)
    upload_chunks_to_pinecone(directory, pinecone_index)
    return jsonify({"message": f"Index '{INDEX_NAME}' initialized and embeddings uploaded."})


@app.route("/api/v1/query", methods=["POST"])
def query():
    """Answer a question based on the embeddings."""
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    pinecone_index = pinecone_client.Index(INDEX_NAME)
    answer = answer_question(pinecone_index, question)
    return jsonify({"answer": answer})


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
