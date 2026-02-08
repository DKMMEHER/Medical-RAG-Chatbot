# 🤖 Valid Gemini Model Names

**Date:** 2026-02-03  
**Purpose:** Reference for correct Gemini model identifiers

---

## ✅ **Valid Gemini Models (As of 2026):**

### **Gemini 1.5 Family** (Current, Recommended)

| Model ID | Use This Exact String | Description |
|----------|----------------------|-------------|
| **Gemini 1.5 Flash** | `gemini-1.5-flash` | ⚡ Fast, free tier (15 RPM) |
| **Gemini 1.5 Pro** | `gemini-1.5-pro` | 💎 Best quality, free tier (2 RPM) |

### **Gemini 1.0 Family** (Legacy)

| Model ID | Use This Exact String | Description |
|----------|----------------------|-------------|
| **Gemini 1.0 Pro** | `gemini-1.0-pro` | Older version |
| **Gemini Pro** | `gemini-pro` | Legacy name (same as 1.0) |

---

## ❌ **Invalid Model Names (Don't Use):**

| What You Might Try | Why It's Wrong | Use This Instead |
|-------------------|----------------|------------------|
| `Gemini 3 Pro` | ❌ Spaces, wrong caps, doesn't exist | `gemini-1.5-pro` |
| `gemini-2.0-flash-exp` | ❌ Experimental, not available | `gemini-1.5-flash` |
| `Gemini 1.5 Flash` | ❌ Has spaces, wrong caps | `gemini-1.5-flash` |
| `gemini_1_5_flash` | ❌ Wrong separators | `gemini-1.5-flash` |
| `gemini-flash` | ❌ Missing version | `gemini-1.5-flash` |

---

## 📋 **Naming Rules:**

1. ✅ **All lowercase** - No capital letters
2. ✅ **Use hyphens** - Not spaces or underscores
3. ✅ **Include version** - e.g., `1.5` or `1.0`
4. ✅ **Exact match** - Must match Google's API exactly

---

## 🎯 **Recommended for Your Project:**

### **For Speed (Recommended):**
```yaml
gemini:
  model: "gemini-1.5-flash"  # ✅ Fast, 15 RPM free
```

### **For Quality:**
```yaml
gemini:
  model: "gemini-1.5-pro"  # ✅ Best quality, 2 RPM free
```

---

## 🔍 **How to Find Valid Models:**

### **Method 1: Google AI Studio**
1. Go to: https://aistudio.google.com/
2. Click on "Models"
3. See list of available models

### **Method 2: API Call**
```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")

for model in genai.list_models():
    print(model.name)
```

### **Method 3: LangChain Docs**
https://python.langchain.com/docs/integrations/chat/google_generative_ai

---

## 📊 **Comparison:**

| Model | Speed | Quality | Free Tier | Best For |
|-------|-------|---------|-----------|----------|
| `gemini-1.5-flash` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 15 RPM | Daily use |
| `gemini-1.5-pro` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 2 RPM | Best quality |
| `gemini-1.0-pro` | ⚡⚡ | ⭐⭐⭐ | 60 RPM | Legacy apps |

---

## ✅ **Current Config (Fixed):**

```yaml
gemini:
  provider: "google"
  model: "gemini-1.5-flash"  # ✅ Correct!
  temperature: 0.5
  max_tokens: 512
  api_key_env: "GEMINI_API_KEY"
```

---

## 🚀 **Test It:**

```powershell
python evaluate_chatbot.py --run-eval
```

**Should work now!** ✅
