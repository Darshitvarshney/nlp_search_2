# 🔍 WedPlanners NLP Search API

A production-ready NLP-powered search API built using **FastAPI**, **MongoDB**, and **LLM-assisted query understanding**.

The system enables users to search wedding vendors and venues using natural language queries such as:

- "Best photographers in Delhi with 5 years experience"
- "Wedding venues under ₹2 lakh in Noida"
- "Makeup artists in Ghaziabad"

Instead of relying only on keyword matching, the API extracts structured information from user queries, applies database filtering, optionally enriches the query using an LLM, and ranks the results based on semantic relevance.

---

# ✨ Features

- Natural Language Search
- Rule-Based Query Parsing
- Optional LLM Enrichment
- MongoDB Filtering
- Intelligent Ranking Engine
- Pagination Support
- Vendor Search
- Venue Search
- REST API using FastAPI
- Modular Architecture
- Production Ready

---

# 🏗 Architecture

```
                User Query
                     │
                     ▼
             FastAPI Search API
                     │
                     ▼
           NLP Query Processing
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
 Rule-Based Extraction      LLM Enrichment
        │                         │
        └────────────┬────────────┘
                     ▼
           Structured Query Object
                     │
                     ▼
         MongoDB Hard Filtering
                     │
                     ▼
         Candidate Result Set
                     │
                     ▼
        Custom Relevance Ranking
                     │
                     ▼
        Threshold Based Filtering
                     │
                     ▼
             Pagination
                     │
                     ▼
              JSON Response
```

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Programming Language |
| FastAPI | REST API Framework |
| Uvicorn | ASGI Server |
| MongoDB | Database |
| MongoEngine | ODM |
| OpenAI API | Optional LLM Query Enrichment |
| Pydantic | Request Validation |
| python-dotenv | Environment Variables |

---

# 📂 Project Structure

```
nlp_search_2/
│
├── app/
│   ├── models/
│   │     ├── request.py
│   │     ├── vendor_model.py
│   │     └── venue_model.py
│   │
│   ├── routes/
│   │     └── search.py
│   │
│   └── utils/
│         ├── extractor.py
│         ├── hard_filter.py
│         ├── llm.py
│         ├── nlp_engine.py
│         ├── pagination.py
│         └── ranking.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

# 🚀 Workflow

## Step 1 — User Query

The client sends a natural language search request.

Example:

```
Best photographers in Delhi with 5 years experience
```

---

## Step 2 — Rule-Based NLP

The NLP engine extracts structured filters from the query.

Example

```json
{
  "city": "Delhi",
  "min_experience": 5,
  "entity_name": null,
  "budget_max": null
}
```

The extraction identifies:

- Experience
- Budget
- Working Since
- Pincode
- Entity Name

---

## Step 3 — LLM Enrichment (Optional)

If enabled:

```
ENABLE_LLM=true
```

The extracted query is enriched using an LLM.

Additional fields include:

- City
- State
- Locality
- Semantic Tags
- Intent
- Entity Recognition

If disabled, the API continues using only rule-based extraction.

---

## Step 4 — Hard Database Filtering

The system applies MongoDB filters before ranking.

Vendor filters include:

- Experience
- Working Since
- Entity Name
- Pincode
- City
- State

Venue filters include:

- Budget
- Visibility
- Entity Name

This significantly reduces the candidate search space.

---

## Step 5 — Custom Ranking Engine

Every candidate receives a relevance score.

### Ranking Priority

| Signal | Score |
|---------|------|
| Exact Entity Match | +100 |
| Pincode Match | +100 |
| Locality Match | +50 |
| City Match | +50 |
| State Match | +50 |
| Experience Match | +10 |
| Budget Match | +10 |
| Working Since Match | +10 |
| Semantic Tag Match | +15 |

Results are then sorted based on:

1. Relevance Score
2. Last Active Date

---

## Step 6 — Threshold Filtering

Only sufficiently relevant results are returned.

```
threshold = top_score × threshold_ratio
```

Low scoring results are automatically removed while keeping meaningful matches.

---

## Step 7 — Pagination

After ranking, pagination is applied.

This ensures:

- Most relevant results appear first
- Better user experience
- Faster API responses

---

# 📡 API

## Search Endpoint

```
POST /api/v1/search
```

---

### Request

```json
{
  "query": "Best photographers in Delhi",
  "flag": "vendor",
  "page": 1,
  "limit": 10,
  "threshold_ratio": 0.2
}
```

---

### Parameters

| Field | Description |
|--------|-------------|
| query | Natural language query |
| flag | vendor / venue / all |
| page | Page number |
| limit | Results per page |
| threshold_ratio | Minimum relevance threshold |

---

### Response

```json
{
  "data": [
    {
      "vendorName": "ABC Photography",
      "city": "Delhi",
      "experience": 8,
      "_score": 175
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_results": 24,
    "total_pages": 3
  }
}
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Darshitvarshney/nlp_search_2.git
```

Move into the project

```bash
cd nlp_search_2
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running the API

```
python main.py
```

or

```
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8050
```

Swagger Documentation:

```
http://localhost:8050/docs
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
DATABASE_NAME=your_database
MONGODB_URI=your_mongodb_uri

ENABLE_LLM=true

OPENAI_API_KEY=your_api_key
```

---

# 📈 Search Pipeline

```
Natural Language Query
          │
          ▼
 Rule-Based NLP Extraction
          │
          ▼
 Optional LLM Enrichment
          │
          ▼
 Structured Query
          │
          ▼
 MongoDB Hard Filter
          │
          ▼
 Candidate Results
          │
          ▼
 Relevance Scoring
          │
          ▼
 Threshold Filtering
          │
          ▼
 Pagination
          │
          ▼
 Final Results
```

---

# 📌 Current Capabilities

- Vendor Search
- Venue Search
- Experience Filtering
- Budget Filtering
- Pincode Search
- City Search
- State Search
- Entity Recognition
- Semantic Ranking
- Pagination
- LLM-assisted Query Understanding

---

# 🚀 Future Improvements

- Vector Embeddings
- Hybrid Search (BM25 + Semantic)
- Elasticsearch Integration
- FAISS / Pinecone Support
- Multi-language Search
- Query Auto Correction
- Synonym Expansion
- Search Analytics
- Personalized Ranking
- Caching Layer (Redis)

---

# 👨‍💻 Author

**Darshit Varshney**

GitHub: https://github.com/Darshitvarshney

LinkedIn: https://www.linkedin.com/in/darshit-varshney-422002390

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
