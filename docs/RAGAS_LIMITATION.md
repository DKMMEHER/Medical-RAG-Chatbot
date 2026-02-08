# ⚠️ Important: RAGAS Evaluation LLM Limitation

## Current Situation

**RAGAS v0.4.3 only supports OpenAI for evaluation metrics.**

### What This Means:

1. **Answer Generation**: Can use ANY LLM (Groq, Gemini, OpenAI, etc.) ✅
2. **RAGAS Evaluation**: **Must use OpenAI** ⚠️

### Your Options:

#### Option 1: Use OpenAI for Evaluation (Recommended)

**Config:**
```yaml
active_llm: "groq"      # Free - for answer generation
evaluation_llm: "openai" # Paid - for RAGAS evaluation
```

**Cost:** ~$0.01-0.05 per evaluation run (very cheap with gpt-4o-mini)

**Setup:**
1. Get OpenAI API key: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   ```

#### Option 2: Skip RAGAS Evaluation

Use `evaluate_simple.py` instead:
```bash
python evaluate_simple.py
```

This script:
- ✅ Uses your configured LLM (Groq, Gemini, etc.)
- ✅ Generates answers
- ✅ Saves detailed comparison reports
- ❌ No RAGAS metrics (faithfulness, relevancy, etc.)

#### Option 3: Accept Default Behavior

Keep current config and RAGAS will try to use OpenAI by default:
```yaml
evaluation_llm: "groq"  # Will show warnings
```

You'll see warnings but it might work with OpenAI if `OPENAI_API_KEY` is set.

---

## Why This Limitation?

RAGAS 0.4.3 was built primarily for OpenAI and doesn't have proper abstraction for other LLM providers. The newer RAGAS versions (v1.0+) will have better support, but they're still in development.

## Recommended Setup

### For Development/Testing:
```yaml
active_llm: "groq"           # Free, fast
evaluation_llm: "groq"       # Use evaluate_simple.py instead
```
Run: `python evaluate_simple.py`

### For Production/Serious Evaluation:
```yaml
active_llm: "groq"           # Free, fast  
evaluation_llm: "openai"     # Paid, but cheap and reliable
```
Run: `python evaluate_rag.py`

---

## Summary Table

| Script | Answer LLM | Evaluation LLM | Cost | RAGAS Metrics |
|--------|------------|----------------|------|---------------|
| `evaluate_simple.py` | Any (from config) | N/A | Free | ❌ No |
| `evaluate_rag.py` | Any (from config) | OpenAI only | ~$0.01-0.05 | ✅ Yes |

---

## Next Steps

1. **If you want RAGAS metrics**: Set `evaluation_llm: "openai"` and add `OPENAI_API_KEY`
2. **If you want free evaluation**: Use `evaluate_simple.py` instead
3. **Current setup works for**: Answer generation with any LLM ✅
