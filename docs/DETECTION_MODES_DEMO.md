# 🚀 Quick Start: Detection Modes Demo

## 📋 Prerequisites

### **1. Download spaCy Model (One-time setup)**

```bash
python -m spacy download en_core_web_sm
```

**Note:** This downloads the English language model (~40MB). Required for Presidio to work.

---

## 🎯 Run the Demo

```bash
# From project root
uv run demo_detection_modes.py
```

---

## 📊 What the Demo Shows

### **Test 1: Structured Data**
```
Text: "Contact info: SSN 123-45-6789, email john@test.com, phone 555-123-4567"

REGEX:    ✅ Finds SSN, email, phone (3 items)
PRESIDIO: ✅ Finds SSN, email, phone (3 items)
HYBRID:   ✅ Finds SSN, email, phone (3 items)

Result: All modes perform equally on structured data
```

### **Test 2: Person Names (Unstructured)**
```
Text: "Dr. Sarah Johnson treated patient Michael Smith at Memorial Hospital"

REGEX:    ❌ Finds nothing (no patterns match)
PRESIDIO: ✅ Finds Dr. Sarah Johnson, Michael Smith, Memorial Hospital (3 items)
HYBRID:   ✅ Finds Dr. Sarah Johnson, Michael Smith, Memorial Hospital (3 items)

Result: Presidio/Hybrid catch what regex misses! ⭐
```

### **Test 3: Mixed Content**
```
Text: "Patient John Doe (SSN: 987-65-4321) was seen by Dr. Emily Chen. 
       Contact: john.doe@hospital.com"

REGEX:    ✅ Finds SSN, email (2 items)
PRESIDIO: ✅ Finds SSN, email, John Doe, Dr. Emily Chen (4 items)
HYBRID:   ✅ Finds SSN, email, John Doe, Dr. Emily Chen (4 items)

Result: Hybrid gives maximum coverage! 🎯
```

### **Test 4: Medical Context**
```
Text: "Dr. Robert Martinez prescribed medication for patient ID MRN-123456"

REGEX:    ✅ Finds MRN (1 item)
PRESIDIO: ✅ Finds MRN, Dr. Robert Martinez (2 items)
HYBRID:   ✅ Finds MRN, Dr. Robert Martinez (2 items)

Result: Presidio understands medical context
```

### **Test 5: Clean Text**
```
Text: "Diabetes is managed through diet, exercise, and medication"

REGEX:    ✅ No PII found
PRESIDIO: ✅ No PII found
HYBRID:   ✅ No PII found

Result: All modes correctly identify clean text
```

---

## ⚡ Performance Results

Typical performance on a modern laptop:

```
⚡ REGEX Mode:    ~2ms per validation
🐢 PRESIDIO Mode: ~50ms per validation (25x slower)
🔄 HYBRID Mode:   ~52ms per validation (26x slower)
```

**Takeaway:** REGEX is much faster, but Presidio/Hybrid catch more PII!

---

## 🎯 Decision Matrix

| Your Requirement | Recommended Mode |
|-----------------|------------------|
| **Speed is critical** | REGEX |
| **Only structured data (SSN, emails)** | REGEX |
| **Development/testing** | REGEX |
| **Need to detect names** | PRESIDIO or HYBRID |
| **Medical/healthcare app** | PRESIDIO or HYBRID |
| **Compliance (HIPAA, GDPR)** | HYBRID |
| **Maximum security** | HYBRID |
| **Can't miss ANY PII** | HYBRID |

---

## 💡 Quick Configuration Examples

### **Use REGEX (Default):**
```python
from Content_Analyzer import ContentValidator

validator = ContentValidator()  # Uses REGEX by default
```

### **Use PRESIDIO:**
```python
from Content_Analyzer import ContentValidator, ValidationConfig, PIIDetectionMode

config = ValidationConfig(pii_detection_mode=PIIDetectionMode.PRESIDIO)
validator = ContentValidator(config)
```

### **Use HYBRID:**
```python
from Content_Analyzer import ContentValidator, ValidationConfig, PIIDetectionMode

config = ValidationConfig(pii_detection_mode=PIIDetectionMode.HYBRID)
validator = ContentValidator(config)
```

---

## 🔍 What You'll See in the Demo

1. **Side-by-side comparison** of all 3 modes
2. **Real examples** with medical context
3. **Performance metrics** (speed comparison)
4. **Recommendations** for your use case
5. **Interactive** - press Enter to advance

---

## 📚 Full Documentation

See `docs/PRESIDIO_INTEGRATION.md` for complete details on:
- Installation instructions
- All 50+ entity types supported
- Advanced configuration options
- Confidence score tuning
- Anonymization features

---

## ✅ Summary

**REGEX:**
- ⚡ Fast (2ms)
- ✅ Good for structured data
- ❌ Misses person names

**PRESIDIO:**
- 🐢 Slower (50ms)
- ✅ Detects person names
- ✅ Context-aware

**HYBRID:**
- 🐢 Slower (52ms)
- ✅ Maximum coverage
- ✅ Best of both worlds

**Choose based on your speed vs accuracy requirements!** 🎯
