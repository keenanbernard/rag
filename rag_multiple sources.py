import os
import PyPDF2
import textwrap
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA

load_dotenv()  # Load environment variables from .env file
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY is not set.")
else:
    print("OpenAI API key loaded successfully.")

# Step 1: Extract text from the PDF
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

# Step 3: Embed the text and store with Chroma
def create_chroma_store_from_policies(directory_path):
    embeddings = OpenAIEmbeddings()
    all_chunks = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing {pdf_path}...")
            pdf_text = extract_text_from_pdf(pdf_path)
            text_chunks = split_text_into_chunks(pdf_text)
            all_chunks.extend(text_chunks)

    # Create a Chroma store with all chunks
    chroma_store = Chroma.from_texts(all_chunks, embeddings)
    return chroma_store

# Step 4: Answer questions using Retrieval-Augmented Generation
def answer_question(chroma_store, question):
    retriever = chroma_store.as_retriever(search_kwargs={"k": 5})
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(), retriever=retriever
    )
    raw_answer = qa_chain.run(question)
    wrapped_answer = textwrap.fill(raw_answer, width=80)
    return wrapped_answer

if __name__ == "__main__":
    # Path to the directory containing PDF files
    policies_directory = "policies"

    # Ensure the directory exists
    if not os.path.exists(policies_directory):
        print(f"Error: Directory not found at {policies_directory}")
        exit()

    # Create embeddings and store in Chroma
    chroma_store = create_chroma_store_from_policies(policies_directory)

    # Ask questions
    while True:
        question = input("Enter your question (or 'exit' to quit): ")
        if question.lower() == "exit":
            break
        answer = answer_question(chroma_store, question)
        print(f"Answer: {answer}")
