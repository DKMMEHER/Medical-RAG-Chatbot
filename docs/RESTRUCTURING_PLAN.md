# Project Restructuring Plan

## 🎯 Goal
Reorganize the Medical Chatbot project to follow a clean, professional structure with a `src/` folder containing all source code, similar to the reference image structure.

## 📊 Current Structure (Problematic)

```
Medical-chatbot/
├── Content_Analyzer/          # Module folder (should be in src/)
├── evaluation/                # Module folder (should be in src/)
├── data/                      # OK - stays at root
├── docs/                      # OK - stays at root
├── logs/                      # OK - stays at root
├── vectorstore/               # OK - stays at root
├── prompts/                   # Should move to src/
├── main.py                    # Should move to src/
├── llm_factory.py             # Should move to src/
├── ingest.py                  # Should move to src/
├── create_memory_for_llm.py   # Should move to src/
├── connect_memory_with_llm.py # Should move to src/
├── example_complete_pipeline.py # Should move to src/
├── demo_*.py                  # Demo files (can stay or move)
├── config.yaml                # Should move to src/config/
├── requirements.txt           # OK - stays at root
├── pyproject.toml             # OK - stays at root
└── README.md                  # OK - stays at root
```

**Problems:**
- ❌ No `src/` folder - code scattered at root level
- ❌ No `utils/` folder with `logger.py` and `exceptions.py`
- ❌ No `config/` folder for configuration files
- ❌ No `model/` folder for model-related code
- ❌ No `ingesters/` folder for data ingestion
- ❌ Module folders mixed with root files

## 🎯 Target Structure (Professional)

Based on the reference image, here's the new structure:

```
Medical-chatbot/
├── .venv/                     # Virtual environment (stays)
├── .vscode/                   # VS Code settings (stays)
├── data/                      # Data files (stays)
├── docs/                      # Documentation (stays)
├── logs/                      # Log files (stays)
├── vectorstore/               # Vector store data (stays)
│
├── src/                       # ⭐ NEW - All source code
│   ├── __init__.py
│   │
│   ├── config/                # ⭐ NEW - Configuration
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── settings.py        # Configuration loader
│   │
│   ├── utils/                 # ⭐ NEW - Utilities
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── logger.py          # ⭐ NEW - Centralized logging
│   │   └── exceptions.py      # ⭐ NEW - Custom exceptions
│   │
│   ├── model/                 # ⭐ NEW - Model management
│   │   ├── __init__.py
│   │   ├── llm_factory.py     # LLM creation (moved)
│   │   └── embeddings.py      # Embedding models
│   │
│   ├── ingesters/             # ⭐ NEW - Data ingestion
│   │   ├── __init__.py
│   │   ├── pdf_ingester.py    # PDF processing (from ingest.py)
│   │   └── document_processor.py
│   │
│   ├── content_analyzer/      # Renamed from Content_Analyzer
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
│   ├── memory/                # ⭐ NEW - Memory management
│   │   ├── __init__.py
│   │   ├── create_memory.py   # From create_memory_for_llm.py
│   │   └── connect_memory.py  # From connect_memory_with_llm.py
│   │
│   ├── evaluation/            # Moved from root
│   │   ├── __init__.py
│   │   ├── evaluate_rag.py
│   │   ├── evaluate_simple.py
│   │   ├── human_evaluation.py
│   │   └── visualize_results.py
│   │
│   ├── prompts/               # Moved from root
│   │   ├── __init__.py
│   │   └── rag_prompt.py
│   │
│   └── app.py                 # Main application (from main.py)
│
├── tests/                     # ⭐ NEW - Test files
│   ├── __init__.py
│   ├── test_content_analyzer.py
│   ├── test_llm_factory.py
│   └── test_ingesters.py
│
├── examples/                  # ⭐ NEW - Example scripts
│   ├── demo_detection_modes.py
│   ├── demo_ner_nlp_comparison.py
│   └── example_complete_pipeline.py
│
├── .env.example               # Environment template (stays)
├── .gitignore                 # Git ignore (stays)
├── .python-version            # Python version (stays)
├── pyproject.toml             # Project config (stays)
├── requirements.txt           # Dependencies (stays)
├── uv.lock                    # UV lock file (stays)
├── README.md                  # Documentation (stays)
└── LANGSMITH_ANALYSIS.md      # Analysis docs (stays)
```

## 📝 Key Changes

### 1. **New `src/` Folder**
All source code moves into `src/` following Python best practices.

### 2. **New `src/utils/` Folder**
```python
# src/utils/logger.py
"""Centralized logging configuration"""

# src/utils/exceptions.py  
"""Custom exception classes"""
```

### 3. **New `src/config/` Folder**
- Move `config.yaml` here
- Add `settings.py` for configuration management

### 4. **New `src/model/` Folder**
- Move `llm_factory.py` here
- Centralize all model-related code

### 5. **New `src/ingesters/` Folder**
- Move ingestion logic from `ingest.py`
- Better organization for data processing

### 6. **Rename `Content_Analyzer` → `content_analyzer`**
- Follow Python naming conventions (lowercase with underscores)

### 7. **New `tests/` Folder**
- Separate test files from source code

### 8. **New `examples/` Folder**
- Move demo scripts here

## 🔧 Migration Steps

### Phase 1: Create New Structure
1. Create `src/` folder and subfolders
2. Create `__init__.py` files
3. Create new utility files (`logger.py`, `exceptions.py`)

### Phase 2: Move Files
1. Move modules to `src/`
2. Rename `Content_Analyzer` → `content_analyzer`
3. Move configuration files
4. Move demo files to `examples/`

### Phase 3: Update Imports
1. Update all import statements
2. Update relative imports
3. Fix module paths

### Phase 4: Update Configuration
1. Update `pyproject.toml`
2. Update entry points
3. Update test configurations

### Phase 5: Testing
1. Run all tests
2. Verify imports work
3. Test application functionality

## ⚠️ Import Changes Required

### Before:
```python
from Content_Analyzer import ContentValidator
from llm_factory import get_generation_llm
import config
```

### After:
```python
from src.content_analyzer import ContentValidator
from src.model.llm_factory import get_generation_llm
from src.config.settings import config
```

## 📋 Files to Create

### 1. `src/utils/logger.py`
```python
"""
Centralized logging configuration for Medical Chatbot
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(
    name: str,
    log_file: str = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with console and file handlers
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path("logs") / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger

# Pre-configured loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger with default configuration"""
    return setup_logger(
        name=name,
        log_file=f"medical_chatbot_{datetime.now().strftime('%Y%m%d')}.log",
        level=logging.INFO
    )
```

### 2. `src/utils/exceptions.py`
```python
"""
Custom exception classes for Medical Chatbot
"""

class MedicalChatbotError(Exception):
    """Base exception for Medical Chatbot"""
    pass

class ConfigurationError(MedicalChatbotError):
    """Raised when configuration is invalid or missing"""
    pass

class VectorStoreError(MedicalChatbotError):
    """Raised when vector store operations fail"""
    pass

class LLMError(MedicalChatbotError):
    """Raised when LLM operations fail"""
    pass

class IngestionError(MedicalChatbotError):
    """Raised when document ingestion fails"""
    pass

class ValidationError(MedicalChatbotError):
    """Raised when content validation fails"""
    pass

class PIIDetectionError(ValidationError):
    """Raised when PII detection fails"""
    pass

class ToxicContentError(ValidationError):
    """Raised when toxic content is detected"""
    pass

class MemoryError(MedicalChatbotError):
    """Raised when memory operations fail"""
    pass

class EvaluationError(MedicalChatbotError):
    """Raised when evaluation fails"""
    pass
```

### 3. `src/config/settings.py`
```python
"""
Configuration management for Medical Chatbot
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError

logger = get_logger(__name__)

class Settings:
    """Application settings manager"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize settings
        
        Args:
            config_path: Path to config.yaml file
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config = self._load_yaml_config(config_path)
        self._validate_config()
    
    def _load_yaml_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise ConfigurationError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise ConfigurationError(f"Invalid YAML: {e}")
    
    def _validate_config(self):
        """Validate required configuration"""
        required_keys = ['llm', 'embeddings', 'vectorstore']
        missing = [key for key in required_keys if key not in self.config]
        
        if missing:
            raise ConfigurationError(f"Missing required config keys: {missing}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    @property
    def groq_api_key(self) -> str:
        """Get Groq API key from environment"""
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ConfigurationError("GROQ_API_KEY not found in environment")
        return key
    
    @property
    def langsmith_api_key(self) -> str:
        """Get LangSmith API key from environment (optional)"""
        return os.getenv("LANGSMITH_API_KEY")

# Global settings instance
settings = Settings()
```

## 🚀 Benefits of New Structure

### 1. **Professional Organization**
- ✅ Clear separation of concerns
- ✅ Easy to navigate
- ✅ Follows Python best practices

### 2. **Better Maintainability**
- ✅ Centralized utilities (`logger.py`, `exceptions.py`)
- ✅ Organized by functionality
- ✅ Easier to find files

### 3. **Improved Testing**
- ✅ Separate `tests/` folder
- ✅ Clear test organization
- ✅ Easy to run tests

### 4. **Scalability**
- ✅ Easy to add new modules
- ✅ Clear structure for new features
- ✅ Better for team collaboration

### 5. **Deployment Ready**
- ✅ Standard Python package structure
- ✅ Easy to package and distribute
- ✅ Clear entry points

## ⏭️ Next Steps

1. **Review this plan** - Confirm the structure meets your needs
2. **Backup current code** - Create a git branch or backup
3. **Execute migration** - I'll create the new structure and move files
4. **Update imports** - Fix all import statements
5. **Test thoroughly** - Ensure everything works

**Ready to proceed with the restructuring?**
