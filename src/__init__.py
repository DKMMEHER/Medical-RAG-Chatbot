"""
Medical Chatbot - RAG-based Medical Information System
"""

__version__ = "0.1.0"
__author__ = "Medical Chatbot Team"

from .utils.logger import get_logger, setup_logger
from .utils.exceptions import (
    MedicalChatbotError,
    ConfigurationError,
    VectorStoreError,
    LLMError,
    IngestionError,
    ValidationError,
    PIIDetectionError,
    ToxicContentError,
    MemoryError,
    EvaluationError,
)

__all__ = [
    "get_logger",
    "setup_logger",
    "MedicalChatbotError",
    "ConfigurationError",
    "VectorStoreError",
    "LLMError",
    "IngestionError",
    "ValidationError",
    "PIIDetectionError",
    "ToxicContentError",
    "MemoryError",
    "EvaluationError",
]
