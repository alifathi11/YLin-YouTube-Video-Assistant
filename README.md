# YLin — YouTube Video Assistant

A **RAG-based YouTube video assistant** that lets users ask questions about a YouTube video and receive answers based on its transcript.

The project includes a **FastAPI backend**, vector search with **PostgreSQL + pgvector**, automatic transcript extraction, and a browser extension integrated directly into YouTube.

## Overview

The system follows a Retrieval-Augmented Generation pipeline:

1. Extract the transcript from a YouTube video
2. Split the transcript into smaller chunks
3. Generate embeddings for each chunk
4. Store embeddings in PostgreSQL using pgvector
5. Retrieve relevant transcript sections for a user question
6. Send the retrieved context to an LLM
7. Generate an answer based on the video content

## Transcript Extraction

The system first tries to retrieve subtitles using the **YouTube Transcript API**.

If subtitles are unavailable, it falls back to:

* `yt-dlp` for downloading the video audio
* **Whisper** for speech-to-text transcription

The default preferred transcript languages are English and Persian.

## Embeddings

Transcript chunks and user questions are embedded using:

* **intfloat/multilingual-e5-small**
* Sentence Transformers
* Normalized vector embeddings

Queries use the `query:` prefix and transcript chunks use the `passage:` prefix.

## Vector Search

Embeddings are stored and searched using:

* **PostgreSQL**
* **pgvector**

A Docker Compose configuration is included for running PostgreSQL with pgvector locally.

## LLM Support

The project uses a configurable LLM provider architecture.

Supported providers include:

* OpenAI-compatible APIs
* Ollama
* Simple local context-based provider

## Browser Extension

The project includes a **Chrome Manifest V3 extension** that runs directly on YouTube video pages.

The extension communicates with the local FastAPI backend and allows users to interact with the current YouTube video.

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── llm/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── vector_store/
│   │   └── main.py
│   ├── postgres/
│   └── requirements.txt
├── extension/
│   ├── content.js
│   ├── manifest.json
│   ├── popup.html
│   └── style.css
├── test_frontend/
├── docker-compose.yml
└── LICENSE
```

## Main Services

The backend contains separate services for:

* Transcript extraction
* YouTube audio downloading
* Whisper transcription
* Transcript chunking
* Embedding generation
* Video ingestion
* Vector search
* RAG question answering

## Main Tools

* Python
* FastAPI
* Sentence Transformers
* multilingual E5
* PostgreSQL
* pgvector
* YouTube Transcript API
* yt-dlp
* Whisper
* OpenAI-compatible APIs
* Ollama
* Docker
* JavaScript
* Chrome Extension API

## Setup

Clone the repository:

```bash
git clone https://github.com/alifathi11/YLin-YouTube-Video-Assistant.git
cd YLin-YouTube-Video-Assistant
```

Start PostgreSQL with pgvector:

```bash
docker compose up -d
```

Install the backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend runs locally on:

```text
http://localhost:8000
```

## Browser Extension

To use the YouTube extension:

1. Open Chrome Extensions
2. Enable **Developer Mode**
3. Select **Load unpacked**
4. Choose the `extension/` directory
5. Open a YouTube video

The extension will communicate with the backend running on `localhost:8000`.

## Goal

The goal of YLin is to make long YouTube videos easier to explore by allowing users to ask natural-language questions and retrieve answers grounded in the actual video transcript.
