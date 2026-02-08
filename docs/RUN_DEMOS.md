# ✅ Files Ready to Run from Root Directory

## 📁 Current Structure

```
Medical-chatbot/
├── Content_Analyzer/          # Module folder
│   ├── __init__.py
│   ├── config.py
│   ├── pii_detector.py
│   ├── toxic_detector.py
│   ├── validator.py
│   ├── utils.py
│   ├── demo.py
│   └── ... (other files)
│
├── output_guardrails.py       # ✅ Standalone demo (root)
├── example_complete_pipeline.py  # ✅ Complete 3-layer demo (root)
└── ... (other project files)
```

---

## 🚀 How to Run

### **1. Output Guardrails Demo**

Tests LLM output validation with 4 test cases:

```bash
# From project root
uv run output_guardrails.py
```

**What it tests:**
- ✅ Clean medical response
- ❌ Response with PII leakage (SSN)
- ⚠️  Medical advice without disclaimer
- ⚠️  Overconfident response (hallucination risk)

---

### **2. Complete 3-Layer Pipeline Demo**

Demonstrates the full validation pipeline:

```bash
# From project root
uv run example_complete_pipeline.py
```

**What it demonstrates:**
- **Layer 1:** Input validation (user query)
- **Layer 2:** Context validation (retrieved documents)
- **Layer 3:** Output validation (LLM responses) ⭐

Shows 4 different LLM responses and how guardrails handle each.

---

## 📊 What Each Demo Shows

### **output_guardrails.py**
```
================================================================================
OUTPUT GUARDRAILS TEST
================================================================================

Test 1: Clean medical response
--------------------------------------------------------------------------------
Output: Diabetes is managed through diet, exercise, and medication...
✅ No issues found
Safe to show: YES ✓

Test 2: Response with PII leakage
--------------------------------------------------------------------------------
Output: Patient John Doe (SSN: 123-45-6789) should take insulin...
❌ Issues found: 1
  - PII_SSN (CRITICAL)
Safe to show: NO ✗
Fallback: I apologize, but I cannot provide that response...

... (and 2 more tests)
```

### **example_complete_pipeline.py**
```
================================================================================
COMPLETE RAG PIPELINE WITH GUARDRAILS
================================================================================

🔒 LAYER 1: INPUT VALIDATION
User Query: What are the symptoms of diabetes?
✅ Query is safe to process

🔒 LAYER 2: CONTEXT VALIDATION
Retrieved 5 documents from vector store
  ✅ Doc 1: Safe
  ❌ Doc 2: BLOCKED (1 issue(s)) - PII_SSN
  ✅ Doc 3: Safe
  ❌ Doc 4: BLOCKED (1 issue(s)) - PII_EMAIL
  ✅ Doc 5: Safe
✅ 3/5 documents safe to send to LLM

🤖 CALLING LLM...

🔒 LAYER 3: OUTPUT VALIDATION
... (tests 4 different LLM responses)
```

---

## ✨ Key Features Demonstrated

| Feature | output_guardrails.py | example_complete_pipeline.py |
|---------|---------------------|------------------------------|
| **PII Detection** | ✅ | ✅ |
| **Toxic Content** | ✅ | ✅ |
| **Hallucination Detection** | ✅ | ✅ |
| **Medical Disclaimers** | ✅ | ✅ |
| **Fallback Responses** | ✅ | ✅ |
| **3-Layer Pipeline** | ❌ | ✅ |
| **Context Validation** | ❌ | ✅ |

---

## 🎯 Quick Reference

### **To test output guardrails only:**
```bash
uv run output_guardrails.py
```

### **To see complete 3-layer validation:**
```bash
uv run example_complete_pipeline.py
```

### **To use in your code:**
```python
from Content_Analyzer import ContentValidator
from output_guardrails import OutputGuardrails

# Initialize
input_validator = ContentValidator()
output_guardrails = OutputGuardrails()

# Validate LLM output
is_safe, issues, safe_output = output_guardrails.validate_output(
    llm_response,
    original_query=user_query,
    retrieved_context=safe_docs
)

if is_safe:
    print(safe_output)  # Safe to show
else:
    print(output_guardrails.get_fallback_response("safety"))
```

---

## 📝 Notes

- Both files are configured to run from the **project root** directory
- They use `Content_Analyzer` as a package import
- `output_guardrails.py` is also available inside `Content_Analyzer/` folder
- The demos are **interactive** and show detailed output

---

**Ready to test! Run either demo to see output guardrails in action.** 🚀
