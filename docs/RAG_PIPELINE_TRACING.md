# 🔍 RAG Pipeline Tracing Guide

**Date:** 2026-02-03  
**Purpose:** Complete guide to viewing all RAG pipeline steps in LangSmith

---

## ✅ **What's Already Traced:**

### **1. Q&A Session (Complete Pipeline)** ✅

**When:** Every time a user asks a question in Streamlit

**What's tracked:**
```
User Query
    ↓
🔍 Document Retrieval
    ├── Number of documents retrieved
    ├── Document sources
    ├── Retrieval parameter (k=3)
    ↓
📝 Context Formatting
    ├── Context length
    ├── Number of chunks
    ↓
🤖 LLM Generation
    ├── Prompt length
    ├── Model used
    ├── Temperature
    ├── Tokens (input/output)
    ├── Latency
    ↓
✅ Final Answer
```

---

## 📊 **How to View in LangSmith:**

### **Step 1: Go to LangSmith**
```
https://smith.langchain.com/
```

### **Step 2: Select Project**
```
Projects → medical-chatbot
```

### **Step 3: Click on a Trace**
You'll see a detailed view with all steps!

---

## 🔍 **What You Can See for Each Query:**

### **1. Query Input**
```
Input: "What is diabetes?"
Query Length: 18 characters
Timestamp: 2026-02-03 19:45:00
```

### **2. Retrieval Step**
```
🔍 Document Retrieval
├── Retrieved: 3 documents
├── Sources:
│   ├── data/medical_data.pdf
│   ├── data/policy_docs.pdf
│   └── data/health_records.csv
├── Retrieval K: 3
└── Latency: 0.15s
```

### **3. Context Formation**
```
📝 Context Formatting
├── Context Length: 1,245 characters
├── Number of Chunks: 3
└── Formatted Context Preview:
    "Diabetes is a chronic condition..."
```

### **4. LLM Call**
```
🤖 LLM Generation
├── Model: llama-3.1-8b-instant (Groq)
├── Prompt Length: 1,500 characters
├── Temperature: 0.5
├── Max Tokens: 512
├── Input Tokens: 375
├── Output Tokens: 150
├── Latency: 0.52s
└── Cost: $0.0001
```

### **5. Final Answer**
```
✅ Output
├── Answer: "Diabetes is a chronic metabolic disorder..."
├── Answer Length: 450 characters
└── Total Latency: 0.72s
```

---

## 📋 **Metadata Tracked:**

### **Query Metadata:**
- ✅ Query text
- ✅ Query length
- ✅ Timestamp
- ✅ User session (if available)

### **Retrieval Metadata:**
- ✅ Number of documents retrieved
- ✅ Document sources
- ✅ Retrieval parameter (k)
- ✅ Similarity scores (if available)

### **LLM Metadata:**
- ✅ Model name
- ✅ Provider (Groq/Gemini/OpenAI)
- ✅ Temperature
- ✅ Max tokens
- ✅ Actual tokens used
- ✅ Latency
- ✅ Cost (if applicable)

### **Response Metadata:**
- ✅ Answer length
- ✅ Total latency
- ✅ Success/Error status

---

## 🎯 **Example Trace View:**

```
Trace: medical_rag_query
├── Input
│   └── query: "What is diabetes?"
│
├── Step 1: Retrieval
│   ├── Duration: 0.15s
│   ├── Retrieved: 3 docs
│   └── Sources: [medical_data.pdf, ...]
│
├── Step 2: Context Formatting
│   ├── Duration: 0.01s
│   └── Context: 1,245 chars
│
├── Step 3: LLM Call
│   ├── Duration: 0.52s
│   ├── Model: llama-3.1-8b-instant
│   ├── Tokens: 375 → 150
│   └── Cost: $0.0001
│
└── Output
    ├── Answer: "Diabetes is..."
    └── Total Duration: 0.72s
```

---

## 🔍 **Detailed Steps You Can See:**

### **1. Document Retrieval** 🔍
**What's visible:**
- Number of documents retrieved (3)
- Source files for each document
- Retrieval parameter (k=3)
- Which chunks were selected

**How to view:**
```
LangSmith → Trace → Expand "Retrieval" step
```

### **2. Embedding Search** (Implicit)
**What happens:**
- Query is embedded using sentence-transformers
- Similarity search in FAISS
- Top-k documents returned

**Note:** Embedding step is fast and automatic, not separately traced

### **3. Context Assembly** 📝
**What's visible:**
- Retrieved documents combined
- Context length
- Formatted text sent to LLM

**How to view:**
```
LangSmith → Trace → View "Context" in metadata
```

### **4. LLM Generation** 🤖
**What's visible:**
- Full prompt sent to LLM
- Model parameters
- Token usage
- Response time
- Generated answer

**How to view:**
```
LangSmith → Trace → Expand "LLM" step
```

---

## 📊 **Console Logs (Real-time):**

**When you run the app, you'll see:**

```
2026-02-03 19:45:00 - app - INFO - Processing query: What is diabetes?...
2026-02-03 19:45:00 - app - INFO - 🔍 Starting document retrieval...
2026-02-03 19:45:00 - app - INFO - ✅ Retrieved 3 relevant documents
2026-02-03 19:45:00 - app - DEBUG - Doc 1: Diabetes is a chronic condition... (source: medical_data.pdf)
2026-02-03 19:45:00 - app - DEBUG - Doc 2: Type 2 diabetes is characterized... (source: medical_data.pdf)
2026-02-03 19:45:00 - app - DEBUG - Doc 3: Managing diabetes requires... (source: medical_data.pdf)
2026-02-03 19:45:00 - app - DEBUG - 📝 Formatted context length: 1245 chars
2026-02-03 19:45:00 - app - INFO - 🤖 Generating answer with LLM...
2026-02-03 19:45:01 - app - INFO - Successfully generated answer (length: 450)
```

---

## 🎯 **What's NOT Traced (Yet):**

### **Vector Store Creation:**
- ❌ Initial document loading
- ❌ Text chunking process
- ❌ Embedding generation
- ❌ FAISS index creation

**Why:** These happen once during setup, not during queries

**To trace:** Run `create_vector_db.py` with logging enabled

---

## 💡 **How to Enable Debug Logging:**

### **See More Details:**

**Edit `src/utils/logger.py`:**
```python
# Change level from INFO to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

**Or set in environment:**
```bash
# .env
LOG_LEVEL=DEBUG
```

**You'll see:**
- Full document content
- Exact prompts
- Detailed timing
- All metadata

---

## 📈 **Performance Metrics Available:**

### **In LangSmith Dashboard:**

**Latency Breakdown:**
```
Total: 0.72s
├── Retrieval: 0.15s (21%)
├── Formatting: 0.01s (1%)
├── LLM: 0.52s (72%)
└── Overhead: 0.04s (6%)
```

**Token Usage:**
```
Input Tokens: 375
Output Tokens: 150
Total: 525 tokens
Cost: $0.0001
```

**Success Rate:**
```
Successful: 95%
Errors: 5%
```

---

## 🚀 **Try It Now:**

### **1. Ask a Question:**
```
Open Streamlit app
Ask: "What is diabetes?"
```

### **2. View in LangSmith:**
```
Go to: https://smith.langchain.com/
Click: Projects → medical-chatbot
Click: Latest trace
Expand: All steps
```

### **3. What You'll See:**
- ✅ Full query
- ✅ Retrieved documents
- ✅ Context used
- ✅ LLM prompt
- ✅ Generated answer
- ✅ All timing
- ✅ All metadata

---

## 📝 **Summary:**

**Already Traced:**
- ✅ User queries
- ✅ Document retrieval
- ✅ Context formatting
- ✅ LLM generation
- ✅ Final answers
- ✅ All latencies
- ✅ All metadata

**How to View:**
- ✅ LangSmith dashboard
- ✅ Console logs
- ✅ Streamlit UI

**Your RAG pipeline is fully observable!** 🎉
