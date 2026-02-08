# 📁 Promptfoo File Organization - Best Practices

**Date:** 2026-02-07  
**Question:** Should Promptfoo configs be in root or tests/ folder?

---

## 🤔 **The Question**

Where should we put Promptfoo configuration files?

**Option A:** Root directory (current)
```
Medical-chatbot/
├── promptfooconfig.yaml
├── promptfoo-redteam.yaml
├── promptfoo-security-simple.yaml
└── ...
```

**Option B:** tests/ folder
```
Medical-chatbot/
├── tests/
│   ├── promptfoo/
│   │   ├── promptfooconfig.yaml
│   │   ├── promptfoo-redteam.yaml
│   │   └── promptfoo-security-simple.yaml
│   └── unit/
│       └── test_*.py
└── ...
```

---

## 📊 **Analysis**

### **Option A: Root Directory** (Current)

**Pros:**
- ✅ **Easy to find** - Visible immediately
- ✅ **Promptfoo convention** - Default location
- ✅ **Easy to run** - `promptfoo eval` works out of the box
- ✅ **Common practice** - Most projects do this
- ✅ **No path issues** - Promptfoo finds configs automatically

**Cons:**
- ❌ **Clutters root** - More files in root directory
- ❌ **Mixed concerns** - Testing files with app files
- ❌ **Less organized** - Not grouped with other tests

**Examples from popular projects:**
```
langchain/
├── promptfooconfig.yaml  ← Root
├── package.json
└── ...

openai-cookbook/
├── promptfooconfig.yaml  ← Root
├── README.md
└── ...
```

---

### **Option B: tests/ Folder** (Organized)

**Pros:**
- ✅ **Better organization** - All tests in one place
- ✅ **Clean root** - Less clutter
- ✅ **Logical grouping** - Tests together
- ✅ **Scalability** - Easy to add more test types
- ✅ **Professional** - Enterprise-grade structure

**Cons:**
- ❌ **Extra config** - Need to specify path
- ❌ **Slightly harder to run** - Need `-c` flag
- ❌ **Less common** - Not the default convention

**How to run:**
```powershell
# Need to specify config path
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
```

---

## 🎯 **My Recommendation**

### **Option C: Hybrid Approach** ⭐ **BEST**

Keep a **main config in root**, detailed configs in **tests/**:

```
Medical-chatbot/
├── promptfooconfig.yaml          ← Main config (root)
├── tests/
│   ├── promptfoo/
│   │   ├── redteam.yaml          ← Advanced tests
│   │   ├── security.yaml         ← Security tests
│   │   ├── quality.yaml          ← Quality tests
│   │   └── README.md             ← Test documentation
│   ├── unit/
│   │   ├── test_llm_factory.py
│   │   ├── test_vectorstore.py
│   │   └── ...
│   └── integration/
│       └── test_rag_pipeline.py
├── app.py
└── ...
```

**Why this is best:**
- ✅ **Easy to run** - `promptfoo eval` works (uses root config)
- ✅ **Organized** - Advanced configs in tests/
- ✅ **Clean root** - Only main config in root
- ✅ **Flexible** - Can run specific configs when needed
- ✅ **Best of both worlds**

---

## 📋 **Recommended Structure**

### **Full Recommended Layout:**

```
Medical-chatbot/
├── promptfooconfig.yaml              ← Main/default config (root)
│
├── tests/                            ← All testing files
│   ├── promptfoo/                    ← Promptfoo tests
│   │   ├── redteam.yaml              ← Red team attacks
│   │   ├── security.yaml             ← Security tests
│   │   ├── quality.yaml              ← Quality tests
│   │   ├── compliance.yaml           ← Compliance tests
│   │   ├── edge-cases.yaml           ← Edge case tests
│   │   └── README.md                 ← Documentation
│   │
│   ├── unit/                         ← Unit tests (pytest)
│   │   ├── test_llm_factory.py
│   │   ├── test_vectorstore.py
│   │   ├── test_content_analyzer.py
│   │   └── test_observability.py
│   │
│   ├── integration/                  ← Integration tests
│   │   ├── test_rag_pipeline.py
│   │   └── test_app.py
│   │
│   └── fixtures/                     ← Test data
│       ├── sample_queries.json
│       └── expected_responses.json
│
├── app.py
├── create_vectorstore.py
├── evaluate_chatbot.py
└── ...
```

---

## 🔧 **How to Implement**

### **Step 1: Create Structure**

```powershell
# Create test folders
New-Item -ItemType Directory -Path "tests/promptfoo"
New-Item -ItemType Directory -Path "tests/unit"
New-Item -ItemType Directory -Path "tests/integration"
New-Item -ItemType Directory -Path "tests/fixtures"
```

### **Step 2: Move Files**

```powershell
# Keep main config in root
# (promptfooconfig.yaml stays)

# Move specialized configs to tests/promptfoo/
Move-Item "promptfoo-redteam.yaml" "tests/promptfoo/redteam.yaml"
Move-Item "promptfoo-security-simple.yaml" "tests/promptfoo/security.yaml"
```

### **Step 3: Update Main Config**

**`promptfooconfig.yaml` (root):**
```yaml
# Main Promptfoo Configuration
# For specialized tests, see tests/promptfoo/

description: "Medical Chatbot - Main Test Suite"

providers:
  - id: groq:llama-3.1-70b-versatile
    config:
      temperature: 0.3
      max_tokens: 500

# Include other configs
extends:
  - tests/promptfoo/security.yaml
  - tests/promptfoo/quality.yaml

# Or define main tests here
tests:
  # Essential tests
  - description: "Core functionality"
    # ...
```

### **Step 4: Create README**

**`tests/promptfoo/README.md`:**
```markdown
# Promptfoo Tests

## Quick Start

# Run main tests (from root)
promptfoo eval

# Run specific test suite
promptfoo eval -c tests/promptfoo/redteam.yaml
promptfoo eval -c tests/promptfoo/security.yaml

## Test Suites

- `redteam.yaml` - Advanced security attacks
- `security.yaml` - Essential security tests
- `quality.yaml` - Quality & accuracy tests
- `compliance.yaml` - Medical compliance tests
```

---

## 📊 **Comparison Table**

| Aspect | Root Only | tests/ Only | Hybrid (Recommended) |
|--------|-----------|-------------|----------------------|
| **Ease of use** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Organization** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Scalability** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Convention** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Clean root** | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Flexibility** | ⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## 💡 **Industry Best Practices**

### **Small Projects (<5 configs):**
```
✅ Root directory
   - Simple
   - Easy to find
   - Quick to run
```

### **Medium Projects (5-10 configs):**
```
✅ Hybrid approach
   - Main config in root
   - Specialized in tests/
   - Best balance
```

### **Large Projects (10+ configs):**
```
✅ tests/ directory
   - Fully organized
   - Categorized
   - Enterprise-grade
```

---

## 🎯 **For Your Medical Chatbot**

### **Current State:**
- 3 Promptfoo configs
- Growing project
- Professional application

### **Recommendation:** **Hybrid Approach** ⭐

**Why:**
1. You have 3 configs (medium size)
2. Professional medical application
3. Will likely add more tests
4. Need organization + ease of use

### **Proposed Structure:**

```
Medical-chatbot/
├── promptfooconfig.yaml          ← Keep (main config)
├── tests/
│   ├── promptfoo/
│   │   ├── redteam.yaml          ← Move here
│   │   ├── security.yaml         ← Move here
│   │   └── README.md             ← Create
│   └── unit/                     ← Future pytest tests
└── ...
```

---

## 🔧 **Migration Steps**

### **Option 1: Keep Current (Simplest)**
```powershell
# Do nothing - current setup works fine
# Good for: Quick projects, prototypes
```

### **Option 2: Hybrid (Recommended)**
```powershell
# 1. Create folder
New-Item -ItemType Directory -Path "tests/promptfoo"

# 2. Move specialized configs
Move-Item "promptfoo-redteam.yaml" "tests/promptfoo/redteam.yaml"
Move-Item "promptfoo-security-simple.yaml" "tests/promptfoo/security.yaml"

# 3. Keep main config in root
# (promptfooconfig.yaml stays)

# 4. Create README
# (Document how to run tests)
```

### **Option 3: Full Migration (Most Organized)**
```powershell
# Move ALL configs to tests/
Move-Item "promptfoo*.yaml" "tests/promptfoo/"

# Update commands to use -c flag
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
```

---

## 📋 **Running Tests After Organization**

### **Hybrid Approach:**
```powershell
# Main tests (easy)
promptfoo eval

# Specific tests (organized)
promptfoo eval -c tests/promptfoo/redteam.yaml
promptfoo eval -c tests/promptfoo/security.yaml
```

### **Full tests/ Approach:**
```powershell
# All tests require -c flag
promptfoo eval -c tests/promptfoo/promptfooconfig.yaml
promptfoo eval -c tests/promptfoo/redteam.yaml
```

---

## ✅ **My Final Recommendation**

### **For Your Project:** **Hybrid Approach** ⭐

**Keep:**
- `promptfooconfig.yaml` in root (main config)

**Move to tests/promptfoo/:**
- `promptfoo-redteam.yaml` → `tests/promptfoo/redteam.yaml`
- `promptfoo-security-simple.yaml` → `tests/promptfoo/security.yaml`

**Benefits:**
- ✅ Clean root directory
- ✅ Easy to run main tests (`promptfoo eval`)
- ✅ Organized specialized tests
- ✅ Room to grow (add more test types)
- ✅ Professional structure
- ✅ Best of both worlds

**Commands:**
```powershell
# Quick test (main config)
promptfoo eval

# Security audit
promptfoo eval -c tests/promptfoo/redteam.yaml

# Quick security check
promptfoo eval -c tests/promptfoo/security.yaml
```

---

## 🎯 **Summary**

**Question:** Root or tests/ folder?

**Answer:** **Hybrid approach** (main in root, specialized in tests/)

**Why:**
- ✅ Easy to use (main config in root)
- ✅ Well organized (specialized in tests/)
- ✅ Scalable (room to grow)
- ✅ Professional (enterprise structure)
- ✅ Flexible (run any config easily)

**Action:**
1. Create `tests/promptfoo/` folder
2. Move `promptfoo-redteam.yaml` → `tests/promptfoo/redteam.yaml`
3. Move `promptfoo-security-simple.yaml` → `tests/promptfoo/security.yaml`
4. Keep `promptfooconfig.yaml` in root
5. Create `tests/promptfoo/README.md`

**Result:** Clean, organized, professional structure! 🚀
