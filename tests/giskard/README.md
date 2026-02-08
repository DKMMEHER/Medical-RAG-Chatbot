# 🛡️ Giskard Testing Suite for Medical RAG Chatbot

Comprehensive security and RAG evaluation testing using Giskard framework.

---

## 📁 **Directory Structure**

```
tests/giskard/
├── __init__.py                 # Package initialization
├── config.py                   # Test configuration and settings
├── model_wrapper.py            # RAG model wrapper for Giskard
├── test_data.py                # Comprehensive test cases
├── security_tests.py           # Security testing suite
├── rag_evaluation.py           # RAG evaluation tests
├── run_tests.py                # Main test runner
├── README.md                   # This file
├── test_data/                  # Test data directory
└── results/                    # Test results directory
```

---

## 🎯 **What This Tests**

### **1. Security Tests** 🛡️

#### **PII Leakage**
- Tests if the model leaks personally identifiable information
- Validates SSN, email, phone, medical records protection
- Uses triple PII detection (Pattern + NER + Presidio)

#### **Prompt Injection**
- Tests resistance to malicious prompt injections
- Validates the model doesn't follow harmful instructions
- Checks for system prompt leakage

#### **Hallucination Detection**
- Tests if the model makes up false information
- Validates groundedness in source documents
- Checks for overconfident claims

#### **Toxic Content**
- Tests if the model generates offensive content
- Validates appropriate responses to toxic queries
- Checks content filtering

#### **Bias Detection**
- Tests for gender, age, racial, and medical bias
- Validates fair and balanced responses
- Checks for stereotyping

---

### **2. RAG Evaluation** 📊

#### **Correctness**
- Tests if answers are factually correct
- Validates response quality

#### **Groundedness**
- Tests if responses are based on retrieved context
- Validates the model doesn't fabricate information

#### **Context Relevance**
- Tests if retrieved documents are relevant to the question
- Validates retrieval quality

#### **Answer Relevance**
- Tests if answers directly address the question
- Validates response relevance

---

## 🚀 **How to Run**

### **Prerequisites**

```powershell
# Install dependencies (if not already installed)
uv add giskard

# Note: Giskard requires Python 3.9-3.11
# If you have Python 3.13, tests will run with fallback mode
```

### **Run All Tests**

```powershell
# From project root
python tests/giskard/run_tests.py

# Or specify test type
python tests/giskard/run_tests.py --test-type security
python tests/giskard/run_tests.py --test-type rag
python tests/giskard/run_tests.py --test-type all
```

### **Run Individual Test Suites**

```powershell
# Security tests only
python tests/giskard/security_tests.py

# RAG evaluation only
python tests/giskard/rag_evaluation.py

# Test model wrapper
python tests/giskard/model_wrapper.py
```

---

## 📊 **Test Results**

Results are saved in `tests/giskard/results/`:

- `security_test_results.json` - Detailed security test results
- `rag_evaluation_results.json` - Detailed RAG evaluation results
- `test_report.txt` - Comprehensive test report

---

## 🧪 **Test Categories**

### **Security Tests (50+ test cases)**

| Category | Tests | Description |
|----------|-------|-------------|
| **PII Leakage** | 5 | SSN, email, phone, medical records |
| **Prompt Injection** | 5 | Malicious instructions, system prompts |
| **Hallucination** | 5 | False claims, overconfidence |
| **Toxic Content** | 4 | Offensive language, insults |
| **Bias** | 4 | Gender, age, racial bias |
| **Robustness** | 4 | Typos, paraphrasing, formatting |
| **Edge Cases** | 4 | Empty input, long input, special chars |
| **Disclaimer** | 3 | Medical disclaimer enforcement |
| **Groundedness** | 2 | Fabricated information |

**Total:** 36+ security test cases

### **RAG Evaluation (10+ test cases)**

| Metric | Tests | Description |
|--------|-------|-------------|
| **Correctness** | 10 | Answer accuracy |
| **Groundedness** | 10 | Context-based responses |
| **Context Relevance** | 10 | Retrieval quality |
| **Answer Relevance** | 10 | Response relevance |

**Total:** 40+ RAG evaluation tests

---

## 📋 **Example Output**

```
================================================================================
MEDICAL RAG CHATBOT - COMPREHENSIVE TEST REPORT
================================================================================

Generated: 2026-02-08 12:00:00

================================================================================
SECURITY TESTING RESULTS
================================================================================

Total Tests: 36
Passed: 32 ✅
Failed: 4 ❌
Pass Rate: 88.9%

Category Breakdown:

  PII_LEAKAGE:
    Total: 5
    Passed: 5 ✅
    Failed: 0 ❌
    Pass Rate: 100.0%

  PROMPT_INJECTION:
    Total: 5
    Passed: 4 ✅
    Failed: 1 ❌
    Pass Rate: 80.0%

  HALLUCINATION:
    Total: 5
    Passed: 4 ✅
    Failed: 1 ❌
    Pass Rate: 80.0%

  TOXIC_CONTENT:
    Total: 4
    Passed: 4 ✅
    Failed: 0 ❌
    Pass Rate: 100.0%

  BIAS:
    Total: 4
    Passed: 3 ✅
    Failed: 1 ❌
    Pass Rate: 75.0%

================================================================================
RAG EVALUATION RESULTS
================================================================================

  CORRECTNESS:
    Total: 10
    Passed: 9 ✅
    Failed: 1 ❌
    Pass Rate: 90.0%

  GROUNDEDNESS:
    Total: 10
    Passed: 8 ✅
    Failed: 2 ❌
    Pass Rate: 80.0%

  CONTEXT_RELEVANCE:
    Total: 10
    Passed: 9 ✅
    Failed: 1 ❌
    Pass Rate: 90.0%

  ANSWER_RELEVANCE:
    Total: 10
    Passed: 10 ✅
    Failed: 0 ❌
    Pass Rate: 100.0%

================================================================================
RECOMMENDATIONS
================================================================================

✅ SECURITY: Good pass rate. Continue monitoring.

================================================================================
```

---

## ⚙️ **Configuration**

Edit `config.py` to customize:

```python
# Security thresholds
SECURITY_THRESHOLDS = {
    "pii_detection_threshold": 0.0,  # Zero tolerance for PII
    "toxicity_threshold": 0.3,
    "hallucination_threshold": 0.2,
    "bias_threshold": 0.3,
}

# Test categories
TEST_CATEGORIES = {
    "security": {
        "pii_leakage": True,
        "prompt_injection": True,
        "toxic_content": True,
        "data_leakage": True,
    },
    # ... more categories
}
```

---

## 🔧 **Customization**

### **Add Custom Test Cases**

Edit `test_data.py`:

```python
# Add your custom tests
CUSTOM_TESTS = [
    {
        "question": "Your test question",
        "expected_behavior": "Expected behavior",
        "category": "your_category"
    },
]
```

### **Add Custom Metrics**

Edit `rag_evaluation.py` to add custom evaluation metrics.

---

## 📝 **Notes**

### **Giskard Availability**

- **Requires Python 3.9-3.11**
- If you have Python 3.13, tests run in **fallback mode**
- Fallback mode uses your existing guardrails instead of Giskard ML models
- All tests still work, just without Giskard-specific features

### **Fallback Mode**

When Giskard is not available:
- ✅ Security tests use your existing guardrails
- ✅ RAG evaluation uses simplified metrics
- ✅ All test cases still run
- ❌ No Giskard ML-powered detection
- ❌ No automated test generation

---

## 🎯 **Integration with Existing Tools**

### **Works With:**

- ✅ **Promptfoo** - Complementary testing
- ✅ **LangSmith** - Observability integration
- ✅ **Guardrails** - Uses your existing guardrails
- ✅ **Triple PII Detection** - Pattern + NER + Presidio

### **Comparison:**

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Promptfoo** | Prompt testing | Development, CI/CD |
| **Giskard** | Security & RAG testing | Pre-deployment, audits |
| **LangSmith** | Production monitoring | Production |
| **Guardrails** | Runtime protection | Production |

---

## ✅ **Summary**

### **What You Get:**

- 🛡️ **36+ security test cases**
- 📊 **40+ RAG evaluation tests**
- 🤖 **Automated testing**
- 📈 **Detailed reports**
- 🔄 **CI/CD ready**
- ✅ **Works with or without Giskard**

### **Test Coverage:**

- ✅ PII leakage
- ✅ Prompt injection
- ✅ Hallucinations
- ✅ Toxic content
- ✅ Bias
- ✅ RAG correctness
- ✅ Groundedness
- ✅ Context relevance
- ✅ Answer relevance

**Your Medical RAG Chatbot has comprehensive security testing!** 🚀

---

## 🔗 **Related Documentation**

- [Promptfoo Tests](../promptfoo/README.md)
- [Guardrails Documentation](../../docs/TRIPLE_PII_DETECTION.md)
- [LangSmith Integration](../../docs/PROMPTFOO_DEV_VS_PRODUCTION.md)

---

## 📞 **Support**

For issues or questions:
1. Check test results in `results/` directory
2. Review test logs
3. Adjust thresholds in `config.py`
4. Modify test cases in `test_data.py`

---

**Happy Testing!** 🎉
