# DocMind — AI Document Search

DocMind is a production-ready Retrieval-Augmented Generation (RAG) chatbot that lets users upload PDFs and chat with them using semantic search and a powerful LLM. 

## Features
- Drag-and-drop PDF upload with background processing
- Chunking, Vector Embeddings (OpenAI text-embedding-3-small)
- FAISS (local dev) and Pinecone (production) support
- Streamed Chat Completions with GPT-4o
- Source Document Citations with page numbers
- Premium UI with Tailwind CSS and React

## Architecture
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, LangChain, Pydantic v2
- **Database**: PostgreSQL (SQLAlchemy + asyncpg)
- **Vector DB**: FAISS (Dev) / Pinecone (Prod)

## Quick Start (Local Setup)
Ensure you have Docker and Docker Compose installed.

1. **Clone and Configure**:
   ```bash
   # create dot-env files
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your OPENAI_API_KEY
   ```

2. **Run Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access Services**:
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs
   
## Manual Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment
- **Frontend** is optimized for [Vercel](https://vercel.com).
  - Add `VITE_API_URL=https://your-backend-url.com/api` in Vercel settings.
- **Backend** can be deployed via Docker to Render or Railway. Make sure to set `VECTOR_STORE_TYPE=pinecone` and supply your `PINECONE_API_KEY`.
