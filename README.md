# Fast-RAG Chatbot Pipeline

An intelligent Sales Bot powered by a Retrieval-Augmented Generation (RAG) pipeline. The project provides a scalable document ingestion framework, dynamic chunking, and an interactive chat interface to answer questions based on the uploaded company or product documents.

## 🚀 Key Features

*   **Customizable Chunking Strategies:** Choose from Recursive, Sentence, Token, Semantic, and Fixed chunking strategies, and tweak the chunk size and overlap to fit your needs.
*   **Asynchronous Processing:** Documents are processed in the background with real-time progress tracking, allowing you to use the interface uninterrupted.
*   **Modern React Interface:** A sleek, high-end React frontend (Vite) utilizing a modern "Soft UI" design and real-time response streaming via Server-Sent Events (SSE).
*   **Agentic Capabilities:** Leverages Langchain and agent frameworks to route queries effectively, with full Opik observability.
*   **Advanced Hybrid Retrieval:** Uses Qdrant's built-in hybrid search with Reciprocal Rank Fusion (RRF) for dense and sparse vectors, followed by FlashRank reranking for maximum accuracy.

## 🛠️ Technology Stack

*   **Frontend:** [React](https://react.dev/) + [Vite](https://vitejs.dev/) (with custom Neumorphic/Glassmorphism CSS)
*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (with SSE streaming)
*   **LLM & RAG Framework:** [LangChain](https://python.langchain.com/), LangChain-Groq, Opik (Observability)
*   **Embeddings & Search:** `sentence-transformers`, Qdrant (RRF Hybrid Search), FastEmbed, FlashRank
*   **Document Loading:** `PyMuPDF`

## 📁 Project Structure

```text
Rag_Chatbot\
├── frontend/              # Modern React/Vite Frontend application
├── app.py                 # Legacy Streamlit Frontend application
├── main.py                # FastAPI Backend entry point (QA_Bot)
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables (OpenAI/Groq keys, etc.)
├── backend/               # FastAPI routers (upload, query, metrics)
├── llm/                   # LLM clients and core agent interaction logic 
├── rag_pipeline/          # Core RAG components (ingestion, embedding, retrieval)
├── vectordb/              # Vector database storage and operations
├── uploads/               # Temporary storage for uploaded user files
├── utils/                 # Helper scripts and utilities
└── logs/                  # System and agent execution logs
```

## ⚙️ Setup and Installation

### 1. Clone the repository
Ensure you are in the project root directory.

### 2. Set up virtual environment (Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (if not exists) and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
# Add other necessary keys...
```

## 🏃 Running the Application

To run the application locally, you will need to start both the FastAPI backend and the React frontend. Note: Ensure Qdrant is running locally (e.g., via Docker on port 6334).

### Start the FastAPI Backend
Open a terminal, navigate to the project root, and run:
```bash
uvicorn main:app --reload --port 8000
```
*The API will be available at `http://localhost:8000`. You can test endpoints via `http://localhost:8000/docs`.*

### Start the React Frontend
In a separate terminal, navigate to the `frontend` directory and run:
```bash
npm install
npm run dev
```
*Your browser will automatically open the Sales Bot interface.*

## 💡 Usage

1. Open the React web application in your browser.
2. In the **Upload Documents** section, securely upload your data files.
3. Select your preferred **Chunking Strategy** and adjust dimensions if necessary.
4. Click **Upload** and watch the background process smoothly digest the data.
5. Head to the **Chat with Sales Bot** section to start extracting insights and asking domain-specific questions!
