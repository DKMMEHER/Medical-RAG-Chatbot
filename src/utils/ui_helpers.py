"""
UI-related helper functions for the Medical Chatbot.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def display_error_message(error: Exception, error_type: str):
    """
    Display user-friendly error messages using non-blocking toast notifications.

    Args:
        error: The exception object
        error_type: Category of error (e.g., VectorStoreError, LLMError)

    Returns:
        dict: Information containing title and suggestion for remediation
    """
    error_messages = {
        "VectorStoreError": {
            "title": "📚 Vector Store Error",
            "suggestion": "Please ensure the vector database is created by running `create_memory_for_llm.py`",
        },
        "ConfigurationError": {
            "title": "⚙️ Configuration Error",
            "suggestion": "Please check your `.env` file and ensure all required API keys are set",
        },
        "LLMError": {
            "title": "🤖 AI Model Error",
            "suggestion": "There was an issue with the AI model. Please try again or check your API key",
        },
        "default": {
            "title": "❌ Unexpected Error",
            "suggestion": "An unexpected error occurred. Please try again",
        },
    }

    error_info = error_messages.get(error_type, error_messages["default"])

    # Non-blocking toast notification if in streamlit context
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx():
            st.toast(f"{error_info['title']}: {str(error)[:100]}", icon="🚨")
    except ImportError:
        pass

    # Log the error
    logger.error(f"{error_type}: {str(error)}", exc_info=True)

    return error_info
