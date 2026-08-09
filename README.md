# Talk to PDF

A voice-enabled, RAG (Retrieval-Augmented Generation) powered academic research assistant. This application allows users to upload PDF research papers, index their contents into a vector database, and perform semantic Q&A using both text and voice. The assistant streams back rigorous academic answers with precise page citations and speaks the response back to the user.

---

## Features

1. **Document Ingestion Pipeline (Asynchronous)**:
   - Multi-page PDF text extraction using PyMuPDF.
   - Semantic text chunking with overlapping windows.
   - High-quality dense vector representations using Gemini `models/gemini-embedding-001`.
   - Multi-collection indexing in Qdrant (one collection per document).
   - Automatic document summarization via Gemini `gemini-2.5-flash` on ingestion.
2. **Retrieval-Augmented Generation (RAG) Q&A**:
   - Semantic search across single or multiple documents concurrently.
   - Streamed token-by-token answer generation using Server-Sent Events (SSE).
   - Grounded context prompting with strict citation instructions (document name and page number).
3. **Voice Capability**:
   - **Speech-to-Text (STT)**: Local offline audio transcription using `faster-whisper` (int8 optimized for CPU execution).
   - **Text-to-Speech (TTS)**: High-fidelity cloud speech synthesis using ElevenLabs API, with a local `pyttsx3` fallback.
4. **Modern UI Dashboard**:
   - Clean, modern dashboard built with React and Tailwind CSS.
   - Document upload status tracker and document library.
   - Voice/Text interactive chat room with live streamed responses and interactive citation nodes.

---

## Tech Stack

### Backend
* **Web Framework**: FastAPI (Python)
* **Metadata Database**: MongoDB (using Motor async client)
* **Vector Database**: Qdrant
* **Task Queue**: Celery (with Redis as broker)
* **AI Embeddings & Generation**: Google Gemini API
* **STT & TTS**: faster-whisper, ElevenLabs API, pyttsx3

### Frontend
* **UI Framework**: React (Vite)
* **Styling**: Tailwind CSS
* **State Management**: Zustand
* **Data Fetching**: TanStack Query (React Query)

---

## Directory Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/            # API endpoints & subrouters
│   │   ├── core/           # Configuration, exceptions, and logging
│   │   ├── database/       # DB clients (MongoDB, Qdrant) and repository classes
│   │   ├── middleware/     # Custom HTTP middleware (exception handlers)
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Core service modules (LLM, Embedding, STT, TTS, PDF)
│   │   └── workers/        # Celery application and background tasks definition
│   ├── tests/              # Unit & API tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── layouts/        # Dashboard layout components
│   │   ├── pages/          # App pages (Dashboard, Chat, Login, Register)
│   │   ├── services/       # Fetch client & HTTP wrapper
│   │   ├── store/          # Zustand global stores (auth, chat, documents)
│   │   └── styles/         # CSS design tokens
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
└── docker-compose.yml      # Orchestration for MongoDB, Qdrant, Redis, Backend, and Frontend
```

---

## Configuration & Environment Variables

Create a `.env` file inside the `backend/` directory based on the following configurations:

```env
PROJECT_NAME="AI Voice Research Assistant"
API_V1_STR="/api/v1"

# Databases
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DB_NAME="voice_rag"
QDRANT_URL="http://localhost:6333"

# Task Broker
REDIS_URL="redis://localhost:6379/0"

# Storage
UPLOAD_DIR="./uploads"

# AI Credentials
GEMINI_API_KEY="your-gemini-api-key"

# Speech Services
STT_MODEL_NAME="base"
TTS_PROVIDER="local" # Use "elevenlabs" for high-fidelity API
ELEVENLABS_API_KEY=""
ELEVENLABS_VOICE_ID="zT03pEAEi0VHKciJODfn"
```

---

## Getting Started

### Method 1: Docker Compose (Recommended)

To run the entire ecosystem (FastAPI, React, MongoDB, Qdrant, Redis, and Celery worker) with a single command:

1. Clone the project.
2. Configure your `backend/.env` file.
3. Start the containers:
   ```bash
   docker-compose up --build
   ```
4. Access the applications:
   - Frontend: `http://localhost`
   - Backend API Docs: `http://localhost:8000/docs`

---

### Method 2: Local Development Setup

#### 1. Start Services
Ensure local instances of **MongoDB**, **Qdrant**, and **Redis** are running.

#### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Start the Celery worker (in a separate terminal window inside `.venv`):
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

#### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm modules:
   ```bash
   npm install --legacy-peer-deps
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to the local URL (usually `http://localhost:5173`).
