# Quick Start: RAG Evaluation

## Overview

This guide will help you quickly run evaluations on your Medical Chatbot RAG system.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Ensure Vector Store Exists

```bash
# If you haven't created the vector store yet:
uv run python create_memory_for_llm.py
```

### Step 2: Run Simple Evaluation

```bash
# Run the basic evaluation (no additional dependencies needed)
uv run python evaluate_simple.py
```

This will:
- Test your RAG system with 10 medical questions
- Generate answers and compare with expected results
- Create detailed reports in `evaluation/results/`

### Step 3: Review Results

Check the generated files in `evaluation/results/`:
- **`comparison_report_*.txt`** - Human-readable comparison of answers
- **`simple_results_*.csv`** - Statistics and metrics
- **`simple_results_*.json`** - Full detailed results

---

## 📊 Advanced Evaluation (Optional)

For comprehensive metrics using RAGAS framework:

### Install RAGAS

```bash
uv pip install ragas datasets pandas matplotlib seaborn
```

### Run Full Evaluation

```bash
# This may take several minutes
uv run python evaluate_rag.py
```

This provides:
- **Faithfulness**: How factually consistent answers are with context
- **Answer Relevancy**: How relevant answers are to questions
- **Context Precision**: How well relevant contexts are ranked
- **Context Recall**: How well all relevant info is retrieved

### Visualize Results

```bash
uv run python visualize_results.py
```

This creates plots in `evaluation/plots/`:
- Average metrics bar chart
- Distribution plots
- Performance heatmap
- Comparison charts

---

## 📝 Customizing Test Questions

Edit `evaluation/test_dataset.json`:

```json
[
  {
    "question": "Your medical question here",
    "ground_truth": "Expected answer based on your knowledge base"
  }
]
```

Then re-run the evaluation.

---

## 🔧 Tuning Your RAG System

Based on evaluation results, you can adjust:

### 1. Retrieval Parameters

In `main.py` or `evaluate_simple.py`:

```python
# Retrieve more contexts for complex questions
retriever = vectorstore.as_retriever(search_kwargs={'k': 5})  # Default: 3
```

### 2. LLM Parameters

```python
llm = ChatGroq(
    model=DEFAULT_MODEL,
    temperature=0.3,  # Lower = more focused, Higher = more creative
    max_tokens=400,   # Adjust answer length
)
```

### 3. Chunking Strategy

In `create_memory_for_llm.py`:

```python
CHUNK_SIZE = 400      # Smaller = more precise, Larger = more context
CHUNK_OVERLAP = 75    # More overlap = better context continuity
```

After changes, recreate the vector store:

```bash
uv run python create_memory_for_llm.py
```

---

## 📈 Interpreting Results

### Good Performance Indicators

- ✅ Answers match ground truth closely
- ✅ Relevant contexts are retrieved
- ✅ No hallucinations (making up information)
- ✅ System identifies when information is not available

### Signs You Need Improvement

- ❌ Answers don't address the question
- ❌ Retrieved contexts are irrelevant
- ❌ System makes up information not in context
- ❌ Missing important information from knowledge base

### What to Do

1. **If retrieval is poor**: Adjust chunk size, increase k parameter
2. **If answers are off-topic**: Lower temperature, improve prompt
3. **If information is missing**: Add more documents to knowledge base
4. **If answers are too long**: Reduce max_tokens, lower temperature

---

## 🎯 Evaluation Workflow

```
1. Create/Update Knowledge Base
   ↓
2. Create Vector Store
   ↓
3. Run Evaluation
   ↓
4. Review Results
   ↓
5. Identify Issues
   ↓
6. Make Improvements
   ↓
7. Re-evaluate
   ↓
8. Repeat until satisfied
```

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `evaluate_simple.py` | Basic evaluation without RAGAS |
| `evaluate_rag.py` | Full evaluation with RAGAS metrics |
| `visualize_results.py` | Create plots and charts |
| `evaluation/test_dataset.json` | Test questions and expected answers |
| `evaluation/results/` | Evaluation output files |
| `evaluation/plots/` | Visualization charts |

---

## 🆘 Troubleshooting

### "Vector store not found"
```bash
uv run python create_memory_for_llm.py
```

### "GROQ_API_KEY not found"
Check your `.env` file:
```
GROQ_API_KEY=your_key_here
```

### "No module named 'ragas'"
```bash
uv pip install ragas datasets pandas matplotlib seaborn
```

### Evaluation takes too long
- Use `evaluate_simple.py` instead of `evaluate_rag.py`
- Reduce number of test questions
- Use a faster model

---

## 💡 Tips

1. **Start Simple**: Use `evaluate_simple.py` first to get quick feedback
2. **Iterate Often**: Run evaluations after each change to track improvements
3. **Track Results**: Keep evaluation results to compare different configurations
4. **Focus on Failures**: Pay special attention to questions that fail
5. **Balance Metrics**: Don't optimize one metric at the expense of others

---

## 📖 Additional Resources

- **`EVALUATION_GUIDE.md`** - Detailed evaluation methodology
- **`EVALUATION_SUMMARY.md`** - Latest evaluation results and analysis
- **`README.md`** - Full project documentation

---

## ✅ Checklist

Before running evaluation:
- [ ] Vector store created (`vectorstore/db_faiss/` exists)
- [ ] Environment variables set (`.env` file with GROQ_API_KEY)
- [ ] Test dataset prepared (`evaluation/test_dataset.json`)
- [ ] Dependencies installed

After evaluation:
- [ ] Review comparison report
- [ ] Check CSV statistics
- [ ] Identify areas for improvement
- [ ] Plan next iteration

---

**Ready to evaluate? Run:**

```bash
uv run python evaluate_simple.py
```

**Good luck! 🚀**
