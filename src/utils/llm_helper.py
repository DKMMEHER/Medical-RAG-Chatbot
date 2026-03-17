"""
LLM-related helper functions for the Medical Chatbot.
"""

from typing import Any


def stream_llm_tokens(llm: Any, formatted_prompt: str):
    """
    Generator that yields string tokens from the LLM for streaming display.

    Works with st.write_stream() — yields plain strings, not AIMessage objects.

    Args:
        llm: Language model instance
        formatted_prompt: The fully formatted prompt string

    Yields:
        str: Individual text tokens
    """
    for chunk in llm.stream(formatted_prompt):
        # LangChain chat models yield AIMessageChunk objects
        if hasattr(chunk, "content"):
            yield chunk.content
        else:
            yield str(chunk)
