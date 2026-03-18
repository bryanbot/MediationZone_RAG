# 📚 Multi-Document RAG API for Technical Documentation of InfoZone

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat)
![Ollama](https://img.shields.io/badge/Ollama-Llama_3-white?style=flat&logo=ollama)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange)

## 📖 Overview
This project implements a RAG (Retrieval-Augmented Generation) system designed to extract, process, and query extensive technical documentation of InfoZone (e.g., MediationZone 9.4 or UEPE Cloud manuals). 

Unlike traditional single-document RAG systems, this architecture allows for dynamic discovery and querying of multiple independent knowledge bases, ensuring zero context-bleeding (hallucinations) while maintaining 100% local and private execution.

This project is focus to be executed locally.

## ✨ Key Features
* **Dynamic & Resilient Extraction:** Web scraping scripts designed to evade Atlassian API Rate Limiting using *Exponential Backoff*, effectively extracting complex documentation trees from Confluence.
* **Semantic Chunking:** Text processing preserves document hierarchy (titles, subtitles) using `MarkdownHeaderTextSplitter`, injecting traceability metadata into each vector to cite exact source pages.
* **Decoupled Architecture (Factory Pattern):** Implementation of a RAG engine factory with *Lazy Loading*. Vector databases are only loaded into RAM when a user makes a specific query, drastically optimizing resource allocation.
* **Privacy & Local Execution:** Natural language inference is executed entirely locally via Llama 3 (through Ollama), supported by HuggingFace embedding models (`BAAI/bge-m3`).
* **Integrated Frontend (Full-Stack):** Intuitive chat user interface served statically through the same FastAPI microservice, ready to be securely exposed via tunnels (Ngrok/Cloudflare).

## 🛠️ Tech Stack
* **Backend:** Python 3.x, FastAPI, Uvicorn
* **AI & NLP:** LangChain, ChromaDB, HuggingFace Embeddings, Ollama (Llama 3)
* **Frontend:** HTML5, CSS3, Vanilla JS / jQuery

## 📂 Project Structure
```text
infozone_rag/
├── requirements.txt           # Python library information
├── extractor_confluence.py    # Interactive web extraction script
├── procesador_chunks.py       # Semantic chunking and metadata logic
├── ingesta_vectorial.py       # Batch ingestion into ChromaDB
├── factory_motores.py         # Factory Pattern for RAG engine memory management
├── api_rag.py                 # FastAPI server and routing
├── data_output/               # Raw JSON files (Auto-generated)
├── bases_vectoriales/         # ChromaDB collections (Auto-generated)
└── frontend/                  
    └── index.html             # Interactive web UI
```

## 🚀 Quickstart Guide
### 1. Prerequisites
- Clone this repository.
- Install Ollama on your system.
- Pull the language model by running in your terminal:

```bash
ollama run llama3
```
### 2. Environment Setup
Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Data Pipeline
Run the extraction and ingestion pipeline to build your local knowledge bases:
```bash
# Step 1: Extract documentation (The script will prompt for the Confluence ID and manual name)
python extractor_confluence.py

# Step 2: Create the vector database
python ingesta_vectorial.py
```

### 4. Deployment
Start the web server and API simultaneously:
```bash
python api_rag.py
```

Open your browser and navigate to `http://localhost:8000/` to interact with the GUI.

# 🗺️ Roadmap / Future Work
- Agentic AI Workflows: Evolve the system from a passive RAG (Q&A) into an LLM agent ecosystem, allowing the AI not only to read manuals but also to execute diagnostic commands or server configurations based on the technical documentation.
- Multi-Format Support: Integrate additional strategies into the extractor (Strategy Pattern) to process local PDF files and code repositories.
