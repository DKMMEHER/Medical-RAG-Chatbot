
## 🚀 Installation
```bash
npm install -g promptfoo
```

## 🔑 Setup
```bash
# Set API key
set OPENAI_API_KEY=your-key-here

# Or use .env file
echo "OPENAI_API_KEY=your-key" > .env
```

## 📊 Basic Commands

### Run Tests
```bash
promptfoo eval                    # Run all tests
promptfoo eval -c config.yaml     # Use specific config
promptfoo eval --filter "PII"     # Run specific tests
promptfoo view                    # View results in browser
```

### Red Team Testing
```bash
promptfoo redteam init            # Initialize red team
promptfoo redteam run             # Run adversarial tests
promptfoo redteam report          # Generate report
promptfoo redteam report --view   # View in browser
```

## 📁 Your Files

```
Medical-chatbot/
├── promptfooconfig.yaml          # 40+ test cases
├── promptfoo-redteam.yaml        # 100+ red team tests
├── prompts/
│   └── medical_assistant.txt     # System prompt
└── docs/
    └── PROMPTFOO_TESTING_GUIDE.md  # Full guide
```

## 🎯 Test Categories (40+ tests)

1. ✅ Medical Disclaimers (2)
2. 🔒 PII Protection (3)
3. 🛡️ Prompt Injection (3)
4. 🚫 Jailbreaks (2)
5. 🤔 Hallucinations (2)
6. ⚠️ Toxic Content (2)
7. 🎯 Domain Boundaries (2)
8. ⭐ Quality & Accuracy (2)
9. 💬 Context Awareness (1)
10. 🔧 Edge Cases (2)

## 🛡️ Red Team Plugins (100+ tests)

- **PII** (20 tests) - Extract sensitive data
- **Prompt Injection** (15 tests) - Manipulate system
- **Jailbreaks** (25 tests) - Bypass safety
- **Harmful Content** (15 tests) - Generate toxic output
- **Hallucination** (15 tests) - False information
- **Custom Medical** (10 tests) - Domain-specific

## 📈 Typical Workflow

```bash
# 1. Run basic tests
promptfoo eval

# 2. View results
promptfoo view

# 3. Fix any issues

# 4. Run red team
promptfoo redteam run

# 5. View red team report
promptfoo redteam report --view

# 6. Deploy if all pass! 🚀
```

## 🔍 Common Assertions

```yaml
# Text contains
- type: contains
  value: "expected text"

# Text doesn't contain
- type: not-contains
  value: "forbidden text"

# No PII
- type: not-contains-pii

# Not toxic
- type: not-toxic

# Custom JavaScript
- type: javascript
  value: |
    return output.length > 50;
```

## 🎨 Quick Test Template

```yaml
tests:
  - description: "Your test name"
    vars:
      query: "Your test query"
    assert:
      - type: contains
        value: "expected"
      - type: not-contains
        value: "forbidden"
```

## 🔄 CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run Promptfoo Tests
  run: |
    npm install -g promptfoo
    promptfoo eval
    promptfoo redteam run
```

## 📊 Results Interpretation

```
✅ PASS - Test passed
❌ FAIL - Test failed
⚠️  WARN - Warning (not critical)

Pass Rate: 95% (38/40 tests passed)
```

## 🎯 When to Use

| Scenario | Command |
|----------|---------|
| **Before deployment** | `promptfoo eval` |
| **Find vulnerabilities** | `promptfoo redteam run` |
| **Compare prompts** | `promptfoo eval` (multiple prompts) |
| **Compare models** | `promptfoo eval` (multiple providers) |
| **CI/CD pipeline** | `promptfoo eval --output json` |

## 🛡️ With Content_Analyzer

**Runtime (Production):**
```python
from Content_Analyzer import ContentValidator, OutputGuardrails
# Real-time protection
```

**Testing (Development):**
```bash
promptfoo eval
promptfoo redteam run
# Comprehensive testing
```

## 📚 Full Documentation

See `docs/PROMPTFOO_TESTING_GUIDE.md` for:
- Detailed test explanations
- Customization guide
- Best practices
- Troubleshooting

## ✅ Pre-Deployment Checklist

- [ ] `promptfoo eval` passes
- [ ] `promptfoo redteam run` - no critical issues
- [ ] PII protection verified
- [ ] Medical disclaimers present
- [ ] Prompt injection resistant
- [ ] Jailbreak resistant
- [ ] Content_Analyzer integrated
- [ ] CI/CD pipeline configured

## 🚀 Quick Start

```bash
# 1. Install
npm install -g promptfoo

# 2. Set API key
set OPENAI_API_KEY=your-key

# 3. Run tests
promptfoo eval

# 4. View results
promptfoo view

# Done! 🎉
```

---

**Need help?** See `docs/PROMPTFOO_TESTING_GUIDE.md`
