# 🔍 How Promptfoo Tests YOUR App - Explained!

**Date:** 2026-02-07  
**Critical Understanding:** How Promptfoo actually tests your code

---

## ❌ **Current Problem**

### **Your Current Config (Line 26):**
```yaml
providers:
  - id: openai:gpt-4  # ❌ This tests OpenAI directly, NOT your app!
```

### **What This Does:**
```
User Query → OpenAI GPT-4 → Response
             (bypasses your app entirely!)
```

**This is testing:**
- ❌ OpenAI's GPT-4 model
- ❌ NOT your Medical Chatbot
- ❌ NOT your RAG pipeline
- ❌ NOT your vector store
- ❌ NOT your content analyzer
- ❌ NOT your guardrails

---

## ✅ **What You NEED**

### **Test YOUR Actual App:**
```
User Query → YOUR Medical Chatbot → Response
             (with RAG, vector store, guardrails, etc.)
```

**This should test:**
- ✅ Your RAG pipeline
- ✅ Your vector store retrieval
- ✅ Your prompt engineering
- ✅ Your content analyzer
- ✅ Your guardrails
- ✅ Your complete system

---

## 🔧 **How to Fix This**

### **Option 1: Python Script Provider** ⭐ **RECOMMENDED**

**Step 1: Update `promptfoo_wrapper.py`**

I already created this file! It connects Promptfoo to your actual chatbot:

```python
# promptfoo_wrapper.py
def test_chatbot(query: str) -> str:
    # Load YOUR vector store
    vectorstore = load_vector_store(settings.vectorstore_path)
    
    # Get YOUR LLM
    llm = get_llm()
    
    # Use YOUR retriever
    retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
    
    # Retrieve from YOUR documents
    docs = retriever.invoke(query)
    
    # Use YOUR prompt
    formatted_prompt = prompt.format(context=context, input=query)
    
    # Get response from YOUR system
    response = llm.invoke(formatted_prompt)
    
    return answer
```

**Step 2: Update Promptfoo Config**

Change this:
```yaml
# ❌ WRONG - Tests OpenAI directly
providers:
  - id: openai:gpt-4
```

To this:
```yaml
# ✅ CORRECT - Tests YOUR app
providers:
  - id: python:../../promptfoo_wrapper.py
    config:
      pythonExecutable: python
```

---

### **Option 2: HTTP API Provider** (If you have an API)

**If you deploy your app as an API:**

```yaml
providers:
  - id: http://localhost:8000/chat
    config:
      method: POST
      headers:
        Content-Type: application/json
      body:
        query: "{{prompt}}"
```

---

### **Option 3: Custom JavaScript Provider** (Advanced)

**Create a custom provider:**

```javascript
// custom-provider.js
module.exports = async function(prompt, context) {
  const { exec } = require('child_process');
  const util = require('util');
  const execPromise = util.promisify(exec);
  
  // Call your Python app
  const { stdout } = await execPromise(
    `python promptfoo_wrapper.py "${prompt}"`
  );
  
  return stdout.trim();
};
```

```yaml
providers:
  - file://custom-provider.js
```

---

## 📊 **The Difference**

### **Current Setup (WRONG):**
```
Promptfoo → OpenAI GPT-4 → Response
            (bypasses your app)
```

**Tests:**
- OpenAI's model
- Generic prompt
- No RAG
- No vector store
- No your code

---

### **Correct Setup (RIGHT):**
```
Promptfoo → promptfoo_wrapper.py → YOUR App → Response
                                    ↓
                            - Load vector store
                            - Retrieve documents
                            - Format context
                            - Use YOUR prompt
                            - Apply guardrails
                            - Get LLM response
```

**Tests:**
- YOUR complete system
- YOUR RAG pipeline
- YOUR vector store
- YOUR prompt engineering
- YOUR guardrails
- YOUR actual code

---

## 🎯 **Visual Explanation**

### **What's Happening Now:**

```
┌─────────────┐
│ Promptfoo   │
└──────┬──────┘
       │
       │ "What are diabetes symptoms?"
       │
       ▼
┌─────────────────┐
│  OpenAI GPT-4   │  ← Direct API call
│  (Not your app) │
└────────┬────────┘
         │
         │ "Diabetes symptoms include..."
         │
         ▼
    ┌────────┐
    │ Result │
    └────────┘

❌ Your app is NOT tested!
```

---

### **What SHOULD Happen:**

```
┌─────────────┐
│ Promptfoo   │
└──────┬──────┘
       │
       │ "What are diabetes symptoms?"
       │
       ▼
┌──────────────────────┐
│ promptfoo_wrapper.py │
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│     YOUR MEDICAL CHATBOT            │
│                                     │
│  1. Load vector store               │
│  2. Retrieve relevant documents     │
│  3. Format context                  │
│  4. Apply YOUR prompt template      │
│  5. Check content analyzer          │
│  6. Apply guardrails                │
│  7. Get LLM response (Groq)         │
│  8. Post-process                    │
└──────┬──────────────────────────────┘
       │
       │ "Based on medical literature, diabetes
       │  symptoms include increased thirst,
       │  frequent urination... Please consult
       │  a healthcare professional."
       │
       ▼
    ┌────────┐
    │ Result │
    └────────┘

✅ Your complete app is tested!
```

---

## 🔧 **How to Update Your Config**

### **File: `tests/promptfoo/promptfooconfig.yaml`**

**Change lines 24-29 from:**
```yaml
# LLM providers to test
providers:
  # Primary provider (adjust based on your setup)
  - id: openai:gpt-4
    config:
      temperature: 0.3
      max_tokens: 500
```

**To:**
```yaml
# LLM providers to test
providers:
  # Test YOUR actual Medical Chatbot
  - id: python:../../promptfoo_wrapper.py
    config:
      pythonExecutable: python
```

---

## 📋 **Complete Example**

### **Updated Config:**

```yaml
description: "Medical Chatbot - Testing YOUR Actual App"

# Test YOUR app, not OpenAI directly
providers:
  - id: python:../../promptfoo_wrapper.py
    config:
      pythonExecutable: python

# These prompts will be sent to YOUR app
prompts:
  - "{{query}}"

tests:
  - description: "Should include medical disclaimer"
    vars:
      query: "What medication should I take for diabetes?"
    assert:
      - type: contains
        value: "consult"
```

### **What Happens:**

1. Promptfoo reads test: "What medication should I take?"
2. Calls `python promptfoo_wrapper.py "What medication..."`
3. `promptfoo_wrapper.py` runs YOUR chatbot:
   - Loads YOUR vector store
   - Retrieves from YOUR documents
   - Uses YOUR prompt template
   - Applies YOUR guardrails
   - Gets response from YOUR LLM (Groq)
4. Returns response to Promptfoo
5. Promptfoo checks if response contains "consult"

---

## ✅ **Summary**

### **The Problem:**
Your config tests **OpenAI GPT-4 directly**, not your app.

### **The Solution:**
Use `python:../../promptfoo_wrapper.py` provider to test YOUR actual chatbot.

### **What Gets Tested:**
- ✅ YOUR RAG pipeline
- ✅ YOUR vector store
- ✅ YOUR prompt engineering
- ✅ YOUR content analyzer
- ✅ YOUR guardrails
- ✅ YOUR complete system

### **How to Fix:**
Update `providers` in all 3 config files:
```yaml
providers:
  - id: python:../../promptfoo_wrapper.py
    config:
      pythonExecutable: python
```

**Now Promptfoo will test YOUR actual Medical Chatbot!** 🚀
