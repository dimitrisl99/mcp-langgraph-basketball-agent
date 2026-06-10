# MCP Basketball Assistant 🏀

An AI-powered Basketball Assistant built with MCP (Model Context Protocol), LangGraph, RAG, OCR, and Text-to-SQL.

The goal of this project is to explore modern AI agent architectures by combining:

- MCP tools
- LangGraph agents
- Retrieval-Augmented Generation (RAG)
- OCR document processing
- Vector databases
- Text-to-SQL workflows
- Local LLM inference with Ollama

---

## Learning Goals

This project was created as a hands-on learning experience focused on:

- Understanding MCP architecture
- Building custom MCP tools
- Creating a complete RAG pipeline from scratch
- Learning semantic search and vector databases
- Implementing local LLM inference
- Combining RAG and Text-to-SQL in a single agent
- Building LangGraph-based multi-tool agents

---

## Project Overview

The assistant can answer questions about basketball systems, offensive concepts, defensive schemes, and player statistics.

### Example Questions

- What is a Spain Pick & Roll?
- How does the 5-Out Motion Offense work?
- What are the key principles of the Flex Offense?
- Which player has the most assists this season?
- Which offensive system best fits a specific player profile?

---

## Current Architecture

```text
Basketball PDFs
        │
        ▼
      OCR
        │
        ▼
Semantic Chunking
        │
        ▼
    Embeddings
        │
        ▼
   ChromaDB
        │
        ▼
    Retriever
        │
        ▼
    Qwen3:8B
        │
        ▼
   MCP Tool
        │
        ▼
 Final Answer
```

---

## Current Features

### OCR Pipeline

- PDF ingestion
- Page rendering with PyMuPDF
- OCR extraction with EasyOCR
- GPU acceleration support
- Structured document metadata

### Semantic Chunking

- Sentence-level semantic splitting
- Similarity-based chunk creation
- Metadata preservation
- Chunk merging for improved retrieval quality

### Vector Database

- BGE embeddings
- ChromaDB persistence
- Metadata-aware storage
- Semantic similarity search

### Retrieval Pipeline

- Top-K retrieval
- Basketball playbook search
- Source tracking
- Page-level citations

### Answer Generation

- Local inference with Ollama
- Qwen3:8B integration
- Context-grounded responses
- Source-aware prompting

### MCP Integration

- MCP server
- MCP client
- Playbook search tool
- Basketball question answering tool

---

## Project Structure

```text
mcp-basketball-assistant/

├── app/
│
│   ├── graph/
│   │
│   ├── mcp/
│   │   ├── server.py
│   │   └── test_client.py
│   │
│   ├── rag/
│   │   ├── pdf_processor.py
│   │   ├── semantic_chunker.py
│   │   ├── build_vector_db.py
│   │   ├── retriever.py
│   │   └── answer_generator.py
│   │
│   └── sql/
│
├── data/
│   ├── playbooks/
│   ├── processed/
│   └── chroma/
│
├── README.md
└── requirements.txt
```

---

## Technologies

- Python
- MCP (Model Context Protocol)
- LangGraph
- EasyOCR
- PyMuPDF
- Sentence Transformers
- BAAI/bge-small-en-v1.5
- ChromaDB
- Ollama
- Qwen3:8B
- SQLite

---

## Development Progress

### Phase 1 — Data Processing

- [x] Project Setup
- [x] MCP Introduction
- [x] OCR Pipeline
- [x] Semantic Chunking

### Phase 2 — Retrieval Pipeline

- [x] Embeddings Generation
- [x] Chroma Vector Database
- [x] Retriever

### Phase 3 — RAG System

- [x] Answer Generator
- [x] Local LLM Integration (Qwen3)
- [x] MCP RAG Tool

### Phase 4 — Structured Data

- [ ] NBA Statistics Database
- [ ] SQLite Integration
- [ ] Text-to-SQL Tool

### Phase 5 — Agent Architecture

- [ ] LangGraph Agent
- [ ] Multi-Tool Routing
- [ ] RAG + SQL Integration
- [ ] End-to-End Basketball Assistant

---

## Current Status

🚧 Work in Progress

Implemented:

- OCR-based PDF processing
- Semantic chunking
- Embedding generation
- Chroma vector database
- Semantic retrieval
- Local RAG pipeline
- MCP server integration
- Basketball playbook question answering

Next milestone:

➡ NBA Statistics Database + Text-to-SQL MCP Tool