# AI Banking Data Assistant

An intelligent, conversational AI assistant for banking data analysis. It accepts natural language queries and automatically routes them to the appropriate data pipeline — structured SQL queries against Snowflake, document retrieval via RAG, or a combined Client 360 view — then returns a human-readable answer with explainability metadata.

---

## Table of Contents

- [Features]
- [Architecture Overview]
- [Project Structure]
- [Tech Stack]
- [Prerequisites]
- [Installation]
- [Configuration]
- [Running the Application]
- [API Reference]
- [Query Intent Types]
- [Security]
- [How It Works]

---

## Features

- **Natural Language to SQL** — Converts plain English questions into Snowflake SQL with automatic retry and self-correction on failure.
- **RAG-Powered Document Search** — Answers unstructured questions by retrieving relevant context from indexed PDF documents using FAISS vector search.
- **Client 360 View** — Combines structured database results and unstructured document context into a unified customer insight.
- **Explainability Layer** — Every response includes a reasoning summary and a list of data sources that were queried.
- **Conversation Memory** — Maintains a rolling window of conversation history so follow-up questions resolve correctly (e.g. "his account", "that loan").
- **SQL Safety Validation** — All generated SQL is validated before execution; only read-only `SELECT` statements are permitted.
- **Auto-Retry with Self-Correction** — On SQL failure, the LLM receives the failed query and error message and regenerates corrected SQL (up to 3 attempts).
- **Chat UI** — A static HTML + css +javascript frontend served directly by the API.

---

## Architecture Overview

User Query (HTTP POST /query)
        │
        ▼
Intent Classifier (GPT-4o-mini)
        │
        ├── 1️⃣ GREETING
        │       └── Direct conversational response
        │
        ├── 2️⃣ STRUCTURED_DATA_QUERY
        │       ├── SQL Engine
        │       ├── Snowflake Execution
        │       └── LLM → Structured Insights
        │
        ├── 3️⃣ UNSTRUCTURED_DATA_QUERY
        │       ├── RAG Engine
        │       │     ├── FAISS Vector Store
        │       │     └── PDF / Document Retrieval
        │       └── LLM → Unstructured Insights
        │
        └── 4️⃣ CLIENT360
                ├── SQL Engine (Structured Data)
                ├── RAG Engine (Unstructured Data)
                ├── Insight Merger
                └── LLM → Holistic Client 360 Insights

                                │
                                ▼
                    Explainability Generator
                                │
                                ▼
            Final Response + Reasoning + Data Sources

---

## Project Structure

```
AI_DATA_BANKING_SYSTEM/
├── app/
│   ├── main.py                  
│   └── config/
│       └── settings.py          
├── core/
│   ├── intent_classifier.py     
│   └── query_router.py          
├── db/
│   ├── data.py                  
│   ├── db_executor.py           
│   ├── schema_loader.py         
│   └── snowflake_connection.py  
├── llm/
│   ├── llm_client.py            
│   └── prompts.py               
├── rag/
│   └── rag_engine.py            
├── security/
│   └── sql_validator.py         
├── structured/
│   └── sql_engine.py            
├── documents/                   
├── faiss_index/                 
├── ui/
│   └── html.html                
├── .env                         
├── requirements.txt             
└── README.md
```

---

## Tech Stack

| Layer                  | Technology                                |
| ---------------------- | ----------------------------------------- |
| API Framework          | FastAPI + Uvicorn                         |
| LLM                    | OpenAI GPT-4o-mini                        |
| Structured Database    | Snowflake                                 |
| Vector Store           | FAISS (via LangChain)                     |
| Embeddings             | OpenAI Embeddings                         |
| Document Parsing       | pypdf                                     |
| Text Splitting         | LangChain RecursiveCharacterTextSplitter  |
| SQL Validation         | Custom regex validator                    |
| Frontend               | HTML + CSS + JavaScript                   |
---

## Prerequisites

- Python 3.9+
- Node.js (optional, for frontend development)
- A Snowflake account with credentials
- An OpenAI API key
- PDF documents placed in the `documents/` folder for RAG

---

## Installation

**1. Clone the repository**

```bash
git clone "https://github.com/sirikisaryu-lab/AI_Banking_Data_Assistant"
cd AI_DATA_BANKING_SYSTEM
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your documents**

Place any PDF files you want the RAG engine to index into the `documents/` folder. The FAISS index will be built automatically on first startup.

---

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Snowflake
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_ROLE=your_role
```

---

## Running the Application

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://localhost:8000`. The chat UI is served at the root `/`.

---

## API Reference

### `GET /`

Serves the chat UI (`html.html`).

---

### `POST /query`

Submit a natural language query.

**Request Body**

```json
{
  "query": "What is the total outstanding loan amount for customer 101?",
  "conversation_history": [
    { "role": "user", "content": "Tell me about customer 101." },
    { "role": "assistant", "content": "Customer 101 is Priya Sharma..." }
  ]
}
```

Request Fields
**query** (string, required) — The user's natural language question.
**conversation_history** (array, optional) — Prior conversation turns for context. Defaults to [].                |

**Response Body**

```json
{
  "response": "The total outstanding loan amount for customer 101 is ₹4,50,000.",
  "explainability": {
    "reasoning": "The query was routed to Snowflake as a structured data query. SQL was generated to sum the OUTSTANDING_AMOUNT from the LOANS table filtered by CUSTOMER_ID = 101.",
    "data_sources": ["Snowflake Database"]
  }
}
```

---

## Query Intent Types

The system automatically classifies every query into one of four intents:

The system automatically classifies every query into one of four intents.
1.**GREETING**: A GREETING is handled directly with no data lookup. 
2.**STRUCTURED_DATA_QUERY**: A STRUCTURED_DATA_QUERY pulls data from Snowflake and covers questions about accounts, loans, transactions, and balances. 
3.**UNSTRUCTURED_DATA_QUERY**:An UNSTRUCTURED_DATA_QUERY searches the document store via RAG and handles questions about complaints, reports, or other document-based information.
4.**CLIENT360**: A CLIENT360 query combines both Snowflake and the document store to produce a holistic customer view.

## Security

- **Read-only enforcement** — The SQL validator rejects any query that is not a `SELECT` statement or that contains keywords such as `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, or `TRUNCATE`.
- **No multi-statement execution** — Queries containing `;` are blocked to prevent SQL injection via statement chaining.
- **No retry on forbidden SQL** — If a disallowed operation is detected, the request is terminated immediately without retry.
- **API keys via environment** — All secrets are loaded from `.env` and never hardcoded.

---

## How It Works

**1. Intent Classification**
Every query is sent to the LLM with a classification prompt. The model returns one of the four intent labels, which determines the processing pipeline.

**2. Structured Queries (SQL)**
The schema is fetched from Snowflake and provided as context to the LLM, which generates a SQL `SELECT` query. The query is validated for safety, then executed. If execution fails, the error and the failed SQL are sent back to the LLM for self-correction (up to 3 attempts). The raw results are then passed to the LLM to generate a natural language summary.

**3. Unstructured Queries (RAG)**
PDF documents in the `documents/` folder are loaded, chunked, and embedded using OpenAI Embeddings on first startup. The FAISS index is persisted to disk at `faiss_index/` and reloaded on subsequent startups. Relevant chunks are retrieved via similarity search and passed to the LLM to generate a contextual answer.

**4. Client 360**
Both the SQL pipeline and the RAG pipeline are executed. Their outputs are combined and sent to the LLM with a dedicated Client 360 prompt to produce a unified customer insight.

**5. Explainability**
After generating an answer, a separate LLM call produces a reasoning summary explaining how the answer was derived. The data sources queried are determined programmatically based on the intent. Both are returned alongside the main response.