# 🔄 Project Restructuring - Migration Guide

## ✅ Restructuring Complete!

The project has been successfully reorganized into a professional structure with a `src/` folder.

---

## 📁 New Structure

```
Medical-chatbot/
├── src/                           # ⭐ NEW - All source code
│   ├── __init__.py
│   ├── app.py                     # Main application (was main.py)
│   │
│   ├── config/                    # ⭐ Configuration
│   │   ├── __init__.py
│   │   ├── config.yaml            # Moved from root
│   │   └── settings.py            # ⭐ NEW - Config loader
│   │
│   ├── utils/                     # ⭐ NEW - Utilities
│   │   ├── __init__.py
│   │   ├── logger.py              # ⭐ NEW - Centralized logging
│   │   └── exceptions.py          # ⭐ NEW - Custom exceptions
│   │
│   ├── model/                     # ⭐ Model management
│   │   ├── __init__.py
│   │   └── llm_factory.py         # Moved from root
│   │
│   ├── ingesters/                 # ⭐ Data ingestion
│   │   ├── __init__.py
│   │   └── pdf_ingester.py        # Was ingest.py
│   │
│   ├── content_analyzer/          # Was Content_Analyzer
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── validator.py
│   │   ├── pii_detector.py
│   │   ├── pii_detector_presidio.py
│   │   ├── toxic_detector.py
│   │   ├── toxic_detector_ml.py
│   │   ├── ner_detector.py
│   │   ├── output_guardrails.py
│   │   └── utils.py
│   │
│   ├── memory/                    # ⭐ Memory management
│   │   ├── __init__.py
│   │   ├── create_memory.py       # Was create_memory_for_llm.py
│   │   └── connect_memory.py      # Was connect_memory_with_llm.py
│   │
│   ├── evaluation/                # Moved from root
│   │   ├── __init__.py
│   │   ├── evaluate_rag.py
│   │   ├── evaluate_simple.py
│   │   ├── human_evaluation.py
│   │   └── visualize_results.py
│   │
│   └── prompts/                   # Moved from root
│       ├── __init__.py
│       └── rag_prompt.py
│
├── examples/                      # ⭐ NEW - Demo scripts
│   ├── demo_detection_modes.py
│   ├── demo_ner_nlp_comparison.py
│   └── example_complete_pipeline.py
│
├── tests/                         # ⭐ NEW - Test files
│   └── __init__.py
│
├── data/                          # Unchanged
├── docs/                          # Unchanged
├── logs/                          # Unchanged
├── vectorstore/                   # Unchanged
├── .venv/                         # Unchanged
├── config.yaml                    # Keep for backward compatibility
├── requirements.txt               # Unchanged
├── pyproject.toml                 # Needs update
└── README.md                      # Unchanged
```

---

## 🔧 Import Changes Required

### Old Imports → New Imports

#### 1. Content Analyzer
```python
# OLD
from Content_Analyzer import ContentValidator, ValidationConfig
from Content_Analyzer.pii_detector import PIIDetector
from Content_Analyzer.toxic_detector import ToxicContentDetector

# NEW
from src.content_analyzer import ContentValidator, ValidationConfig
from src.content_analyzer.pii_detector import PIIDetector
from src.content_analyzer.toxic_detector import ToxicContentDetector
```

#### 2. LLM Factory
```python
# OLD
from llm_factory import get_generation_llm, load_config

# NEW
from src.model.llm_factory import get_generation_llm, load_config
```

#### 3. Configuration
```python
# OLD
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# NEW
from src.config.settings import settings
config = settings.config
api_key = settings.groq_api_key
```

#### 4. Utilities (NEW!)
```python
# NEW - Use centralized logger
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Message")

# NEW - Use custom exceptions
from src.utils.exceptions import ConfigurationError, LLMError

raise ConfigurationError("Missing API key")
```

#### 5. Ingestion
```python
# OLD
from ingest import ingest_documents

# NEW
from src.ingesters.pdf_ingester import ingest_documents
```

#### 6. Memory
```python
# OLD
from create_memory_for_llm import create_memory
from connect_memory_with_llm import connect_memory

# NEW
from src.memory.create_memory import create_memory
from src.memory.connect_memory import connect_memory
```

#### 7. Evaluation
```python
# OLD
from evaluation.evaluate_rag import evaluate_rag
from evaluation.human_evaluation import run_evaluation

# NEW
from src.evaluation.evaluate_rag import evaluate_rag
from src.evaluation.human_evaluation import run_evaluation
```

---

## 📝 Files That Need Import Updates

### High Priority (Core Files):
1. ✅ `src/app.py` (was main.py) - **NEEDS UPDATES**
2. ✅ `src/model/llm_factory.py` - **NEEDS UPDATES**
3. ✅ `src/ingesters/pdf_ingester.py` - **NEEDS UPDATES**
4. ✅ `src/memory/create_memory.py` - **NEEDS UPDATES**
5. ✅ `src/memory/connect_memory.py` - **NEEDS UPDATES**
6. ✅ `src/content_analyzer/*.py` - **NEEDS UPDATES**
7. ✅ `src/evaluation/*.py` - **NEEDS UPDATES**

### Medium Priority (Examples):
8. `examples/demo_detection_modes.py` - **NEEDS UPDATES**
9. `examples/demo_ner_nlp_comparison.py` - **NEEDS UPDATES**
10. `examples/example_complete_pipeline.py` - **NEEDS UPDATES**

---

## 🚀 Running the Application

### Old Way:
```bash
streamlit run main.py
```

### New Way:
```bash
# Option 1: Run from root
streamlit run src/app.py

# Option 2: Run as module (after updating pyproject.toml)
python -m src.app
```

---

## ⚙️ Update pyproject.toml

Add this to `pyproject.toml`:

```toml
[project]
name = "medical-chatbot"
version = "0.1.0"
description = "RAG-based Medical Information Chatbot"
readme = "README.md"
requires-python = ">=3.13"

[project.scripts]
medical-chatbot = "src.app:main"

[tool.setuptools]
packages = ["src"]
```

---

## 🧪 Testing After Migration

### 1. Test Imports
```python
# Test in Python REPL
python
>>> from src.utils.logger import get_logger
>>> from src.utils.exceptions import ConfigurationError
>>> from src.config.settings import settings
>>> from src.content_analyzer import ContentValidator
>>> print("All imports successful!")
```

### 2. Test Application
```bash
# Run the main app
streamlit run src/app.py
```

### 3. Test Examples
```bash
# Run demo scripts
python examples/demo_detection_modes.py
```

---

## 📋 Next Steps

### Phase 1: Update Core Files (CRITICAL)
- [ ] Update `src/app.py` imports
- [ ] Update `src/model/llm_factory.py` imports
- [ ] Update `src/content_analyzer/__init__.py` exports
- [ ] Update `src/ingesters/pdf_ingester.py` imports
- [ ] Update `src/memory/*.py` imports

### Phase 2: Update Evaluation Files
- [ ] Update `src/evaluation/evaluate_rag.py` imports
- [ ] Update `src/evaluation/evaluate_simple.py` imports
- [ ] Update `src/evaluation/human_evaluation.py` imports

### Phase 3: Update Examples
- [ ] Update `examples/demo_detection_modes.py` imports
- [ ] Update `examples/demo_ner_nlp_comparison.py` imports
- [ ] Update `examples/example_complete_pipeline.py` imports

### Phase 4: Testing
- [ ] Test main application
- [ ] Test content analyzer
- [ ] Test evaluation scripts
- [ ] Test example scripts

### Phase 5: Cleanup (Optional)
- [ ] Remove old files from root (after confirming new structure works)
- [ ] Update README.md with new structure
- [ ] Update documentation

---

## 🎯 Benefits Achieved

✅ **Professional Structure** - Follows Python best practices  
✅ **Centralized Utilities** - `logger.py` and `exceptions.py`  
✅ **Better Organization** - Clear separation of concerns  
✅ **Easier Navigation** - Logical folder structure  
✅ **Scalable** - Easy to add new modules  
✅ **Testable** - Separate tests folder  
✅ **Maintainable** - Clear module boundaries  

---

## ⚠️ Important Notes

1. **Old files still exist** - Original files in root are preserved for safety
2. **Gradual migration** - Update imports file by file
3. **Test frequently** - Test after each file update
4. **Keep backups** - Git commit before major changes
5. **Update documentation** - Update README after migration complete

---

## 🆘 Troubleshooting

### Import Error: "No module named 'src'"
**Solution:** Run from project root or add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH += ";$(pwd)"              # Windows PowerShell
```

### Import Error: "No module named 'Content_Analyzer'"
**Solution:** Update import to use `src.content_analyzer`

### Config file not found
**Solution:** Config is now in `src/config/config.yaml`, but settings.py will find it automatically

---

## 📞 Need Help?

If you encounter issues:
1. Check this migration guide
2. Verify file locations match new structure
3. Update imports according to examples above
4. Test imports in Python REPL first

---

**Migration Status:** ✅ Structure Created  
**Next Step:** Update imports in core files  
**Ready to proceed with import updates?**
