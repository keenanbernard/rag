
# PDF Question Answering with LangChain

This project demonstrates a **Retrieval-Augmented Generation (RAG)** pipeline for answering questions from a given PDF document using Python, LangChain, and OpenAI's GPT model.

RAG stands for Retrieval-Augmented Generation. It is a framework designed to enhance the capabilities of language models by combining retrieval-based techniques with generative language models.

---

## How RAG Works: 

Retrieval:
A retriever fetches relevant information (e.g., from a database, documents, or embeddings) based on a query.
The retriever uses techniques like semantic search (e.g., vector similarity) to find the most relevant chunks of data.

Augmented Generation:
The retrieved information is passed as context to a generative model (like GPT-4) to generate a response.
The generative model uses the retrieved data to produce more accurate, contextually aware answers.

![plot](./flow_charts/RAG%20Diagram.png)

---

## Features

- Extracts text from PDF files.
- Splits text into manageable chunks for embedding.
- Stores embeddings using Chroma for fast retrieval.
- Generates answers using OpenAI's GPT-4 model.

---

## Requirements

- Python 3.8+
- An OpenAI API key (GPT-4 or GPT-3.5 access).

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pdf-question-answering.git
   cd pdf-question-answering
   ```
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

---

## Usage

1. Place the PDF file in the project directory (e.g., `example.pdf`).

2. Run the script:
   ```bash
   python main.py
   ```

3. Enter your questions in the terminal. Type `exit` to quit.

---

## Project Structure

```
.
├── main.py            # Main script for the project
├── requirements.txt   # List of dependencies
├── .env               # Contains environment variables (ignored by Git)
├── README.md          # Project documentation
└── example.pdf        # Example PDF file (replace with your file)
```

---

## Dependencies

- [PyPDF2](https://pypi.org/project/PyPDF2/): Extract text from PDF files.
- [LangChain](https://github.com/hwchase17/langchain): Build LLM-powered workflows.
- [LangChain-Pinecone](https://pypi.org/project/langchain-pinecone/): Integration between LangChain and Pinecone for vector storage and retrieval.
- [Pinecone](https://pypi.org/project/pinecone-client/): Manage vector embeddings with scalable and efficient cloud-based storage.
- [Chroma](https://pypi.org/project/chroma/): Manage embeddings for fast retrieval.
- [python-dotenv](https://pypi.org/project/python-dotenv/): Load environment variables from a `.env` file.

---

## Example Workflow

1. **Load PDF**: Extract text using `PyPDF2`.
2. **Text Splitting**: Split text into smaller chunks for embedding.
3. **Embedding and Storage**: Use OpenAI embeddings with Chroma or Pinecone for fast text retrieval.
4. **Question Answering**: Retrieve relevant chunks and generate answers with GPT-4.

---

## License

This project is licensed under the APACHE License. See the `LICENSE` file for details.
