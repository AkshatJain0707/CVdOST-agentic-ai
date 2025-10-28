# 🚀 Resumate Startup Guide

## Quick Start (3 Steps)

### Step 1: Start Backend Server
Open a **Command Prompt or PowerShell** and run:

```bash
cd c:\Users\asus\resumate-agentic-ai
.\.venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

✅ You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 2: Keep Terminal 1 Running, Open NEW Terminal

In a **new terminal window**, run:

```bash
cd c:\Users\asus\resumate-agentic-ai
.\.venv\Scripts\activate
streamlit run frontend.py
```

✅ Streamlit will open automatically at `http://localhost:8501`

### Step 3: Use the App

1. Go to **Dashboard Overview**
2. Upload a resume (PDF/DOCX)
3. Paste a job description
4. Click **"Analyze Resume"** ✨

---

## ✅ Verification Checklist

**Backend Server:** 
- [ ] Terminal 1 shows "Application startup complete"
- [ ] API docs available at `http://localhost:8000/docs`

**Frontend (Streamlit):**
- [ ] Terminal 2 shows "You can now view your Streamlit app in your browser"
- [ ] Opens at `http://localhost:8501`

**Connection Test:**
- [ ] Go to Dashboard → Upload resume → Paste JD → Click Analyze
- [ ] Should show "AI is analyzing your resume..." spinner
- [ ] Then results appear (no connection error)

---

## 🛠️ Troubleshooting

### Issue: "Connection refused" / "Connection reset"
**Solution:** Backend server NOT running
- Check Terminal 1 - is it showing the Uvicorn startup message?
- If not, check if port 8000 is already in use: `netstat -ano | findstr :8000`

### Issue: "Backend server not running!" error in Streamlit
**Solution:** 
1. Make sure Terminal 1 is still running and hasn't crashed
2. Check for error messages in Terminal 1
3. Look at logs in `data/logs/` directory

### Issue: "ModuleNotFoundError"
**Solution:** Make sure virtual env is activated
```bash
.\.venv\Scripts\activate
```

### Issue: Slow analysis / Timeout
**Solution:** First run downloads models (takes 1-2 min)
- Wait for completion in backend terminal
- Subsequent runs are instant due to caching

---

## 📊 API Endpoints

When backend is running, test directly:

```bash
# Health check
curl http://localhost:8000/api/health

# View API docs
http://localhost:8000/docs

# Analyze (requires multipart form)
curl -X POST http://localhost:8000/api/analyze \
  -F "resume_file=@resume.pdf" \
  -F "job_description=Your JD here"
```

---

## 📂 Important Files

- `backend/main.py` - FastAPI endpoints
- `backend/orchestration.py` - Pipeline controller
- `frontend.py` - Streamlit UI
- `data/logs/` - Analysis results and logs
- `.env` - API keys (OpenAI)

---

## 🔧 Environment Setup

Make sure `.env` file exists with:
```
OPENAI_API_KEY=your_key_here
RESULTS_DIR=data/results
```

---

## 💡 Pro Tips

1. **Keep both terminals running** - Backend in Terminal 1, Frontend in Terminal 2
2. **First run slow?** - Models download automatically, cached for speed
3. **Check logs** - `data/logs/resumate_result_*.json` for analysis details
4. **API docs** - Visit `http://localhost:8000/docs` to test endpoints directly

---

## 🎯 Next Steps

After first successful analysis:
- Check `data/logs/` for detailed results
- Use analytics tab for insights  
- Download full report when ready

Happy analyzing! 🧠✨