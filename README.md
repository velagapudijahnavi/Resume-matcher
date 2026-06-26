[Uploading README (2).md…]()
# 🎯 Resume Matcher

**An AI-powered backend system that matches resumes to job requirements using semantic understanding — not keyword matching.**

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-0078D4?style=flat&logo=microsoftazure&logoColor=white)
![FAISS](https://img.shields.io/badge/Vector%20Search-FAISS-FF6F00?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📌 Overview

Traditional resume screening relies on keyword matching, which misses qualified candidates who describe their skills differently than a job description does. **Resume Matcher** solves this by converting resumes and job descriptions into semantic vector embeddings, allowing the system to understand *meaning* — not just exact word overlap.

Built during my internship, this project automates candidate-job matching end-to-end: parsing raw files, generating embeddings, performing fast vector similarity search, and ranking results with AI-generated explanations.

## 🏗️ System Architecture

![Architecture Diagram](docs/architecture.svg)

```
User Input → Parser → Embedder → FAISS Index → Matcher → UI Results
```

| Stage | Responsibility |
|---|---|
| **Parser** | Extracts text and structured fields from resumes/JDs across PDF, DOCX, and JSON formats |
| **Embedder** | Converts parsed text into numerical vectors using Azure OpenAI embeddings |
| **FAISS Vector Store** | Stores embeddings and performs fast, scalable similarity search |
| **Matcher** | Compares query vectors against stored vectors, ranks results, and generates short explanations for each match |
| **Frontend** | Displays ranked matches with relevance scores in a simple HTML/CSS/JS interface |

## 🖥️ Live Demo

![Resume Matcher UI](docs/screenshot.png)

The system supports **two search directions**:
- **Employer Search** — recruiters describe the candidate they need (e.g. *"Candidate with 5+ years of experience in finance, Python, and communication skills"*) and get ranked, scored matches from the resume pool
- **Candidate Search** — candidates can search for relevant job openings based on their own profile

## ✨ Key Features

- 🔍 **Semantic search** — matches based on meaning and context, not just exact keywords
- 🧠 **AI-generated explanations** — every match comes with a short rationale, making results transparent and explainable
- 📄 **Multi-format support** — handles PDF, DOCX, and JSON resume/job inputs
- ⚡ **Fast, scalable retrieval** — FAISS-backed vector search performs efficiently even as the dataset grows
- 🧩 **Modular design** — parser, embedder, vector store, and matcher are independent, swappable components
- 🌐 **Simple frontend integration** — lightweight UI layer consumes the FastAPI backend directly

## 🔄 Workflow

```
User Query
   ↓
Convert to Embedding
   ↓
Search FAISS Index
   ↓
Retrieve Top Matches
   ↓
Generate Explanation
   ↓
Display Ranked Results
```

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **Storage:** Azure Blob Storage
- **Embeddings:** Azure OpenAI
- **Vector Search:** FAISS
- **Frontend:** HTML / CSS / JavaScript

## 📂 Project Structure

```
resume-matcher/
├── backend/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # App & Azure configuration
│   ├── parser.py                # Resume/JD text extraction
│   ├── embedder.py              # Azure OpenAI embedding generation
│   ├── matcher.py               # Ranking & explanation logic
│   ├── vector_store.py          # FAISS index management
│   ├── azure_loader.py          # Azure Blob Storage integration
│   ├── .env                     # Environment variables (not committed)
│   └── data/
│       ├── faiss_index/          # Persisted FAISS vector index
│       ├── jrs/                  # Job requirement files
│       └── resumes/              # Candidate resume files
├── frontend/
│   └── index.html               # Employer Search / Candidate Search UI
├── tests/
│   ├── test_parser.py
│   ├── test_matcher.py
│   └── test_vector_store.py
├── docs/
│   ├── architecture.svg
│   └── screenshot.png
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.14
- An Azure account with OpenAI and Blob Storage access

### Installation

```bash
git clone https://github.com/velagapudijahnavi/resume-matcher.git
cd resume-matcher
pip install -r requirements.txt
```

### Configuration

Create a `.env` file inside `backend/` based on `.env.example` and add your Azure credentials:

```
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
```

### Run the app

```bash
cd backend
python main.py
```

Then open `frontend/index.html` in your browser (or serve it locally) to try Employer Search or Candidate Search.

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|---|---|
| Large datasets caused high memory/time usage | Filtered and pre-processed data before embedding |
| Inconsistent job title formatting | Added cleanup logic before indexing |
| Azure OpenAI API rate limits during embedding | Implemented batched embedding requests |
| Maintaining data consistency across modules | Added structured error handling (try/except) throughout the pipeline |

## 🔮 Future Enhancements

- [ ] Improved job title extraction logic
- [ ] Parallelized indexing for faster processing
- [ ] Polished UI/UX for the frontend
- [ ] Cloud deployment (Azure App Service)
- [ ] Skill-based weighted ranking
- [ ] Personalized job recommendations
- [ ] Real-time matching as new resumes/JDs are added

## 📝 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## 👤 Author

**Jahnavi Velagapudi**
Built as part of an internship project applying AI-driven semantic search to recruitment workflows.
