# ✅ Update Complete: evaluate_simple.py

## What Was Changed

Updated `evaluate_simple.py` to use the **config.yaml** system, just like `evaluate_rag.py`.

### Changes Made:

1. **Removed hardcoded Groq imports**
   ```python
   # ❌ Before
   from langchain_groq import ChatGroq
   ```

2. **Added config-based imports**
   ```python
   # ✅ After
   from llm_factory import load_config, get_generation_llm
   ```

3. **Updated constants to load from config**
   ```python
   # ❌ Before
   DB_FAISS_PATH = "vectorstore/db_faiss"
   DEFAULT_MODEL = "llama-3.1-8b-instant"
   
   # ✅ After
   CONFIG = load_config()
   DB_FAISS_PATH = CONFIG['vectorstore']['path']
   # Model comes from config.yaml
   ```

4. **Updated LLM initialization**
   ```python
   # ❌ Before
   groq_api_key = os.environ.get("GROQ_API_KEY")
   llm = ChatGroq(model=DEFAULT_MODEL, api_key=groq_api_key)
   
   # ✅ After
   active_llm = CONFIG.get('active_llm', 'groq')
   llm = get_generation_llm(CONFIG)
   ```

5. **Updated error messages**
   - Now mentions checking `config.yaml` instead of just `GROQ_API_KEY`

## ✅ Verification

Tested successfully! The script:
- ✅ Loads configuration from `config.yaml`
- ✅ Uses the active LLM (currently: `groq`)
- ✅ Generates answers successfully
- ✅ Saves results properly

## 🎯 How to Use

### Switch LLMs for evaluate_simple.py

Just edit `config.yaml`:

```yaml
# Use Groq (fast, free)
active_llm: "groq"

# Or use Gemini (better rate limits)
active_llm: "gemini"

# Or use OpenAI (best quality)
active_llm: "openai"
```

Then run:
```bash
python evaluate_simple.py
```

**No code changes needed!** The script automatically picks up the LLM from config.

## 📊 Both Scripts Now Use Config

| Script | Uses Config | Active LLM | Evaluation LLM |
|--------|-------------|------------|----------------|
| `evaluate_simple.py` | ✅ Yes | From `active_llm` | N/A (no RAGAS) |
| `evaluate_rag.py` | ✅ Yes | From `active_llm` | From `evaluation_llm` |

## 🎉 Benefits

1. **Centralized configuration** - One place to manage all LLMs
2. **Easy switching** - Change LLM without touching code
3. **Consistent** - Both evaluation scripts use the same system
4. **Flexible** - Can use different LLMs for different purposes
5. **No hardcoded values** - Everything comes from config

## 📝 Current Configuration

Your current setup (from `config.yaml`):
```yaml
active_llm: "groq"           # Used by both scripts for generation
evaluation_llm: "gemini"     # Used only by evaluate_rag.py for RAGAS
```

This means:
- `evaluate_simple.py` uses **Groq** for answer generation
- `evaluate_rag.py` uses **Groq** for answer generation + **Gemini** for evaluation

Perfect setup to avoid rate limits! 🚀
