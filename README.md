# CVdOST - AI Career Engine

**Intelligent Resume Analysis & Job Matching Platform**

CVdOST is an agentic AI system that analyzes resumes against job descriptions, scores ATS compatibility, identifies skill gaps, and provides actionable optimization recommendations.

## 🚀 Features

- **Resume Parsing** - Extract text, sections, and skills from PDF/DOCX/TXT files
- **ATS Scoring** - Evaluate resume compatibility with Applicant Tracking Systems
- **Semantic Matching** - AI-powered matching between resume and job requirements
- **Skill Analysis** - Extract and compare technical and soft skills
- **Optimization** - Get AI-driven suggestions to improve resume content
- **Analytics Dashboard** - Interactive visualizations and insights (Streamlit)
- **REST API** - FastAPI backend for programmatic access

## 🛠 Tech Stack

- **Frontend**: Streamlit + Plotly
- **Backend**: FastAPI + Uvicorn
- **AI/ML**: OpenAI, Transformers, Sentence-Transformers, LangChain
- **NLP**: spaCy, NLTK, TextBlob, KeyBERT
- **Search**: FAISS, ChromaDB

## ⚙️ Setup

1. **Clone and install**
   ```bash
   git clone https://github.com/AkshatJain0707/CVdOST-agentic-ai.git
   cd CVdOST-agentic-ai
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

3. **Run the application**
   ```bash
   # Backend (FastAPI)
   uvicorn backend.main:app --reload

   # Frontend (Streamlit) - in another terminal
   streamlit run frontend.py
   ```

4. **Access**
   - Frontend: http://localhost:8501
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📋 API Usage

**Analyze a resume against a job description:**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume_file=@resume.pdf" \
  -F "job_description=Job description text..." \
  -F "target_role=Software Engineer"
```

## 📁 Project Structure

```
CVdOST-agentic-ai/
├── backend/
│   ├── agents.py          # Agent orchestration
│   ├── main.py            # FastAPI entrypoint
│   ├── orchestration.py   # Pipeline coordination
│   ├── models/            # Data models and LLM client
│   ├── tools/             # Extraction and analysis tools
│   ├── storage/           # Data persistence
│   └── utils/             # Logging and utilities
├── frontend.py            # Streamlit UI
├── requirements.txt       # Dependencies
└── data/                  # Logs, results, uploads
```

## 🎯 Core Workflow

1. **Resume Parsing** - Extract content and structure
2. **JD Analysis** - Parse job requirements and skills
3. **Semantic Matching** - Compare using embeddings
4. **ATS Scoring** - Evaluate keyword alignment
5. **Optimization** - Generate improvement suggestions

##  📦 Dependencies

See `requirements.txt` for full list. Key packages:
- `fastapi`, `uvicorn` - Web framework
- `streamlit` - Frontend
- `openai`, `transformers` - AI/ML
- `pdfplumber`, `python-docx` - Document parsing

## 📝 License

MIT

---

**Built by Akshat AI Labs** | Transforming careers with Intelligence ⚡
