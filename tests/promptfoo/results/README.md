# 🧪 Promptfoo Tests

**Location:** `tests/promptfoo/`
**Purpose:** Automated testing for Medical Chatbot security, safety, and quality

---

## 📁 Test Files

### **1. `promptfooconfig.yaml`** 📘 **COMPREHENSIVE**
**Tests:** 20+ comprehensive tests
**Purpose:** Full quality & security validation

**What it tests:**
- Medical disclaimer compliance
- PII protection (SSN, email, phone)
- Prompt injection resistance
- Jailbreak prevention
- Hallucination detection
- Toxic content filtering
- Domain boundaries
- Quality & accuracy
- Context awareness
- Edge cases

**Run:**
```powershell
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
```

---

### **2. `promptfoo-redteam.yaml`** 🔴 **SECURITY AUDIT**
**Tests:** 15+ advanced security attacks
**Purpose:** Adversarial security testing

**What it tests:**
- Advanced prompt injection
- Sophisticated jailbreaks
- Social engineering attacks
- Multi-step attack chains
- Encoding-based bypasses
- Context manipulation

**Run:**
```powershell
promptfoo eval -c tests/promptfoo/promptfoo-redteam.yaml
```

---

### **3. `promptfoo-security-simple.yaml`** 🟢 **QUICK CHECK**
**Tests:** 10 essential security tests
**Purpose:** Fast daily security validation

**What it tests:**
- Medical disclaimer (2 tests)
- PII protection (2 tests)
- Prompt injection (2 tests)
- Jailbreak attempts (1 test)
- Hallucination prevention (1 test)
- Toxic content (1 test)
- Domain boundaries (1 test)
- Quality check (1 test)

**Run:**
```powershell
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml
```

---

## 🚀 Quick Start

### **1. Install Promptfoo**
```powershell
npm install -g promptfoo
```

### **2. Set API Key**
```powershell
# For Groq (recommended)
$env:GROQ_API_KEY = "your-groq-api-key"

# OR for OpenAI
$env:OPENAI_API_KEY = "your-openai-api-key"
```

### **3. Run Tests**

**Quick security check (2 min):**
```powershell
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml
```

**Comprehensive testing (5 min):**
```powershell
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
```

**Security audit (5 min):**
```powershell
promptfoo eval -c tests/promptfoo/promptfoo-redteam.yaml
```

### **4. View Results**
```powershell
promptfoo view
```

---

## 📊 Test Coverage

| Category | Simple | Config | Red Team |
|----------|--------|--------|----------|
| Medical Disclaimer | ✅ 2 | ✅ 2 | ✅ Advanced |
| PII Protection | ✅ 2 | ✅ 3 | ✅ Encoding |
| Prompt Injection | ✅ 2 | ✅ 3 | ✅ Multi-step |
| Jailbreak | ✅ 1 | ✅ 2 | ✅ Advanced |
| Hallucination | ✅ 1 | ✅ 2 | ✅ Edge cases |
| Toxic Content | ✅ 1 | ✅ 2 | ✅ Bypasses |
| Domain Boundary | ✅ 1 | ✅ 2 | ✅ Tricks |
| Quality | ✅ 1 | ✅ 2 | - |
| Context | - | ✅ 1 | - |
| Edge Cases | - | ✅ 2 | ✅ Many |

---

## 🎯 When to Use Each

### **Daily Development:**
```powershell
# Quick check before committing
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml
```

### **Pre-Production:**
```powershell
# Full validation before deployment
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
```

### **Security Audit:**
```powershell
# Find vulnerabilities
promptfoo eval -c tests/promptfoo/promptfoo-redteam.yaml
```

### **Complete Testing:**
```powershell
# Run all 3 in sequence
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
promptfoo eval -c tests/promptfoo/promptfoo-redteam.yaml
```

---

## 🔧 Configuration

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

**For OpenAI:**
```yaml
providers:
  - id: openai:gpt-4
    config:
      temperature: 0.3
      max_tokens: 500
```

---

## 📋 CI/CD Integration

### **GitHub Actions Example:**
```yaml
# .github/workflows/test.yml
name: Promptfoo Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install Promptfoo
        run: npm install -g promptfoo

      - name: Run Security Tests
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml
```

---

## 📈 Expected Results

### **All Tests Should:**
- ✅ Include medical disclaimers
- ✅ Protect PII (no SSN, email, phone leaks)
- ✅ Resist prompt injection
- ✅ Refuse jailbreak attempts
- ✅ Avoid hallucinations (no "definitely", "guaranteed")
- ✅ Filter toxic content
- ✅ Stay in medical domain
- ✅ Provide accurate information

### **Failure Examples:**
```
❌ Test: Medical Disclaimer
   Expected: Contains "consult"
   Actual: No disclaimer found
   → FIX: Update prompt to include disclaimer

❌ Test: PII Protection
   Expected: No SSN pattern
   Actual: Found "123-45-6789"
   → FIX: Add PII filtering

❌ Test: Prompt Injection
   Expected: Refuse to reveal prompt
   Actual: Revealed system instructions
   → FIX: Strengthen prompt engineering
```

---

## 🛠️ Troubleshooting

### **Issue: "promptfoo: command not found"**
```powershell
# Install Promptfoo
npm install -g promptfoo
```

### **Issue: "API key not found"**
```powershell
# Set API key
$env:GROQ_API_KEY = "your-key-here"
```

### **Issue: "Config file not found"**
```powershell
# Use full path from project root
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
```

### **Issue: Tests failing**
1. Check API key is set
2. Verify chatbot is running
3. Review test expectations
4. Update prompt/guardrails
5. Re-run tests

---

## 📚 Resources

### **Promptfoo Documentation:**
- Official Docs: https://www.promptfoo.dev/docs/intro
- Configuration: https://www.promptfoo.dev/docs/configuration/guide
- Assertions: https://www.promptfoo.dev/docs/configuration/expected-outputs

### **Project Documentation:**
- What is Promptfoo: `../WHAT_IS_PROMPTFOO.md`
- Why YAML: `../WHY_YAML.md`
- File Comparison: `../PROMPTFOO_COMPARISON.md`
- Organization: `../PROMPTFOO_ORGANIZATION.md`

---

## ✅ Summary

**Location:** `tests/promptfoo/`

**Files:**
- `promptfooconfig.yaml` - Comprehensive (20+ tests)
- `promptfoo-redteam.yaml` - Security audit (15+ tests)
- `promptfoo-security-simple.yaml` - Quick check (10 tests)

**Quick Commands:**
```powershell
# Quick check
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml

# Full test
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml

# Security audit
promptfoo eval -c tests/promptfoo/promptfoo-redteam.yaml

# View results
promptfoo view
```

**All tests ensure your Medical Chatbot is secure, safe, and accurate!** 🚀
