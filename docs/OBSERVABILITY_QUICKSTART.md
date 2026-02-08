# 🚀 Quick Start: Enabling Observability

## ⏱️ 5-Minute Setup

### Step 1: Get Your API Key (2 minutes)

1. Visit [https://smith.langchain.com](https://smith.langchain.com)
2. Sign up with your email (or use Google/GitHub)
3. Click on **Settings** (gear icon)
4. Go to **API Keys**
5. Click **Create API Key**
6. Copy the key (starts with `ls__...`)

### Step 2: Configure Your Environment (1 minute)

Open your `.env` file and add:

```bash
# LangSmith Observability
LANGSMITH_API_KEY=ls__your_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=medical-chatbot
```

**Don't have a `.env` file?**
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install langsmith langsmith[all]
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### Step 4: Run the App (1 minute)

```bash
streamlit run app.py
```

You should see:
```
✅ LangSmith observability enabled
```

---

## ✅ Verify It's Working

### In the App

1. **Check the Sidebar**
   - Should show: "📊 LangSmith Observability: **Enabled**"

2. **Ask a Question**
   - Type: "What is diabetes?"
   - Wait for response

3. **Give Feedback**
   - Click 👍 or 👎 after the answer
   - Should see: "Thanks for your feedback!"

### In LangSmith Dashboard

1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Click on **Projects** → **medical-chatbot**
3. You should see your query in the **Runs** tab!

---

## 🎯 What You Get

### Automatic Tracking
- ✅ Every query and response
- ✅ Execution time (latency)
- ✅ Success/failure status
- ✅ Error messages

### User Feedback
- ✅ Thumbs up/down ratings
- ✅ Quality scores
- ✅ Linked to specific queries

### Performance Metrics
- ✅ Average response time
- ✅ Success rate
- ✅ Error frequency
- ✅ User satisfaction

---

## 🔍 View Your First Trace

1. Ask a question in the chatbot
2. Go to LangSmith dashboard
3. Click on the latest run
4. You'll see:
   - **Input:** Your question
   - **Output:** The answer
   - **Latency:** How long it took
   - **Metadata:** Query details
   - **Feedback:** Your rating (if given)

---

## 📊 Example Trace

```
┌─────────────────────────────────────────────────────┐
│  medical_rag_query                                  │
├─────────────────────────────────────────────────────┤
│  Input:  "What are the symptoms of diabetes?"       │
│  Output: "Common symptoms of diabetes include..."   │
│  Latency: 1.2 seconds                               │
│  Status: ✅ Success                                 │
│  Feedback: 👍 Helpful                              │
│                                                     │
│  Metadata:                                          │
│    • Model: llama-3.1-8b-instant                    │
│    • Retriever: k=3                                 │
│    • Query Length: 38 characters                    │
│    • Timestamp: 2026-01-30 10:55:41                 │
│                                                     │
│  Tags: rag, medical, chatbot                        │
└─────────────────────────────────────────────────────┘
```

---

## 🚫 Disable Observability

### Temporary (for testing)

Just comment out in `.env`:
```bash
# LANGSMITH_API_KEY=ls__your_key
```

Restart the app. You'll see:
```
ℹ️ LangSmith observability disabled (API key not configured)
```

The app will work normally, just without tracing.

### Permanent

Remove the lines from `.env` or don't set the API key.

---

## 💡 Pro Tips

### 1. **Use Different Projects**
Separate dev/staging/production:
```bash
# Development
LANGCHAIN_PROJECT=medical-chatbot-dev

# Production
LANGCHAIN_PROJECT=medical-chatbot-prod
```

### 2. **Monitor Daily**
- Check your dashboard once a day
- Review user feedback
- Look for error patterns

### 3. **Export Data**
Use the monitoring module to export runs:
```python
from src.observability.monitoring import export_runs_to_csv

export_runs_to_csv("daily_runs.csv", hours=24)
```

### 4. **Create Test Datasets**
Build evaluation datasets from real queries:
```python
from src.observability.evaluation import create_dataset

# Use your best Q&A pairs
examples = [...]
create_dataset("medical_qa_v1", examples)
```

---

## 🐛 Common Issues

### "LangSmith not enabled"
- ✅ Check `.env` file exists
- ✅ Verify `LANGSMITH_API_KEY` is set
- ✅ Restart the application

### Feedback buttons not showing
- ✅ LangSmith must be enabled
- ✅ Check sidebar shows "Enabled"
- ✅ Try asking a new question

### Traces not in dashboard
- ✅ Wait 30 seconds for sync
- ✅ Refresh the browser
- ✅ Check project name matches

---

## 📚 Learn More

- **Full Documentation:** `docs/OBSERVABILITY_INTEGRATION.md`
- **LangSmith Docs:** https://docs.smith.langchain.com/
- **Monitoring Module:** `src/observability/monitoring.py`
- **Evaluation Module:** `src/observability/evaluation.py`

---

## ✅ Checklist

- [ ] Created LangSmith account
- [ ] Got API key
- [ ] Added to `.env` file
- [ ] Installed dependencies
- [ ] Ran the app
- [ ] Saw "Observability: Enabled" in sidebar
- [ ] Asked a test question
- [ ] Gave feedback (👍/👎)
- [ ] Checked LangSmith dashboard
- [ ] Saw my trace!

---

**Congratulations! 🎉**

Your Medical Chatbot now has full observability!

Every interaction is tracked, monitored, and ready for analysis.

**Next:** Start using the app and watch your dashboard fill with insights!
