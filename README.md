# MCP Basketball Assistant 🏀

An AI-powered Basketball Assistant built with MCP (Model Context Protocol), LangGraph, RAG, OCR, and Text-to-SQL.

The goal of this project is to explore modern AI agent architectures by combining:

- MCP tools
- LangGraph agents
- Retrieval-Augmented Generation (RAG)
- OCR document processing
- Vector databases
- Text-to-SQL workflows

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

## Architecture

```text
User Question
      │
      ▼
 LangGraph Agent
      │
      ▼
     Router
      │
 ┌────┼────┐
 ▼    ▼    ▼
RAG  SQL  Future MCP Tools
      │
      ▼
 Final Response
```

---

## Current Features

### OCR Pipeline

- PDF ingestion
- Page rendering with PyMuPDF
- OCR extraction with EasyOCR
- Structured document metadata

### Semantic Chunking

- Sentence embeddings using Sentence Transformers
- Similarity-based chunk creation
- Chunk metadata preservation

---

## Project Structure

```text
mcp-basketball-assistant/

├── app/
│   ├── graph/
│   ├── mcp/
│   ├── rag/
│   └── sql/
│
├── data/
│   ├── playbooks/
│   └── processed/
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
- ChromaDB
- SQLite

---

## Development Progress

### Phase 1

- [x] Project Setup
- [x] MCP Introduction
- [x] OCR Pipeline
- [x] Semantic Chunking

### Phase 2

- [ ] Embeddings Generation
- [ ] Chroma Vector Database
- [ ] Retriever

### Phase 3

- [ ] MCP RAG Tool
- [ ] NBA Statistics Database
- [ ] Text-to-SQL

### Phase 4

- [ ] LangGraph Agent
- [ ] Multi-Tool Routing
- [ ] End-to-End Basketball Assistant

---

## Current Status

🚧 Work in Progress

The project currently includes:

- OCR-based PDF processing
- Semantic chunking pipeline
- Basketball playbook knowledge base

Next steps include embeddings generation, vector search, and MCP tool integration.