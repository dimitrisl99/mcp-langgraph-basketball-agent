# MCP Basketball Assistant 🏀

An AI-powered Basketball Assistant built with MCP (Model Context Protocol), LangGraph, RAG, OCR, Text-to-SQL, and local LLMs.

The project demonstrates how modern AI agents can combine:

- Unstructured knowledge retrieval (RAG)
- Structured database querying (SQL)
- Multi-turn conversation memory
- Dynamic tool routing
- Local LLM inference

within a single AI system.

---

## Learning Goals

This project was created as a hands-on learning experience focused on:

- Understanding MCP architecture
- Building custom MCP tools
- Creating a complete RAG pipeline from scratch
- Implementing OCR-based document processing
- Building vector databases and semantic search systems
- Implementing local LLM inference with Ollama
- Building Text-to-SQL systems
- Creating LangGraph-based AI agents
- Combining RAG and SQL workflows
- Building evaluation pipelines
- Measuring and improving agent latency

---

## Project Overview

The assistant can answer questions about:

### Basketball Systems & Playbooks

- How does Spain Pick and Roll work?
- Explain the Flex Offense.
- What are the progressions of 5-Out Motion?
- Explain Davidson Motion Offense.
- What play should I run against pressure defense?

### NBA Statistics

- Who leads the league in assists?
- Who has the highest scoring average?
- Which player has the best 3PT percentage?
- Compare players by points and rebounds.
- What team does Trae Young play for?

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
 Answer Generator
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
    Qwen3:8B
        │
        ▼
   Text-to-SQL
        │
        ▼
 SQLite Database
        │
        ▼
   SQL Results
        │
        ▼
    MCP Tool
```

### Agent Pipeline

```text
User Question
        │
        ▼
 Query Rewriting
        │
        ▼
 Rule-Based Router
        │
   (fallback)
        ▼
  LLM Router
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

## Agent Features

### Query Rewriting

Supports follow-up questions such as:

```text
How does Spain Pick and Roll work?

What are its advantages?
```

Automatically rewritten to:

```text
What are the advantages of Spain Pick and Roll?
```

---

### Hybrid Router

Uses:

1. Rule-Based Routing
2. LLM Fallback Routing

Examples:

```text
Who has the most assists?
→ SQL
```

```text
Explain the Flex Offense.
→ RAG
```

```text
Who is the best scorer?
→ LLM Fallback → SQL
```

---

### Multi-Turn Conversations

The assistant maintains conversation history and supports contextual follow-up questions.

---

### Agent Observability

The system tracks:

- Rewrite Time
- Routing Time
- Retrieval Time
- Context Building Time
- LLM Generation Time
- Total RAG Time
- Total Agent Time

Example:

```text
rewrite_question: 4.2s
route_question: 0.0s
rag_retrieval: 0.8s
rag_ollama_generation: 6.4s
total_agent_time: 11.8s
```

---

## Streamlit Interface

Current UI Features:

### Chat Features

- Multi-chat support
- Conversation persistence
- Chat history sidebar
- Chat renaming
- Delete chat
- Suggested starter questions
- Source citations
- Collapsible source panel

### Developer Features

- Agent Observability Panel
- Route visualization
- Retrieved sources count
- Timing breakdown
- Router method display

---

## Current Features

### OCR Pipeline

- PDF ingestion
- PyMuPDF rendering
- EasyOCR extraction
- Metadata preservation
- GPU support

### Semantic Chunking

- Semantic chunking
- Metadata-aware chunks
- Chunk merging

### Embeddings

- BAAI/bge-small-en-v1.5
- Local embeddings
- Vector search

### Vector Database

- ChromaDB
- Persistent storage
- Metadata filtering

### Retrieval

- Top-K retrieval
- Source tracking
- Page citations
- Semantic search

### Answer Generation

- Qwen3:8B
- Ollama
- Context-grounded answers
- Source-aware prompting

### SQL Pipeline

- NBA statistics database
- SQLite
- Safe execution
- SQL validation

### MCP Integration

- MCP Server
- MCP Client
- Basketball RAG Tool
- NBA Statistics Tool

### LangGraph Agent

- Query rewriting
- Dynamic routing
- Multi-tool orchestration
- RAG + SQL integration

---

## Evaluation Framework

### Retriever Evaluation

Metrics:

- Hit@K
- Text Hit@K
- Mean Reciprocal Rank (MRR)

Current Results:

```text
Hit@5: 1.00
Text Hit@5: 1.00
MRR: 1.00
```

---

### Router Evaluation

Metrics:

- Routing Accuracy

Current Results:

```text
Accuracy: 1.00
```

---

### Rewrite Evaluation

Metrics:

- Rewrite Accuracy

Current Results:

```text
Accuracy: 1.00
```

---

### End-to-End Agent Evaluation

Evaluates:

- Query Rewriting
- Routing
- MCP Communication
- Retrieval
- Generation
- Final Answers

through the complete production pipeline.

---

## Project Structure

```text
mcp-rag-sql-chatbot/

├── app/
│
├── graph/
│   ├── agent.py
│   └── mcp_client.py
│
├── mcp/
│   ├── server.py
│   └── test_client.py
│
├── rag/
│   ├── pdf_processor.py
│   ├── semantic_chunker.py
│   ├── build_vector_db.py
│   ├── retriever.py
│   └── answer_generator.py
│
├── sql/
│   ├── build_nba_db.py
│   ├── text_to_sql.py
│   └── sql_executor.py
│
├── evaluation/
│   ├── evaluate_retrieval.py
│   ├── evaluate_router.py
│   ├── evaluate_rewrite.py
│   └── evaluate_agent.py
│
├── streamlit_app.py
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
- Streamlit
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

- [x] OCR Pipeline
- [x] Semantic Chunking
- [x] Metadata Extraction

### Phase 2 — Retrieval Pipeline

- [x] Embeddings Generation
- [x] ChromaDB
- [x] Retriever

### Phase 3 — RAG System

- [x] Answer Generator
- [x] Source Citations
- [x] MCP RAG Tool

### Phase 4 — Structured Data

- [x] NBA Statistics Database
- [x] SQL Executor
- [x] Text-to-SQL
- [x] MCP SQL Tool

### Phase 5 — Agent Architecture

- [x] Query Rewriting
- [x] LangGraph Agent
- [x] Rule-Based Router
- [x] LLM Fallback Router
- [x] Multi-Turn Conversations

### Phase 6 — User Interface

- [x] Streamlit Chat UI
- [x] Multiple Chats
- [x] Chat Persistence
- [x] Rename Chat
- [x] Suggested Questions
- [x] Agent Observability

### Phase 7 — Evaluation

- [x] Retriever Evaluation
- [x] Router Evaluation
- [x] Rewrite Evaluation
- [x] End-to-End Evaluation

### Phase 8 — Future Work

- [ ] Cross-Encoder Reranking
- [ ] Hybrid Search (BM25 + Vector)
- [ ] Streaming Responses
- [ ] Multi-Agent Workflows
- [ ] Basketball Diagram Retrieval
- [ ] Advanced Analytics Dashboard

---

## Current Status

✅ Fully Functional End-to-End AI Agent

Implemented:

- OCR Pipeline
- Semantic Chunking
- Vector Database
- RAG Retrieval
- Local LLM Generation
- Text-to-SQL
- MCP Tools
- LangGraph Agent
- Query Rewriting
- Multi-turn Conversations
- Streamlit Interface
- Evaluation Framework
- Agent Observability

Next milestone:

➡ Hybrid Search + Cross-Encoder Reranking