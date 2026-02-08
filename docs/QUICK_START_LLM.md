# 🎯 Quick Start: Switching LLMs

## ✅ What I've Created

1. **`config.yaml`** - Central configuration file for all LLMs
2. **`llm_factory.py`** - Dynamic LLM loader
3. **Updated `evaluate_rag.py`** - Now uses config instead of hardcoded Groq
4. **`LLM_CONFIG_GUIDE.md`** - Complete documentation

## 🚀 How to Switch LLMs

### Option 1: Use Groq (Current - Fast & Free)
```yaml
# config.yaml
active_llm: "groq"
evaluation_llm: "groq"
```
✅ Already configured!

### Option 2: Use Gemini (Recommended - Better Rate Limits)
```yaml
# config.yaml
active_llm: "gemini"
evaluation_llm: "gemini"
```

Then add to `.env`:
```bash
GOOGLE_API_KEY=your_key_here
```

Get key: https://aistudio.google.com/app/apikey

### Option 3: Use OpenAI (Paid - Best Quality)
```yaml
# config.yaml
active_llm: "openai"
evaluation_llm: "openai"
```

Then add to `.env`:
```bash
OPENAI_API_KEY=your_key_here
```

### Option 4: Mix and Match
```yaml
# Use Groq for fast generation
active_llm: "groq"

# Use Gemini for better evaluation (no rate limit issues)
evaluation_llm: "gemini"
```

## 📝 Steps to Change LLM

1. **Edit `config.yaml`**
   ```yaml
   active_llm: "gemini"  # Change this line
   evaluation_llm: "gemini"  # Change this line
   ```

2. **Add API key to `.env`**
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Run evaluation**
   ```bash
   python evaluate_rag.py
   ```

That's it! No code changes needed! 🎉

## 🔧 Test Your Configuration

```bash
python llm_factory.py
```

This shows:
- Which LLM is active
- Which LLM is used for evaluation
- All available LLMs
- If the LLM can be created successfully

## 💡 Recommended Setup to Fix Rate Limits

**Problem:** Groq has 6000 TPM limit → causes NaN metrics

**Solution:** Use Gemini for evaluation (15 RPM, 1M tokens/day)

```yaml
# config.yaml
active_llm: "groq"      # Keep Groq for fast generation
evaluation_llm: "gemini" # Switch to Gemini for evaluation
```

This gives you:
- ✅ Fast answer generation (Groq)
- ✅ No rate limit errors (Gemini)
- ✅ Complete evaluation metrics
- ✅ Still 100% free!

## 📚 Full Documentation

See `LLM_CONFIG_GUIDE.md` for:
- Detailed setup for each LLM
- API key instructions
- Troubleshooting
- Best practices
- Example configurations
