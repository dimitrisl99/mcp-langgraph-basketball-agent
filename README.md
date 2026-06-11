# MCP Basketball Assistant 🏀

An AI-powered Basketball Assistant built with MCP (Model Context Protocol), LangGraph, RAG, OCR, and Text-to-SQL.

The project demonstrates how modern AI agents can combine unstructured knowledge retrieval and structured database querying within a single architecture.

---

## Learning Goals

This project was created as a hands-on learning experience focused on:

- Understanding MCP architecture
- Building custom MCP tools
- Creating a complete RAG pipeline from scratch
- Implementing OCR-based document processing
- Building vector databases and semantic search systems
- Implementing local LLM inference with Ollama
- Creating Text-to-SQL pipelines
- Building LangGraph-based multi-tool agents
- Combining RAG and SQL workflows into a single AI assistant

---

## Project Overview

The assistant can answer questions about:

### Basketball Systems & Playbooks

- What is a Spain Pick & Roll?
- How does the 5-Out Motion Offense work?
- What are the principles of the Flex Offense?
- Explain the Davidson Motion Offense.

### NBA Statistics

- Who leads the league in assists?
- Which players average over 25 points per game?
- Who has the highest FG% this season?
- Compare Nikola Jokic and Luka Doncic.

---

## Current Architecture

### RAG Pipeline

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
```

### SQL Pipeline

```text
User Question
        │
        ▼
     Qwen3
        │
        ▼
   Text-to-SQL
        │
        ▼
 SQLite Database
        │
        ▼
    Results
        │
        ▼
   MCP Tool
```

### Agent Architecture

```text
User Question
        │
        ▼
  LangGraph Router
        │
   ┌────┴────┐
   ▼         ▼
  RAG       SQL
   │         │
   ▼         ▼
 MCP Tool  MCP Tool
   │         │
   └────┬────┘
        ▼
 Final Answer
```

---

## Current Features

### OCR Pipeline

- PDF ingestion
- PyMuPDF page rendering
- EasyOCR extraction
- GPU acceleration support
- Structured document metadata

### Semantic Chunking

- Semantic document splitting
- Sentence-transformer embeddings
- Metadata preservation
- Chunk merging

### Vector Database

- ChromaDB persistence
- BGE embeddings
- Metadata-aware storage
- Semantic similarity search

### Retrieval Pipeline

- Top-K retrieval
- Source tracking
- Page-level citations
- Basketball playbook search

### Answer Generation

- Local inference with Ollama
- Qwen3:8B integration
- Context-grounded responses
- Source-aware prompting

### SQL Pipeline

- NBA statistics database
- SQLite storage
- Safe SQL execution
- Text-to-SQL generation
- SQL validation layer

### MCP Integration

- MCP Server
- MCP Client
- Basketball RAG Tool
- NBA Statistics Tool

### LangGraph Agent

- Multi-tool routing
- RAG vs SQL classification
- Dynamic tool selection
- End-to-end agent workflow

---

## Project Structure

```text
mcp-basketball-assistant/

├── app/
│
│   ├── graph/
│   │   ├── agent.py
│   │   └── mcp_client.py
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
│       ├── build_nba_db.py
│       ├── inspect_db.py
│       ├── sql_executor.py
│       └── text_to_sql.py
│
├── data/
│   ├── playbooks/
│   ├── processed/
│   ├── chroma/
│   └── nba_stats.db
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
- Pandas
- nba_api

---

## Development Progress

### Phase 1 — Data Processing

- [x] Project Setup
- [x] OCR Pipeline
- [x] Semantic Chunking

### Phase 2 — Retrieval Pipeline

- [x] Embeddings Generation
- [x] Chroma Vector Database
- [x] Retriever

### Phase 3 — RAG System

- [x] Answer Generator
- [x] Local LLM Integration
- [x] MCP RAG Tool

### Phase 4 — Structured Data

- [x] NBA Statistics Database
- [x] SQLite Integration
- [x] SQL Executor
- [x] Text-to-SQL Tool
- [x] MCP SQL Tool

### Phase 5 — Agent Architecture

- [x] LangGraph Agent
- [x] Multi-Tool Routing
- [x] RAG + SQL Integration

### Phase 6 — Next Steps

- [ ] Conversation Memory
- [ ] Query Rewriting
- [ ] Multi-turn Conversations
- [ ] Streamlit Chat Interface
- [ ] Agent Observability
- [ ] Evaluation Framework

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
- NBA statistics database
- Text-to-SQL pipeline
- MCP server and tools
- LangGraph routing agent
- End-to-end RAG + SQL architecture

Next milestone:

➡ Conversation Memory & Follow-up Question Handling