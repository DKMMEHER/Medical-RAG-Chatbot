# 📊 Promptfoo Configuration Files - Comparison

**Date:** 2026-02-06  
**Purpose:** Explain the 3 different Promptfoo configs

---

## 🗂️ The 3 Files

```
Medical-chatbot/
├── promptfooconfig.yaml              ← Comprehensive testing
├── promptfoo-redteam.yaml            ← Red team / adversarial testing
└── promptfoo-security-simple.yaml    ← Quick security testing (NEW)
```

---

## 📋 Detailed Comparison

### **1. `promptfooconfig.yaml`** 📘

**Purpose:** Comprehensive quality & security testing  
**Created:** January 26, 2026 (original)  
**Size:** 10,666 bytes (307 lines)  
**Complexity:** ⭐⭐⭐⭐⭐ (Most comprehensive)

**What it tests:**
```
✅ Medical Disclaimer (2 tests)
✅ PII Protection (3 tests)
✅ Prompt Injection (3 tests)
✅ Jailbreak Attempts (2 tests)
✅ Hallucination Prevention (2 tests)
✅ Toxic Content (2 tests)
✅ Domain Boundaries (2 tests)
✅ Quality & Accuracy (2 tests)
✅ Context Awareness (1 test)
✅ Edge Cases (2 tests)

Total: ~20 tests
```

**Provider:**
```yaml
providers:
  - id: openai:gpt-4
    config:
      temperature: 0.3
      max_tokens: 500
```

**Use When:**
- Full quality assurance testing
- Pre-production validation
- Comprehensive security audit
- Regular regression testing

**Run With:**
```powershell
promptfoo eval
# OR
promptfoo eval -c promptfooconfig.yaml
```

---

### **2. `promptfoo-redteam.yaml`** 🔴

**Purpose:** Adversarial / red team security testing  
**Created:** January 26, 2026 (original)  
**Size:** 5,065 bytes  
**Complexity:** ⭐⭐⭐⭐ (Advanced attacks)

**What it tests:**
```
🔴 Advanced Prompt Injection
🔴 Sophisticated Jailbreaks
🔴 Social Engineering Attacks
🔴 Multi-step Attack Chains
🔴 Encoding-based Bypasses
🔴 Context Manipulation
🔴 Adversarial Inputs
🔴 Edge Case Exploits
```

**Focus:** Offensive security testing

**Use When:**
- Security penetration testing
- Finding vulnerabilities
- Testing defense mechanisms
- Before public deployment

**Run With:**
```powershell
promptfoo eval -c promptfoo-redteam.yaml
```

---

### **3. `promptfoo-security-simple.yaml`** 🟢

**Purpose:** Quick essential security testing  
**Created:** February 5, 2026 (NEW - created by me)  
**Size:** ~3 KB  
**Complexity:** ⭐⭐ (Simplified)

**What it tests:**
```
✅ Medical Disclaimer (2 tests)
✅ PII Protection (2 tests)
✅ Prompt Injection (2 tests)
✅ Jailbreak Attempts (1 test)
✅ Hallucination Prevention (1 test)
✅ Toxic Content (1 test)
✅ Domain Boundaries (1 test)
✅ Quality Check (1 test)

Total: 10 essential tests
```

**Provider:**
```yaml
providers:
  - id: python:app.py  # Uses your actual chatbot
```

**Use When:**
- Quick security check
- Daily testing
- CI/CD pipeline
- Rapid validation

**Run With:**
```powershell
promptfoo eval -c promptfoo-security-simple.yaml
```

---

## 🎯 Which One Should You Use?

### **Scenario 1: Quick Daily Check** ⚡
**Use:** `promptfoo-security-simple.yaml`
- Fast (10 tests)
- Essential security only
- Good for CI/CD

---

### **Scenario 2: Pre-Production Testing** 🚀
**Use:** `promptfooconfig.yaml`
- Comprehensive (20+ tests)
- Quality + Security
- Full validation

---

### **Scenario 3: Security Audit** 🔒
**Use:** `promptfoo-redteam.yaml`
- Advanced attacks
- Find vulnerabilities
- Penetration testing

---

### **Scenario 4: Complete Testing** 💯
**Use:** All 3 files in sequence
```powershell
# 1. Quick check
promptfoo eval -c promptfoo-security-simple.yaml

# 2. Comprehensive testing
promptfoo eval -c promptfooconfig.yaml

# 3. Red team attacks
promptfoo eval -c promptfoo-redteam.yaml
```

---

## 📊 Feature Comparison Table

| Feature | Simple | Config | Red Team |
|---------|--------|--------|----------|
| **Tests** | 10 | 20+ | 15+ |
| **Speed** | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡ Slow |
| **Complexity** | ⭐⭐ Easy | ⭐⭐⭐⭐⭐ Complex | ⭐⭐⭐⭐ Advanced |
| **Provider** | Python/Any | OpenAI GPT-4 | OpenAI GPT-4 |
| **Focus** | Essential | Comprehensive | Adversarial |
| **Use Case** | Daily checks | Pre-production | Security audit |
| **API Cost** | Low | Medium | Medium |
| **Setup** | Easy | Medium | Medium |

---

## 🔧 How to Modify for Your Setup

### **Update Provider (All Files)**

**For Groq (your current LLM):**
```yaml
providers:
  - id: groq:llama-3.1-70b-versatile
    config:
      temperature: 0.3
      max_tokens: 500
```

**For Ollama (local):**
```yaml
providers:
  - id: ollama:llama3.1
    config:
      temperature: 0.3
```

**For Gemini:**
```yaml
providers:
  - id: google:gemini-pro
    config:
      temperature: 0.3
```

---

## 💡 My Recommendations

### **For You (Right Now):**

**Option A: Start Simple** ⭐ **RECOMMENDED**
```powershell
# 1. Use the simple config
promptfoo eval -c promptfoo-security-simple.yaml

# 2. Review results
promptfoo view
```

**Why:**
- Only 10 tests (quick)
- Essential security coverage
- Easy to understand results

---

**Option B: Comprehensive Testing**
```powershell
# 1. Update promptfooconfig.yaml to use Groq
# 2. Run full test suite
promptfoo eval

# 3. Review results
promptfoo view
```

**Why:**
- Complete coverage
- Quality + Security
- Production-ready validation

---

**Option C: Security-First**
```powershell
# 1. Run red team tests
promptfoo eval -c promptfoo-redteam.yaml

# 2. Fix vulnerabilities
# 3. Run again until all pass
```

**Why:**
- Find security holes
- Adversarial testing
- Maximum security

---

## 📋 Test Coverage Breakdown

### **Medical Disclaimer Tests**
- ✅ Simple: 2 tests
- ✅ Config: 2 tests
- ✅ Red Team: Advanced bypass attempts

### **PII Protection**
- ✅ Simple: 2 tests (SSN, email)
- ✅ Config: 3 tests (SSN, email, phone)
- ✅ Red Team: Encoding tricks, obfuscation

### **Prompt Injection**
- ✅ Simple: 2 tests (basic, role-play)
- ✅ Config: 3 tests (basic, role-play, delimiter)
- ✅ Red Team: Multi-step, encoding, context manipulation

### **Jailbreak Attempts**
- ✅ Simple: 1 test (DAN)
- ✅ Config: 2 tests (DAN, hypothetical)
- ✅ Red Team: Advanced jailbreaks, chain attacks

---

## 🎯 Summary

**You have 3 configs:**

1. **`promptfoo-security-simple.yaml`** 🟢
   - Quick (10 tests)
   - Essential security
   - Easy to run

2. **`promptfooconfig.yaml`** 📘
   - Comprehensive (20+ tests)
   - Quality + Security
   - Production validation

3. **`promptfoo-redteam.yaml`** 🔴
   - Advanced (15+ tests)
   - Adversarial attacks
   - Security audit

**Recommendation:**
- **Start with:** `promptfoo-security-simple.yaml` (quick check)
- **Then run:** `promptfooconfig.yaml` (full validation)
- **Finally:** `promptfoo-redteam.yaml` (security audit)

**All 3 are valuable - use them based on your needs!** 🚀
