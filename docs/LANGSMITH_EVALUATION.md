# 🧪 LangSmith Evaluation Guide

**Date:** 2026-02-03  
**Status:** ✅ Fully Implemented

---

## 📊 **What's Implemented:**

### **✅ 1. Tracing & Observability** (Already Working)
- Real-time trace logging
- LLM call monitoring
- Error tracking
- Latency measurement
- View at: https://smith.langchain.com/

### **✅ 2. Evaluation System** (NEW!)
- Test dataset creation
- Automated evaluation
- Custom evaluators
- Performance metrics
- Result reporting

---

## 🎯 **Evaluation Features:**

### **Test Dataset:**
- **8 test examples** covering:
  - Medical definitions (diabetes)
  - Symptoms & treatment
  - Policy queries
  - Personal data retrieval
  - Complex reasoning

### **Custom Evaluators:**
1. ✅ **Answer Relevance** - Checks if answer is substantial
2. ✅ **Keyword Presence** - Verifies expected keywords appear
3. ✅ **Response Length** - Ensures appropriate answer length
4. ✅ **No Errors** - Confirms successful execution

---

## 🚀 **How to Use:**

### **Step 1: Create Test Dataset**

```powershell
# Create dataset in LangSmith
python evaluate_chatbot.py --create-dataset
```

**What this does:**
- Creates dataset named `medical-chatbot-test`
- Adds 8 test examples
- Uploads to LangSmith

**Output:**
```
📊 Creating dataset: medical-chatbot-test
✅ Dataset created successfully
📝 Total examples: 8
```

---

### **Step 2: Run Evaluation**

```powershell
# Run evaluation on your RAG chain
python evaluate_chatbot.py --run-eval
```

**What this does:**
- Loads your RAG chain
- Runs all 8 test queries
- Applies 4 evaluators to each
- Saves results to CSV
- Uploads to LangSmith

**Output:**
```
🔬 Starting evaluation: medical_eval_groq
📊 Dataset: medical-chatbot-test
✅ Evaluation completed successfully
📊 View results at: https://smith.langchain.com/
```

---

### **Step 3: View Results**

**Option 1: LangSmith Dashboard** (Recommended)
1. Go to: https://smith.langchain.com/
2. Navigate to your project: `medical-chatbot`
3. Click on "Datasets" tab
4. View evaluation results

**Option 2: Local CSV File**
```powershell
# Results saved to:
evaluation/results/eval_medical_eval_groq_YYYYMMDD_HHMMSS.csv
```

---

## 📊 **Evaluation Metrics:**

### **1. Answer Relevance**
- **Score:** 0.0 or 1.0
- **Criteria:** Answer > 20 characters
- **Purpose:** Ensure non-empty responses

### **2. Keyword Presence**
- **Score:** 0.0 to 1.0 (percentage)
- **Criteria:** Expected keywords found / total keywords
- **Purpose:** Verify answer contains relevant terms

### **3. Response Length**
- **Score:** 0.3, 0.7, or 1.0
- **Criteria:** 
  - 1.0: 20-500 words (good)
  - 0.7: >500 words (too long)
  - 0.3: <20 words (too short)
- **Purpose:** Ensure appropriate answer length

### **4. No Errors**
- **Score:** 0.0 or 1.0
- **Criteria:** Run completed without errors
- **Purpose:** Track system reliability

---

## 🧪 **Test Examples:**

### **Easy (Factual):**
```
Query: "What is diabetes?"
Expected Keywords: ["blood sugar", "glucose", "insulin", "chronic"]
```

### **Medium (Retrieval):**
```
Query: "Tell me about policy number 146382023"
Expected Keywords: ["policy", "insurance", "coverage"]
```

### **Hard (Reasoning):**
```
Query: "What is the relationship between diabetes and heart disease?"
Expected Keywords: ["diabetes", "heart", "cardiovascular", "risk"]
```

---

## 📈 **Comparing LLM Performance:**

### **Test Different Models:**

```powershell
# Test with Groq
# Edit config.yaml: active_llm: "groq"
python evaluate_chatbot.py --run-eval

# Test with Gemini
# Edit config.yaml: active_llm: "gemini"
python evaluate_chatbot.py --run-eval

# Test with Claude
# Edit config.yaml: active_llm: "claude"
python evaluate_chatbot.py --run-eval
```

**Compare results in LangSmith dashboard!**

---

## 🎯 **Advanced Usage:**

### **Custom Dataset Name:**
```powershell
python evaluate_chatbot.py --create-dataset --dataset-name my-custom-test
python evaluate_chatbot.py --run-eval --dataset-name my-custom-test
```

### **Add More Test Cases:**

Edit `evaluate_chatbot.py`:
```python
MEDICAL_TEST_EXAMPLES = [
    # Add your custom test cases here
    {
        "inputs": {"query": "Your question here"},
        "outputs": {
            "expected_keywords": ["keyword1", "keyword2"],
            "category": "your_category"
        },
        "metadata": {"difficulty": "medium", "type": "factual"}
    },
]
```

---

## 📊 **Example Results:**

```
=============================================================
EVALUATION RESULTS
=============================================================
Experiment: medical_eval_groq_20260203_095441

Total examples: 8

Metric Summaries:
  answer_relevance: 1.000
  keyword_presence: 0.750
  response_length: 0.950
  no_error: 1.000

💾 Results saved to: evaluation/results/eval_medical_eval_groq_20260203_095441.csv
=============================================================
```

---

## 🔍 **What Each Score Means:**

| Metric | Score | Interpretation |
|--------|-------|----------------|
| **answer_relevance** | 1.0 | ✅ All answers substantial |
| **keyword_presence** | 0.75 | ⚠️ 75% of keywords found |
| **response_length** | 0.95 | ✅ Good answer lengths |
| **no_error** | 1.0 | ✅ No system errors |

**Overall:** Good performance, but some keywords missing

---

## 💡 **Best Practices:**

### **1. Run Evaluation Regularly:**
```powershell
# After code changes
python evaluate_chatbot.py --run-eval

# After updating documents
python evaluate_chatbot.py --run-eval

# When switching LLMs
python evaluate_chatbot.py --run-eval
```

### **2. Track Performance Over Time:**
- Compare evaluation runs in LangSmith
- Monitor metric trends
- Identify regressions

### **3. Use for A/B Testing:**
```powershell
# Test Groq
active_llm: "groq"
python evaluate_chatbot.py --run-eval

# Test Gemini
active_llm: "gemini"
python evaluate_chatbot.py --run-eval

# Compare results!
```

---

## 🚨 **Troubleshooting:**

### **Issue: "LangSmith not enabled"**
**Solution:** Check `.env` file has `LANGSMITH_API_KEY`

### **Issue: "Dataset not found"**
**Solution:** Run `--create-dataset` first

### **Issue: "Evaluation failed"**
**Solution:** 
1. Check vector store exists
2. Verify LLM API key is valid
3. Check logs for specific error

---

## 📝 **Files Created:**

```
Medical-chatbot/
├── evaluate_chatbot.py          # Main evaluation script ✅
├── src/observability/
│   └── evaluation.py             # Evaluation utilities ✅
└── evaluation/
    └── results/
        └── eval_*.csv            # Evaluation results
```

---

## 🎉 **Summary:**

**You now have:**
- ✅ **Test dataset** with 8 medical queries
- ✅ **4 custom evaluators** for quality metrics
- ✅ **Automated evaluation** script
- ✅ **LangSmith integration** for tracking
- ✅ **CSV export** for local analysis

**To get started:**
```powershell
# 1. Create dataset
python evaluate_chatbot.py --create-dataset

# 2. Run evaluation
python evaluate_chatbot.py --run-eval

# 3. View results
# Go to: https://smith.langchain.com/
```

**Your Medical Chatbot now has enterprise-grade evaluation!** 🚀
