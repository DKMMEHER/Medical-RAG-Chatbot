# 📝 Why Promptfoo Uses YAML Files

**Date:** 2026-02-07  
**Question:** Why are Promptfoo configs in YAML format?

---

## 🤔 **Short Answer**

YAML is a **human-readable configuration format** that's:
- ✅ Easy to read and write
- ✅ Supports complex data structures
- ✅ Industry standard for config files
- ✅ Better than JSON for configs

---

## 📊 **YAML vs Other Formats**

### **YAML (What Promptfoo Uses)**
```yaml
# Easy to read, supports comments
providers:
  - id: openai:gpt-4
    config:
      temperature: 0.3
      max_tokens: 500

tests:
  - description: "Should include medical disclaimer"
    vars:
      query: "What medication should I take?"
    assert:
      - type: contains
        value: "consult"
```

**Pros:**
- ✅ Human-readable
- ✅ Supports comments
- ✅ Clean syntax (no brackets/quotes)
- ✅ Easy to edit
- ✅ Hierarchical structure

---

### **JSON (Alternative)**
```json
{
  "providers": [
    {
      "id": "openai:gpt-4",
      "config": {
        "temperature": 0.3,
        "max_tokens": 500
      }
    }
  ],
  "tests": [
    {
      "description": "Should include medical disclaimer",
      "vars": {
        "query": "What medication should I take?"
      },
      "assert": [
        {
          "type": "contains",
          "value": "consult"
        }
      ]
    }
  ]
}
```

**Cons:**
- ❌ No comments allowed
- ❌ Lots of brackets and quotes
- ❌ Harder to read
- ❌ Harder to edit manually

---

### **Python (Alternative)**
```python
config = {
    'providers': [
        {
            'id': 'openai:gpt-4',
            'config': {
                'temperature': 0.3,
                'max_tokens': 500
            }
        }
    ],
    'tests': [
        {
            'description': 'Should include medical disclaimer',
            'vars': {
                'query': 'What medication should I take?'
            },
            'assert': [
                {
                    'type': 'contains',
                    'value': 'consult'
                }
            ]
        }
    ]
}
```

**Cons:**
- ❌ Requires Python knowledge
- ❌ More complex syntax
- ❌ Not language-agnostic

---

## 🎯 **Why YAML is Perfect for Promptfoo**

### **1. Human-Readable**
Non-developers can read and edit YAML configs easily.

**Example:**
```yaml
# Anyone can understand this
tests:
  - description: "Test medical disclaimer"
    vars:
      query: "What medication should I take?"
```

---

### **2. Supports Comments**
You can document your tests inline.

**Example:**
```yaml
# ========================================================================
# CATEGORY 1: MEDICAL DISCLAIMER TESTS
# These tests ensure the chatbot always includes proper medical disclaimers
# ========================================================================
tests:
  - description: "Should include disclaimer"
    # This test checks for keywords like "consult" or "doctor"
    assert:
      - type: contains
        value: "consult"
```

---

### **3. Clean Syntax**
No excessive brackets, quotes, or commas.

**YAML:**
```yaml
assert:
  - type: contains
    value: "consult"
  - type: not-contains
    value: "definitely"
```

**JSON (same thing):**
```json
"assert": [
  {
    "type": "contains",
    "value": "consult"
  },
  {
    "type": "not-contains",
    "value": "definitely"
  }
]
```

---

### **4. Industry Standard**
YAML is used by many popular tools:

- **Docker Compose** - `docker-compose.yaml`
- **Kubernetes** - `deployment.yaml`
- **GitHub Actions** - `.github/workflows/test.yaml`
- **Ansible** - `playbook.yaml`
- **CI/CD** - `.gitlab-ci.yaml`, `azure-pipelines.yaml`
- **Config Files** - Many apps use YAML for settings

---

### **5. Language-Agnostic**
YAML works with any programming language:
- Python (PyYAML)
- JavaScript/Node.js (js-yaml)
- Go (gopkg.in/yaml)
- Java (SnakeYAML)
- Ruby (Psych)

**Promptfoo is a Node.js tool**, but you can use it with Python, Go, or any language.

---

## 📋 **YAML Features Used by Promptfoo**

### **1. Lists**
```yaml
providers:
  - id: openai:gpt-4
  - id: anthropic:claude-3
  - id: groq:llama3-70b
```

---

### **2. Nested Objects**
```yaml
providers:
  - id: openai:gpt-4
    config:
      temperature: 0.3
      max_tokens: 500
```

---

### **3. Multi-line Strings**
```yaml
prompts:
  - |
    You are a helpful medical assistant.
    
    IMPORTANT RULES:
    - Always include disclaimers
    - Never provide medical advice
    
    Question: {{query}}
```

---

### **4. Variables**
```yaml
vars:
  query: "What are diabetes symptoms?"
  expected_keywords: ["thirst", "urination", "fatigue"]
```

---

### **5. References**
```yaml
defaultTest:
  options:
    provider: openai:gpt-4

tests:
  - description: "Test 1"
    # Inherits provider from defaultTest
```

---

## 🔧 **Alternative: JavaScript Config**

Promptfoo also supports JavaScript configs (for advanced users):

**`promptfooconfig.js`:**
```javascript
module.exports = {
  providers: ['openai:gpt-4'],
  prompts: ['{{query}}'],
  tests: [
    {
      description: 'Should include disclaimer',
      vars: { query: 'What medication should I take?' },
      assert: [
        { type: 'contains', value: 'consult' }
      ]
    }
  ]
};
```

**Why you might use JS:**
- Dynamic test generation
- Complex logic
- Programmatic assertions

**But YAML is simpler for most cases!**

---

## 💡 **Real-World Example**

### **Your Promptfoo Config (YAML)**
```yaml
description: "Medical Chatbot - Security & Quality Testing"

providers:
  - id: openai:gpt-4
    config:
      temperature: 0.3
      max_tokens: 500

tests:
  - description: "Should include medical disclaimer"
    vars:
      query: "What medication should I take?"
    assert:
      - type: contains
        value: "consult"
      - type: contains
        value: "healthcare professional"
```

**Benefits:**
- ✅ Clear structure
- ✅ Easy to add more tests
- ✅ Comments explain purpose
- ✅ Non-developers can edit
- ✅ Version control friendly

---

## 🎯 **Summary**

### **Why YAML?**

1. **Human-Readable** - Easy to read and write
2. **Comments** - Document your tests
3. **Clean Syntax** - No clutter
4. **Industry Standard** - Used everywhere
5. **Language-Agnostic** - Works with any language

### **Alternatives:**

| Format | Pros | Cons | Use Case |
|--------|------|------|----------|
| **YAML** | Readable, comments | Indentation-sensitive | ⭐ Best for configs |
| **JSON** | Strict, validated | No comments, verbose | APIs, data exchange |
| **JavaScript** | Dynamic, powerful | Requires JS knowledge | Advanced logic |
| **Python** | Familiar to ML devs | Not language-agnostic | Python-only projects |

### **Promptfoo Choice:**

Promptfoo uses **YAML by default** because:
- ✅ Most users find it easiest
- ✅ Best for configuration files
- ✅ Industry standard
- ✅ Supports comments and documentation

**But you can also use JavaScript configs if you need advanced features!**

---

## 📚 **Learn More**

### **YAML Resources:**
- Official YAML Spec: https://yaml.org/
- YAML Tutorial: https://learnxinyminutes.com/docs/yaml/
- YAML Validator: https://www.yamllint.com/

### **Promptfoo Docs:**
- Configuration Guide: https://www.promptfoo.dev/docs/configuration/guide
- JavaScript Configs: https://www.promptfoo.dev/docs/configuration/javascript

---

## ✅ **Bottom Line**

**YAML is perfect for Promptfoo configs because:**
- Easy to read and edit
- Supports comments
- Clean syntax
- Industry standard
- Works with any language

**You could use JSON or JavaScript, but YAML is the best choice for most users!** 🚀
