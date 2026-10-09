# HealthOS — Multimodal RAG & Health Facility QA System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Qdrant](https://img.shields.io/badge/VectorDB-Qdrant-red.svg)](https://qdrant.tech/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)](https://gradio.app/)
[![Gemini 3.8 Flash](https://img.shields.io/badge/LLM-Gemini%203.8%20Flash-teal.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**HealthOS** is an enterprise-grade Multimodal Retrieval-Augmented Generation (RAG) platform tailored for health facility operational specifications, clinical guidelines, and architectural reports. It extracts and indexes structured tables, text, and visual context snapshots from technical PDF documents, enabling fast, accurate query responses with visual context verification using Gemini 3.8 Flash and Qdrant.

---

## Key Features

- **Multimodal PDF Parsing**: Extract text, layout hierarchy, and structured tables seamlessly using `pdfplumber` and `PyMuPDF` (`fitz`), eliminating local dependency on external tools like Poppler.
- **Visual Context Preservation**: Renders high-resolution snapshots per document page, allowing the multimodal LLM to evaluate visual charts, schematics, and layout tables in tandem with text.
- **Qdrant Vector Database**: Embedded, high-performance vector search engine using sentence-transformers (`all-MiniLM-L6-v2`) for semantic indexing and retrieval.
- **Gemini 3.8 Flash Reasoning**: Powered by Google's latest multimodal vision-empowered intelligence model for context synthesis and precise citation generation.
- **Enterprise UI Interface**: Sleek, branded interactive interface built with Gradio, featuring real-time ingestion status and multi-column visual context snapshot galleries.

---

## System Architecture

```
                                  [ User Input ]
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │  1. Ingestion Engine  │               │   2. RAG QA Engine    │
        │   (PyMuPDF / Plumber) │               │   (Vector Search)     │
        └───────────┬───────────┘               └───────────┬───────────┘
                    │                                       │
    Extracts Text, Tables & Page Images          Retrieves Relevant Chunks
                    │                                       │
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │ Qdrant Vector Store   │ ─────────────►│ Gemini 3.8 Flash LLM  │
        │  (Embedding Storage)  │               │  (Context + Vision)   │
        └───────────────────────┘               └───────────┬───────────┘
                                                            │
                                                            ▼
                                                [ Structured Answer + ]
                                                [ Visual Snapshot Src ]
```

---

## Repository Structure

```text
Data Science/
├── app/
│   └── main.py                     # Gradio Web Interface & Controller
├── src/
│   ├── ingestion/
│   │   └── parser.py               # PDF Parsing & Image Snapshot Extractor
│   ├── vector_store/
│   │   └── store.py                # Qdrant Vector Store Management
│   └── generation/
│       └── rag_engine.py           # Gemini 3.8 Multimodal RAG Query Engine
├── data/
│   ├── processed_pages/            # Rendered Page Snapshots
│   └── qdrant_db/                  # Embedded Qdrant Database Storage
├── .env                            # Environment Variables (API Keys)
├── .gitignore                      # Git Ignore Configuration
├── healthos.png                    # System Logo Icon
├── requirements.txt                # Python Dependencies
└── README.md                       # Project Documentation
```

---

## Getting Started

### Prerequisites

- **Python 3.10+** installed
- A **Google Gemini API Key** (obtainable from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/healthos-multimodal-rag.git
cd healthos-multimodal-rag
```

### 2. Set Up Virtual Environment

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Usage

Launch the Gradio dashboard:

```bash
python app/main.py
```

After starting, navigate to `http://127.0.0.1:7860` in your web browser.

### Step-by-Step Workflow

1. **Ingest Document**:
   - Upload a health facility PDF document (e.g., `sample_health_facility_spec.pdf`) under section **1. Ingest PDF Document**.
   - Click **Parse & Index to Qdrant**.
2. **Submit Queries**:
   - Ask questions regarding facility specifications, operational rules, or maintenance schedules in section **2. Multimodal Query & QA Engine**.
   - Example Query: *"What is the target temperature and backup power protocol for OR-202?"*
3. **Inspect Output**:
   - View synthesized text responses with exact page citations alongside visual page snapshot evidence in the gallery.

---

## Dependencies

Major packages required for this project:

```text
google-genai
google-generativeai
qdrant-client
sentence-transformers
PyMuPDF
pdfplumber
gradio
pillow
python-dotenv
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Author

Developed by **Keorapetse Makhubo** — [GitHub Profile](https://github.com/)
