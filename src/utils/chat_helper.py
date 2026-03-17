"""
Chat-related helper functions for the Medical Chatbot.
"""


def format_chat_history(messages: list, max_history: int = 10) -> str:
    """
    Format the recent chat history for inclusion in the LLM prompt.

    Args:
        messages: List of message dictionaries from st.session_state.messages
        max_history: Number of recent messages to include (default 10 = 5 exchanges)

    Returns:
        str: Formatted chat history string
    """
    if not messages:
        return "(No previous conversation)"

    recent = messages[-max_history:]
    formatted_lines = []

    for m in recent:
        role = "User" if m["role"] == "user" else "Assistant"
        # Truncate long messages to prevent prompt bloat while keeping recent context
        content = (
            m["content"][:300] + "..." if len(m["content"]) > 300 else m["content"]
        )
        formatted_lines.append(f"{role}: {content}")

    return "\n".join(formatted_lines)
