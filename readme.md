# Enterprise RAG Policy Assistant & Automated Evaluation Pipeline

## Overview
This project is a production-grade Retrieval-Augmented Generation (RAG) API designed for technology-enabled compliance and case management. Engineered to handle complex, multi-part policy queries, the system extracts unstructured document data and enforces strict zero-hallucination guardrails. It includes an automated "LLM-as-a-Judge" evaluation framework to mathematically validate data extraction and factual alignment, serving as a robust ETL pipeline for legal and corporate workflows.

## Tech Stack
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend API** | FastAPI | High-performance async routing and HTTP endpoints |
| **Vector Database** | ChromaDB | Local, privacy-compliant semantic search and storage |
| **LLM Inference** | Groq API (`gpt-oss-120b`) | High-speed, open-weight model for logic and generation |
| **Evaluation** | Python / API Requests | Automated scoring of factual alignment and citations |

## Core Features
* **Semantic Data Ingestion (ETL):** Replaces basic character-count chunking with semantic splitting (by `\n\n`) to preserve the structural and legal boundaries of clauses, caps, and limits.
* **Strict Citation Guardrails:** The LLM is constrained by "Completeness" and "Boundary" rules, forcing it to append exact section numbers and verbatim quotes to every answer to eliminate hallucinations.
* **Dynamic Distance Thresholds:** Integrates a database-level distance score (`> 1.2`) to intercept off-topic queries before they reach the LLM, reducing API load and preventing fabricated responses.
* **Automated Evaluation Scorecard:** Features a Golden Dataset and an automated auditor script that tests the API and outputs a pass/fail matrix based on factual accuracy and formatting compliance.

## Repository Structure
* `main.py` — The FastAPI server, routing, and RAG prompt architecture.
* `ingest.py` — The ETL script for semantically chunking and loading text into ChromaDB.
* `evaluate_rag.py` — The automated testing script utilizing the LLM-as-a-Judge methodology.
* `golden_dataset.json` — The ground-truth testing matrix.
* `policy.txt` — The raw, unstructured enterprise policy handbook.

## Quick Start Guide

### 1. Install Dependencies
```bash
pip install fastapi uvicorn chromadb groq requests python-dotenv
```

### 2. Configure Environment
Create a `.env` file in the root directory and add your Groq API key:
```text
GROQ_API_KEY=your_api_key_here
```

### 3. Run the ETL Pipeline
Ingest the unstructured policy document into the ChromaDB vector store:
```bash
python ingest.py
```

### 4. Start the API Server
```bash
uvicorn main:app --reload
```

### 5. Run the Automated Evaluation
In a separate terminal window, execute the scoring matrix against the live server:
```bash
python evaluate_rag.py
```

## Engineering Roadblocks & Root Cause Analysis
During development, an automated evaluation run revealed a 60% failure rate on complex queries involving legal maximums (e.g., a 26-week severance cap). 

* **Root Cause:** Initial character-based chunking severed critical legal clauses in the database, while wide retrieval nets (`n_results=5`) caused the LLM to suffer from context confusion between adjoining policy sections.
* **Resolution:** The data extraction pipeline was overhauled to use semantic chunking, preserving strict paragraph boundaries. The prompt was reinforced with a "Boundary Rule" to prevent the LLM from hallucinating mismatched section titles. This optimization resulted in a validated 100% pass rate with perfect 5.0 factual scores across all evaluation cases.