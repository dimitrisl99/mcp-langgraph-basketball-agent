MCP Basketball Assistant 🏀

An AI-powered Basketball Assistant built with MCP (Model Context Protocol), LangGraph, RAG, OCR, and Text-to-SQL.

The goal of this project is to explore modern AI agent architectures by combining:

MCP tools
LangGraph agents
Retrieval-Augmented Generation (RAG)
OCR document processing
Vector databases
Text-to-SQL workflows
Project Overview

The assistant can answer questions about basketball systems, offensive concepts, defensive schemes, and player statistics.

Examples:

What is a Spain Pick & Roll?
How does the 5-Out Motion Offense work?
What are the key principles of the Flex Offense?
Which player has the most assists this season?
Which offensive system best fits a specific player profile?
Architecture

User Question

↓

LangGraph Agent

↓

Router

├── RAG Tool (Playbooks & Coaching Documents)

├── NBA Statistics Tool (Text-to-SQL)

└── Future MCP Tools

↓

Final Response

Current Features
OCR Pipeline
PDF ingestion
Page rendering with PyMuPDF
OCR extraction with EasyOCR
Structured document metadata
Semantic Chunking
Sentence embeddings using Sentence Transformers
Similarity-based chunk creation
Chunk metadata preservation
Project Structure
mcp-basketball-assistant/

├── app/
│   ├── mcp/
│   ├── rag/
│   ├── sql/
│   └── graph/
│
├── data/
│   ├── playbooks/
│   └── processed/
│
└── README.md
Technologies
Python
MCP (Model Context Protocol)
LangGraph
EasyOCR
PyMuPDF
Sentence Transformers
ChromaDB
SQLite
Roadmap
Phase 1

MCP Introduction

Project Setup

OCR Pipeline

Semantic Chunking

Phase 2

Embeddings Generation

Chroma Vector Database

Retriever

Phase 3

MCP RAG Tool

NBA Statistics Database

Text-to-SQL

Phase 4

LangGraph Agent

Multi-tool Routing

End-to-End Basketball Assistant

Status

Work in Progress 🚧

Currently implementing the RAG pipeline before integrating MCP tools and LangGraph routing.