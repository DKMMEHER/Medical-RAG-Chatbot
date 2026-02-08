# 📖 Evaluation Commands Explained

**Date:** 2026-02-03

---

## 🎯 **How the Commands Work:**

### **Command 1: Create Dataset**
```powershell
python evaluate_chatbot.py --create-dataset
```

**What it does (step-by-step):**

1. **Loads test examples** (8 medical questions)
   ```python
   MEDICAL_TEST_EXAMPLES = [
       {"inputs": {"query": "What is diabetes?"}, ...},
       {"inputs": {"query": "What are symptoms?"}, ...},
       # ... 6 more examples
   ]
   ```

2. **Connects to LangSmith**
   - Uses `LANGSMITH_API_KEY` from `.env`
   - Creates LangSmith client

3. **Creates dataset**
   ```python
   dataset = client.create_dataset(
       dataset_name="medical-chatbot-test",
       description="Test dataset for Medical Chatbot"
   )
   ```

4. **Uploads examples**
   ```python
   for example in MEDICAL_TEST_EXAMPLES:
       client.create_example(
           dataset_id=dataset.id,
           inputs=example["inputs"],
           outputs=example["outputs"]
       )
   ```

5. **Returns success**
   - Dataset is now stored in LangSmith cloud
   - Can be viewed at: https://smith.langchain.com/

**Purpose:** One-time setup to create test data

---

### **Command 2: Run Evaluation**
```powershell
python evaluate_chatbot.py --run-eval
```

**What it does (step-by-step):**

1. **Initializes RAG chain**
   ```python
   # Load components
   vectorstore = get_vectorstore()  # Load FAISS
   llm = initialize_llm(config)     # Load Gemini/Groq/etc
   prompt = get_rag_prompt()        # Load prompt template
   
   # Create chain
   rag_chain = (
       {"context": retriever, "question": RunnablePassthrough()}
       | prompt
       | llm
       | StrOutputParser()
   )
   ```

2. **Fetches test dataset from LangSmith**
   ```python
   # Gets the 8 test examples you created
   dataset = client.read_dataset(dataset_name="medical-chatbot-test")
   ```

3. **Runs each test query**
   ```python
   for example in dataset:
       query = example.inputs["query"]
       result = rag_chain.invoke(query)  # Run through your RAG
   ```

4. **Applies evaluators**
   ```python
   # For each result, check:
   - answer_relevance: Is answer substantial?
   - keyword_presence: Are expected keywords found?
   - response_length: Is answer appropriately sized?
   - no_error: Did it work without errors?
   ```

5. **Uploads results to LangSmith**
   ```python
   # Results include:
   - Each query
   - Generated answer
   - Scores for each metric
   - Timestamp, model used, etc.
   ```

6. **Saves CSV locally**
   ```python
   # Saves to: evaluation/results/eval_*.csv
   ```

**Purpose:** Test your RAG system and measure performance

---

## ❌ **Why It's Failing:**

### **Error:**
```
LangSmith not enabled, cannot create dataset
```

### **Root Cause:**
The `is_langsmith_enabled()` function checks for:
```python
os.environ.get("LANGCHAIN_TRACING_V2") == "true"
AND
os.environ.get("LANGCHAIN_API_KEY") is not None
```

But your `.env` has:
```bash
LANGSMITH_API_KEY=lsv2_...  # ✅ Correct
LANGCHAIN_TRACING_V2=true   # ❓ Maybe missing?
```

---

## ✅ **The Fix:**

### **Option 1: Check Your `.env` File**

Make sure you have BOTH:
```bash
# .env
LANGSMITH_API_KEY=lsv2_xxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_xxxxxxxxxxxxxxxxxxxxx  # Same as LANGSMITH_API_KEY
LANGCHAIN_PROJECT=medical-chatbot
```

**Note:** LangChain uses `LANGCHAIN_API_KEY`, LangSmith uses `LANGSMITH_API_KEY`. They should be the same!

---

### **Option 2: I Fixed the Script**

I updated `evaluate_chatbot.py` to:
1. ✅ Configure LangSmith at startup
2. ✅ Show clear error messages
3. ✅ Check if API key is set

**Try again:**
```powershell
python evaluate_chatbot.py --create-dataset
```

---

## 🔍 **How to Debug:**

### **Check if LangSmith is configured:**
```python
# In Python console
import os
print("LANGSMITH_API_KEY:", os.getenv("LANGSMITH_API_KEY"))
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
```

**Expected output:**
```
LANGSMITH_API_KEY: lsv2_xxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_API_KEY: lsv2_xxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_TRACING_V2: true
```

---

## 📊 **Complete Flow Diagram:**

```
┌─────────────────────────────────────────┐
│  python evaluate_chatbot.py             │
│  --create-dataset                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  1. Load 8 test examples                │
│     - Medical questions                 │
│     - Expected keywords                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  2. Connect to LangSmith                │
│     - Use LANGSMITH_API_KEY             │
│     - Create client                     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  3. Create dataset in cloud             │
│     - Name: medical-chatbot-test        │
│     - Upload 8 examples                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  ✅ Dataset created!                    │
│  View at: https://smith.langchain.com/  │
└─────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────┐
│  python evaluate_chatbot.py             │
│  --run-eval                             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  1. Initialize RAG chain                │
│     - Load vectorstore (FAISS)          │
│     - Load LLM (Gemini/Groq)            │
│     - Create chain                      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  2. Fetch test dataset                  │
│     - Get 8 examples from LangSmith     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  3. Run each query (8 times)            │
│     - Query → RAG chain → Answer        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  4. Apply evaluators (4 per query)      │
│     - Answer relevance                  │
│     - Keyword presence                  │
│     - Response length                   │
│     - No errors                         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  5. Upload results to LangSmith         │
│     - 8 queries × 4 metrics = 32 scores │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  6. Save CSV locally                    │
│     - evaluation/results/eval_*.csv     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  ✅ Evaluation complete!                │
│  View results in LangSmith dashboard    │
└─────────────────────────────────────────┘
```

---

## 🎯 **Summary:**

**`--create-dataset`:**
- Creates test data in LangSmith cloud
- One-time setup
- 8 medical questions

**`--run-eval`:**
- Tests your RAG chain
- Runs 8 queries
- Measures 4 metrics per query
- Uploads results to LangSmith

**Both need:**
- ✅ `LANGSMITH_API_KEY` in `.env`
- ✅ `LANGCHAIN_TRACING_V2=true` in `.env`
- ✅ `LANGCHAIN_API_KEY` in `.env` (same as LANGSMITH)

**Try again now!** 🚀
