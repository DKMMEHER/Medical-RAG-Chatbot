"""
Integration tests: End-to-end RAG pipeline

Tests the full query flow from app.py using mocked external dependencies:
  validate_environment → get_rag_prompt → prepare_rag_context → validate_response

No real API calls are made: the LLM and FAISS vectorstore are both mocked.
"""

import pytest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_guardrails_passthrough():
    """
    Return a MagicMock OutputGuardrails that marks every response as safe
    and returns the output unchanged.
    """
    guardrails = MagicMock()
    guardrails.validate_output.side_effect = (
        lambda llm_output, query, context, **kwargs: (
            True,  # is_safe
            [],  # issues
            llm_output,  # safe_output
        )
    )
    guardrails.get_fallback_response.return_value = (
        "I'm sorry, I cannot assist with that request."
    )
    return guardrails


def _make_guardrails_blocking():
    """
    Return a MagicMock OutputGuardrails that blocks every response (PII found).
    """
    from src.content_analyzer.config import ValidationIssue, ValidationSeverity

    block_issue = ValidationIssue(
        issue_type="PII_SSN",
        severity=ValidationSeverity.CRITICAL,
        description="SSN detected",
    )
    guardrails = MagicMock()
    guardrails.validate_output.side_effect = (
        lambda llm_output, query, context, **kwargs: (
            False,
            [block_issue],
            "I'm sorry, I cannot assist with that request.",
        )
    )
    guardrails.get_fallback_response.return_value = (
        "I'm sorry, I cannot assist with that request."
    )
    return guardrails


# ---------------------------------------------------------------------------
# Tests: get_rag_prompt
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGetRagPromptIntegration:
    """get_rag_prompt() returns a usable prompt template."""

    def test_prompt_is_not_none(self):
        import app as app_module

        prompt = app_module.get_rag_prompt()
        assert prompt is not None

    def test_prompt_has_context_variable(self):
        """Prompt template must expose a {context} input variable."""
        import app as app_module

        prompt = app_module.get_rag_prompt()
        assert "{context}" in prompt, (
            f"Expected '{{context}}' in prompt template, got: {prompt}"
        )

    def test_prompt_has_input_variable(self):
        """Prompt template must expose an {input} input variable."""
        import app as app_module

        prompt = app_module.get_rag_prompt()
        assert "{input}" in prompt, (
            f"Expected '{{input}}' in prompt template, got: {prompt}"
        )

    def test_fallback_prompt_created_when_file_missing(self, monkeypatch):
        """create_fallback_prompt() is used when the prompt file is absent."""
        import app as app_module
        from pathlib import Path

        # Mock Path.exists to return False ONLY for the prompt file
        original_exists = Path.exists

        def patched_exists(self):
            if "medical_assistant.txt" in str(self):
                return False
            return original_exists(self)

        monkeypatch.setattr(Path, "exists", patched_exists)

        prompt = app_module.get_rag_prompt()
        assert prompt is not None
        assert "{context}" in prompt


# ---------------------------------------------------------------------------
# Tests: prepare_rag_context / validate_response
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestPrepareRagContextIntegration:
    """prepare_rag_context() retrieves docs and builds the prompt correctly."""

    def _get_prompt(self):
        import app as app_module

        return app_module.get_rag_prompt()

    def test_returns_tuple(self, mock_vectorstore):
        """A well-formed query returns (formatted_prompt, retrieved_docs)."""
        from src.rag.engine import prepare_rag_context

        prompt = self._get_prompt()

        result = prepare_rag_context(
            "What is diabetes?",
            mock_vectorstore,
            prompt,
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        formatted_prompt, docs = result
        assert isinstance(formatted_prompt, str)
        assert "{context}" not in formatted_prompt  # Should be formatted
        assert len(docs) > 0

    def test_calls_vectorstore_retriever(self, mock_vectorstore):
        """Retriever is invoked once per query."""
        from src.rag.engine import prepare_rag_context

        prompt = self._get_prompt()

        prepare_rag_context(
            "What is hypertension?",
            mock_vectorstore,
            prompt,
        )

        mock_vectorstore.similarity_search.assert_called_once()


@pytest.mark.integration
class TestValidateResponseIntegration:
    """validate_response() runs guardrails on the complete LLM output."""

    def test_validates_output_via_guardrails(self):
        """guardrails.validate_output is called once per validation."""
        from src.rag.engine import validate_response

        passthrough_guardrails = _make_guardrails_passthrough()

        validate_response(
            "Some medical answer about cholesterol.",
            "What is cholesterol?",
            [],
            passthrough_guardrails,
        )

        passthrough_guardrails.validate_output.assert_called_once()

    def test_unsafe_output_returns_fallback(self):
        """When guardrails block, returns (False, fallback)."""
        from src.rag.engine import validate_response

        blocking_guardrails = _make_guardrails_blocking()

        is_safe, answer = validate_response(
            "Patient SSN: 123-45-6789 needs treatment.",
            "Tell me about the patient.",
            [],
            blocking_guardrails,
        )

        assert is_safe is False
        assert "sorry" in answer.lower() or "cannot" in answer.lower()

    def test_clean_output_is_returned_unchanged(self):
        """Safe LLM output is returned as-is (no modification by guardrails)."""
        from src.rag.engine import validate_response

        passthrough_guardrails = _make_guardrails_passthrough()
        test_answer = "Diabetes is a chronic metabolic disease."

        is_safe, answer = validate_response(
            test_answer, "What is diabetes?", [], passthrough_guardrails
        )

        assert is_safe is True
        assert answer == test_answer
