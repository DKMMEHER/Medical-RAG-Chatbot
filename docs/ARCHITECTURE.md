# Content Analyzer - Architecture Overview

## 🏗️ Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Content Analyzer Module                      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    ContentValidator                         │ │
│  │                  (Main Orchestrator)                        │ │
│  │                                                              │ │
│  │  • validate(text) → (is_safe, issues)                       │ │
│  │  • validate_batch(texts)                                    │ │
│  │  • sanitize_content(text)                                   │ │
│  │  • get_validation_summary(issues)                           │ │
│  └──────────────┬────────────────────────┬─────────────────────┘ │
│                 │                        │                        │
│                 ▼                        ▼                        │
│  ┌──────────────────────┐  ┌──────────────────────────┐         │
│  │   PIIDetector        │  │  ToxicContentDetector     │         │
│  │                      │  │                           │         │
│  │ • detect()           │  │ • detect()                │         │
│  │ • detect_by_type()   │  │ • detect_by_category()    │         │
│  │ • has_pii()          │  │ • has_toxic_content()     │         │
│  │ • redact_pii()       │  │ • get_toxicity_score()    │         │
│  │ • get_pii_count()    │  │ • filter_toxic_content()  │         │
│  └──────────────────────┘  └──────────────────────────┘         │
│                 │                        │                        │
│                 └────────────┬───────────┘                        │
│                              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Configuration                            │ │
│  │                                                              │ │
│  │  • ValidationSeverity (LOW, MEDIUM, HIGH, CRITICAL)         │ │
│  │  • ValidationIssue (issue_type, severity, description)      │ │
│  │  • PII_PATTERNS (10+ types)                                 │ │
│  │  • TOXIC_CATEGORIES (5 categories)                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Utilities                                │ │
│  │                                                              │ │
│  │  • format_validation_report()                               │ │
│  │  • calculate_risk_score()                                   │ │
│  │  • create_validation_metrics()                              │ │
│  │  • export_issues_to_dict()                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Validation Flow

```
┌─────────────────┐
│   Input Text    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     ContentValidator.validate()         │
└────────┬────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ PII Detection│   │Toxic Detection│   │   Logging    │
│              │   │               │   │              │
│ • Email      │   │ • Profanity   │   │ • Issue log  │
│ • SSN        │   │ • Hate speech │   │ • Metrics    │
│ • Phone      │   │ • Violence    │   │ • Audit      │
│ • Medical ID │   │ • Harassment  │   │              │
└──────┬───────┘   └──────┬────────┘   └──────────────┘
       │                  │
       └────────┬─────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│      Evaluate Safety (Blocking Rules)   │
│                                         │
│  • Check CRITICAL severity → Block?     │
│  • Check HIGH severity → Block?         │
│  • Apply custom rules                   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Return Results                  │
│                                         │
│  (is_safe: bool, issues: List[Issue])   │
└─────────────────────────────────────────┘
```

---

## 🎯 Integration Points in RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Medical Chatbot                          │
└─────────────────────────────────────────────────────────────────┘

1. INGESTION PHASE (ingest.py)
   ┌──────────────────┐
   │  Load PDF        │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐      ┌─────────────────────┐
   │  Chunk Text      │─────▶│ ✅ Validate Chunks  │◀── Content Analyzer
   └────────┬─────────┘      └─────────────────────┘
            │                         │
            │                         ▼
            │                ┌─────────────────────┐
            │                │ Redact PII          │
            │                │ Filter Toxic        │
            │                └──────────┬──────────┘
            │                           │
            ▼                           ▼
   ┌──────────────────────────────────────┐
   │  Create Embeddings (Safe Content)    │
   └────────┬─────────────────────────────┘
            │
            ▼
   ┌──────────────────┐
   │  Vector Store    │
   └──────────────────┘


2. RUNTIME PHASE (main.py)
   ┌──────────────────┐
   │  User Query      │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐      ┌─────────────────────┐
   │  Validate Query  │◀─────│ ✅ Content Analyzer │
   └────────┬─────────┘      └─────────────────────┘
            │
            │ (if safe)
            ▼
   ┌──────────────────┐
   │  Retrieve Docs   │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐      ┌─────────────────────┐
   │  Validate Context│◀─────│ ✅ Content Analyzer │
   └────────┬─────────┘      └─────────────────────┘
            │
            │ (safe docs only)
            ▼
   ┌──────────────────┐
   │  Send to LLM     │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐      ┌─────────────────────┐
   │  Validate Output │◀─────│ ✅ Content Analyzer │
   └────────┬─────────┘      └─────────────────────┘
            │
            ▼
   ┌──────────────────┐
   │  Show to User    │
   └──────────────────┘
```

---

## 📊 Data Flow Example

```
Input: "Patient John Doe, SSN: 123-45-6789, has diabetes. Contact: john@email.com"

         │
         ▼
┌─────────────────────────────────────────┐
│  PIIDetector.detect()                   │
│                                         │
│  Found:                                 │
│  • PII_SSN (CRITICAL)                   │
│  • PII_EMAIL (HIGH)                     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  ToxicContentDetector.detect()          │
│                                          │
│  Found: None                             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Evaluate Safety                         │
│                                          │
│  • CRITICAL PII found → BLOCK            │
│  • is_safe = False                       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Return:                                 │
│  is_safe = False                         │
│  issues = [                              │
│    ValidationIssue(                      │
│      type="PII_SSN",                     │
│      severity=CRITICAL,                  │
│      description="SSN detected",         │
│      matched_text="12***89"              │
│    ),                                    │
│    ValidationIssue(                      │
│      type="PII_EMAIL",                   │
│      severity=HIGH,                      │
│      description="Email detected",       │
│      matched_text="jo***om"              │
│    )                                     │
│  ]                                       │
└─────────────────────────────────────────┘
```

---

## 🔧 Configuration Matrix

| Config Setting | STRICT | BALANCED | LENIENT |
|----------------|--------|----------|---------|
| `pii_block_on_critical` | ✅ True | ✅ True | ✅ True |
| `pii_block_on_high` | ✅ True | ❌ False | ❌ False |
| `toxic_block_on_critical` | ✅ True | ✅ True | ❌ False |
| `toxic_block_on_high` | ✅ True | ❌ False | ❌ False |
| **Use Case** | Medical/Financial | General RAG | Internal Tools |
| **Blocks** | Everything | Critical only | Critical PII only |

---

## 📈 Performance Considerations

```
┌─────────────────────────────────────────────────────────────┐
│                    Performance Profile                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PII Detection (Regex):        ~1-2ms per 1000 chars       │
│  Toxic Detection (Word list):  ~0.5-1ms per 1000 chars     │
│  Total Validation:             ~2-3ms per 1000 chars       │
│                                                              │
│  Recommended:                                                │
│  • Ingestion: Full validation (time not critical)          │
│  • Runtime: Lightweight validation (speed matters)         │
│  • Output: Medium validation (balance speed & safety)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Learning Path

```
1. Start Here:
   └─ Read: Content_Analyzer/README.md
   └─ Run: demo_content_analyzer.py
   └─ Study: Content_Analyzer/QUICK_START.py

2. Understand Core:
   └─ Review: config.py (severity levels, patterns)
   └─ Review: pii_detector.py (PII logic)
   └─ Review: toxic_detector.py (toxic logic)

3. Integration:
   └─ Study: validator.py (main orchestrator)
   └─ Study: utils.py (helper functions)
   └─ Read: CONTENT_ANALYZER_SUMMARY.md

4. Customize:
   └─ Add custom PII patterns
   └─ Add custom toxic categories
   └─ Adjust blocking policies

5. Deploy:
   └─ Integrate into ingest.py
   └─ Integrate into main.py
   └─ Set up logging and monitoring
```

---

## 🚀 Quick Commands

```bash
# View module structure
ls Content_Analyzer/

# Read documentation
cat Content_Analyzer/README.md

# Run demo (requires Python environment)
python demo_content_analyzer.py

# Test individual components
python Content_Analyzer/pii_detector.py
python Content_Analyzer/toxic_detector.py
python Content_Analyzer/validator.py

# View quick examples
cat Content_Analyzer/QUICK_START.py
```

---

## ✅ Checklist for Integration

- [ ] Read README.md
- [ ] Run demo_content_analyzer.py
- [ ] Understand ValidationConfig options
- [ ] Test with your own data
- [ ] Decide on blocking policy (strict/balanced/lenient)
- [ ] Add custom PII patterns if needed
- [ ] Add custom toxic categories if needed
- [ ] Integrate into ingest.py (optional)
- [ ] Integrate into main.py (recommended)
- [ ] Set up logging
- [ ] Test end-to-end
- [ ] Monitor validation metrics
- [ ] Document your configuration

---

**You're all set! 🎉**
