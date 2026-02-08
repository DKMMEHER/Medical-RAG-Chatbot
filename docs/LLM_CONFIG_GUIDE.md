# LLM Configuration Guide

This guide explains how to use the `config.yaml` file to switch between different LLM providers for your RAG Medical Chatbot.

## Quick Start

### 1. Choose Your LLM

Edit `config.yaml` and set the `active_llm` and `evaluation_llm`:

```yaml
# For answer generation
active_llm: "groq"

# For RAGAS evaluation
evaluation_llm: "groq"
```

### 2. Set API Keys

Add the required API key to your `.env` file or environment variables:

```bash
# For Groq
GROQ_API_KEY=your_groq_api_key_here

# For Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# For HuggingFace
HUGGINGFACE_API_KEY=your_huggingface_token_here

# Ollama doesn't need an API key (runs locally)
```

### 3. Run Evaluation

```bash
python evaluate_rag.py
```

## Available LLMs

### 1. **Groq** (Default - Fast & Free)
```yaml
active_llm: "groq"
evaluation_llm: "groq"
```
- **Model:** llama-3.1-8b-instant
- **Free Tier:** 6,000 tokens/minute
- **Best for:** Fast inference
- **Get API Key:** https://console.groq.com/keys

### 2. **Google Gemini** (Recommended for Evaluation)
```yaml
active_llm: "gemini"
evaluation_llm: "gemini"
```
- **Model:** gemini-1.5-flash
- **Free Tier:** 15 requests/minute, 1M tokens/day
- **Best for:** Better rate limits, good for evaluation
- **Get API Key:** https://aistudio.google.com/app/apikey

### 3. **OpenAI** (Paid - High Quality)
```yaml
active_llm: "openai"
evaluation_llm: "openai"
```
- **Model:** gpt-4o-mini
- **Cost:** $0.15/1M input tokens, $0.60/1M output tokens
- **Best for:** Highest quality responses
- **Get API Key:** https://platform.openai.com/api-keys

### 4. **HuggingFace** (Free)
```yaml
active_llm: "huggingface"
evaluation_llm: "huggingface"
```
- **Model:** meta-llama/Meta-Llama-3-8B-Instruct
- **Free Tier:** Rate limited
- **Best for:** Open source models
- **Get API Key:** https://huggingface.co/settings/tokens

### 5. **Ollama** (100% Free - Local)
```yaml
active_llm: "ollama"
evaluation_llm: "ollama"
```
- **Model:** llama3.1
- **Cost:** Free (runs on your machine)
- **Best for:** No rate limits, complete privacy
- **Setup:** Install Ollama from https://ollama.ai

## Mix and Match

You can use different LLMs for generation and evaluation:

```yaml
# Use Groq for fast answer generation
active_llm: "groq"

# Use Gemini for better evaluation (higher rate limits)
evaluation_llm: "gemini"
```

## Customizing LLM Settings

Edit the LLM configuration in `config.yaml`:

```yaml
llms:
  groq:
    provider: "groq"
    model: "llama-3.1-8b-instant"  # Change model
    temperature: 0.7               # Adjust creativity (0.0-1.0)
    max_tokens: 1024              # Change max response length
    api_key_env: "GROQ_API_KEY"
```

## Troubleshooting

### Rate Limit Errors
If you see `RateLimitError`:
1. Switch to Gemini (better free tier)
2. Reduce test dataset size
3. Upgrade to paid tier

### API Key Not Found
```
ValueError: API key not found. Please set GROQ_API_KEY environment variable.
```
**Solution:** Add the API key to your `.env` file

### Import Errors
```
ModuleNotFoundError: No module named 'langchain_google_genai'
```
**Solution:** Install the required package:
```bash
pip install langchain-google-genai
```

## Testing the Configuration

Test if your LLM configuration works:

```bash
python llm_factory.py
```

This will show:
- Active LLM
- Evaluation LLM
- Available LLMs
- Whether the LLM can be created successfully

## Best Practices

1. **For Development:** Use Groq or Ollama (free, fast)
2. **For Evaluation:** Use Gemini (better rate limits)
3. **For Production:** Use OpenAI or Gemini (reliable, high quality)
4. **For Privacy:** Use Ollama (local, no data sent to cloud)

## Example Configurations

### Budget-Friendly Setup
```yaml
active_llm: "groq"
evaluation_llm: "gemini"
```

### High-Quality Setup
```yaml
active_llm: "openai"
evaluation_llm: "openai"
```

### Privacy-First Setup
```yaml
active_llm: "ollama"
evaluation_llm: "ollama"
```

### Hybrid Setup
```yaml
active_llm: "groq"      # Fast generation
evaluation_llm: "gemini" # Better evaluation limits
```
