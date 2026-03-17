"""
Unit tests for src/rag/engine.py — covering:
  - prepare_rag_context: FAISS-only (fallback) path
  - prepare_rag_context: Hybrid (FAISS + BM25) path using EnsembleRetriever
  - build_bm25_retriever: happy path
  - build_bm25_retriever: empty docstore (graceful skip)
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch, mock_open
from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_sys_modules():
    """Ensure sys.modules is clean of our mocks before and after each test."""
    yield
    mocked_modules = [
        "langchain.retrievers",
        "langchain.retrievers.ensemble",
        "langchain_community.retrievers",
        "langchain_community.retrievers.ensemble",
        "langchain_classic.retrievers",
        "langchain_classic.retrievers.ensemble",
    ]
    for mod in mocked_modules:
        if mod in sys.modules:
            del sys.modules[mod]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_vectorstore(docs=None):
    """Return a mock FAISS vectorstore with a seeded docstore."""
    if docs is None:
        docs = [
            Document(page_content="Hypertension is high blood pressure.", metadata={}),
            Document(page_content="Metformin 500mg is used for diabetes.", metadata={}),
        ]
    vs = MagicMock()
    vs.docstore._dict = {str(i): d for i, d in enumerate(docs)}
    vs.similarity_search.return_value = docs
    faiss_ret = MagicMock()
    faiss_ret.invoke.return_value = docs
    vs.as_retriever.return_value = faiss_ret
    return vs, docs


def _inject_ensemble_module(docs):
    """
    Inject fake EnsembleRetriever modules into sys.modules to handle various
    LangChain version structures used in the revised engine.py fallback logic.
    """
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = docs

    mock_cls = MagicMock(return_value=mock_instance)

    # Inject into various possible locations to satisfy engine.py fallback logic
    # 1. langchain.retrievers
    fake_langchain_ret = types.ModuleType("langchain.retrievers")
    fake_langchain_ret.EnsembleRetriever = mock_cls
    sys.modules["langchain.retrievers"] = fake_langchain_ret

    # 2. langchain_community.retrievers
    fake_community_ret = types.ModuleType("langchain_community.retrievers")
    fake_community_ret.EnsembleRetriever = mock_cls
    sys.modules["langchain_community.retrievers"] = fake_community_ret

    # 3. langchain_classic.retrievers
    fake_classic_ret = types.ModuleType("langchain_classic.retrievers")
    fake_classic_ret.EnsembleRetriever = mock_cls
    sys.modules["langchain_classic.retrievers"] = fake_classic_ret

    return mock_cls, mock_instance


PROMPT_TEMPLATE = "Context: {context}\nHistory: {chat_history}\nQuestion: {input}"


# ---------------------------------------------------------------------------
# prepare_rag_context — FAISS-only (no bm25_retriever)
# ---------------------------------------------------------------------------


class TestPrepareRagContextFaissOnly:
    def test_calls_similarity_search(self):
        """Without BM25, falls back to vectorstore.similarity_search."""
        from src.rag.engine import prepare_rag_context

        vs, docs = _make_vectorstore()
        prompt, retrieved = prepare_rag_context(
            query="What is hypertension?",
            vectorstore=vs,
            prompt_template=PROMPT_TEMPLATE,
        )

        vs.similarity_search.assert_called_once_with("What is hypertension?", k=20)
        assert retrieved == docs

    def test_prompt_contains_context(self):
        """The final prompt embeds the document text."""
        from src.rag.engine import prepare_rag_context

        vs, docs = _make_vectorstore()
        prompt, _ = prepare_rag_context(
            query="diabetes",
            vectorstore=vs,
            prompt_template=PROMPT_TEMPLATE,
        )

        assert "Hypertension is high blood pressure." in prompt
        assert "diabetes" in prompt

    def test_history_embedded_in_prompt(self):
        """Chat history is forwarded into the prompt."""
        from src.rag.engine import prepare_rag_context

        vs, _ = _make_vectorstore()
        prompt, _ = prepare_rag_context(
            query="test query",
            vectorstore=vs,
            prompt_template=PROMPT_TEMPLATE,
            history_str="User: hello\nAssistant: hi",
        )

        assert "User: hello" in prompt


# ---------------------------------------------------------------------------
# prepare_rag_context — Hybrid (EnsembleRetriever)
# ---------------------------------------------------------------------------


class TestPrepareRagContextHybrid:
    def test_uses_ensemble_when_bm25_provided(self):
        """With bm25_retriever, EnsembleRetriever is invoked instead of similarity_search."""
        from src.rag.engine import prepare_rag_context

        vs, docs = _make_vectorstore()
        mock_bm25 = MagicMock()
        mock_cls, mock_instance = _inject_ensemble_module(docs)

        try:
            prompt, retrieved = prepare_rag_context(
                query="Metformin dosage",
                vectorstore=vs,
                prompt_template=PROMPT_TEMPLATE,
                bm25_retriever=mock_bm25,
            )
        finally:
            sys.modules.pop("langchain.retrievers.ensemble", None)

        mock_cls.assert_called_once()
        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["weights"] == [0.6, 0.4]
        assert len(call_kwargs["retrievers"]) == 2
        # similarity_search must NOT be called — that's the FAISS-only path
        vs.similarity_search.assert_not_called()
        assert retrieved == docs

    def test_as_retriever_called_with_correct_k(self):
        """FAISS side of ensemble uses k=20 search kwargs."""
        from src.rag.engine import prepare_rag_context

        vs, docs = _make_vectorstore()
        mock_bm25 = MagicMock()
        _inject_ensemble_module(docs)

        try:
            prepare_rag_context(
                query="ICD-10 E11.9",
                vectorstore=vs,
                prompt_template=PROMPT_TEMPLATE,
                bm25_retriever=mock_bm25,
            )
        finally:
            sys.modules.pop("langchain.retrievers.ensemble", None)

        vs.as_retriever.assert_called_once_with(search_kwargs={"k": 20})


# ---------------------------------------------------------------------------
# build_bm25_retriever
# ---------------------------------------------------------------------------


class TestBuildBm25Retriever:
    def test_returns_bm25_retriever(self):
        """Returns a BM25Retriever for a vectorstore that has documents."""
        from src.rag.engine import build_bm25_retriever

        vs, _ = _make_vectorstore()
        mock_bm25 = MagicMock()

        with patch(
            "langchain_community.retrievers.bm25.BM25Retriever.from_documents",
            return_value=mock_bm25,
        ) as mock_from_docs:
            result = build_bm25_retriever(vs, k=5)

        mock_from_docs.assert_called_once()
        assert result == mock_bm25

    def test_returns_none_for_empty_docstore(self):
        """Returns None gracefully when docstore is empty — no docs to index."""
        from src.rag.engine import build_bm25_retriever

        vs, _ = _make_vectorstore(docs=[])
        result = build_bm25_retriever(vs)

        assert result is None


# ---------------------------------------------------------------------------
# rerank_documents
# ---------------------------------------------------------------------------


class TestRerankDocuments:
    def test_rerank_sorts_by_score(self):
        """Verify that documents are re-ordered based on cross-encoder scores."""
        from src.rag.engine import rerank_documents

        docs = [
            Document(page_content="Chunk A", metadata={"id": "A"}),
            Document(page_content="Chunk B", metadata={"id": "B"}),
            Document(page_content="Chunk C", metadata={"id": "C"}),
        ]

        mock_encoder = MagicMock()
        # Mock scores: B=0.9, A=0.1, C=0.5
        mock_encoder.predict.return_value = [0.1, 0.9, 0.5]

        result = rerank_documents("query", docs, mock_encoder, top_k=2)

        assert len(result) == 2
        assert result[0].page_content == "Chunk B"  # Highest score
        assert result[1].page_content == "Chunk C"  # Second highest

        # Verify predict called with correct pairs
        mock_encoder.predict.assert_called_once_with(
            [
                ("query", "Chunk A"),
                ("query", "Chunk B"),
                ("query", "Chunk C"),
            ]
        )

    def test_rerank_graceful_fallback_no_encoder(self):
        """If encoder is None, return first top_k docs as-is."""
        from src.rag.engine import rerank_documents

        docs = [Document(page_content=f"D{i}") for i in range(10)]

        result = rerank_documents("query", docs, None, top_k=3)
        assert len(result) == 3
        assert result[0].page_content == "D0"

    def test_rerank_handles_exception(self):
        """If prediction fails, fall back to original order."""
        from src.rag.engine import rerank_documents

        docs = [Document(page_content="D1"), Document(page_content="D2")]
        mock_encoder = MagicMock()
        mock_encoder.predict.side_effect = Exception("Model crash")

        result = rerank_documents("q", docs, mock_encoder, top_k=2)
        assert result == docs  # Original order preserved


# ---------------------------------------------------------------------------
# prepare_rag_context (Integration with Re-ranker)
# ---------------------------------------------------------------------------


class TestPrepareRagContextIntegration:
    @patch("src.rag.engine.rerank_documents")
    def test_calls_reranker_with_broad_k(self, mock_rerank):
        """Verify prepare_rag_context retrieves k=20 and then calls rerank."""
        from src.rag.engine import prepare_rag_context

        vs, docs = _make_vectorstore()

        mock_rerank.return_value = docs[:1]

        prepare_rag_context(
            "q",
            vs,
            PROMPT_TEMPLATE,
            cross_encoder=MagicMock(),
            retrieval_k=20,
            rerank_top_k=5,
        )

        # Verify FAISS was called with k=20
        vs.similarity_search.assert_called_once_with("q", k=20)
        # Verify rerank was called with the result
        mock_rerank.assert_called_once()
        args, kwargs = mock_rerank.call_args
        assert kwargs["top_k"] == 5


# ---------------------------------------------------------------------------
# validate_response
# ---------------------------------------------------------------------------


class TestValidateResponse:
    def test_validate_response_safe(self):
        """Returns (True, output) for safe content"""
        from src.rag.engine import validate_response

        mock_guardrails = MagicMock()
        mock_guardrails.validate_output.return_value = (
            True,
            [],
            "This is a safe medical answer.",
        )

        is_safe, output = validate_response(
            "This is a safe medical answer.",
            "What is diabetes?",
            [],
            mock_guardrails,
        )

        assert is_safe is True
        assert "safe medical answer" in output
        # verify args: answer, query, context
        mock_guardrails.validate_output.assert_called_once_with(
            "This is a safe medical answer.", "What is diabetes?", []
        )

    def test_validate_response_blocked_by_guardrails(self):
        """Returns (False, fallback) when guardrails block the output"""
        from src.rag.engine import validate_response
        from src.content_analyzer.config import ValidationIssue, ValidationSeverity

        pii_issue = ValidationIssue(
            issue_type="PII_SSN",
            severity=ValidationSeverity.CRITICAL,
            description="SSN detected",
            matched_text="12***89",
            position=8,
        )
        mock_guardrails = MagicMock()
        mock_guardrails.validate_output.return_value = (False, [pii_issue], "")
        mock_guardrails.get_fallback_response.return_value = (
            "I apologize, but the response contained sensitive information."
        )

        is_safe, output = validate_response(
            "Patient SSN: 123-45-6789",
            "Tell me about SSN 123-45-6789",
            [],
            mock_guardrails,
        )

        assert is_safe is False
        assert "sensitive information" in output


# ---------------------------------------------------------------------------
# rebuild_vectorstore_from_pdfs
# ---------------------------------------------------------------------------


class TestRebuildVectorstoreFromPdfs:
    @patch("src.rag.engine.PyPDFLoader")
    @patch("langchain_experimental.text_splitter.SemanticChunker")
    @patch("langchain_community.vectorstores.FAISS.from_documents")
    @patch("src.rag.engine.tempfile.TemporaryDirectory")
    @patch("os.path.exists")
    def test_success(
        self,
        mock_exists,
        mock_temp_dir_cls,
        mock_faiss_from_docs,
        mock_chunker_cls,
        mock_pdf_loader_cls,
    ):
        """Successfully rebuilds vectorstore from PDFs."""
        from src.rag.engine import rebuild_vectorstore_from_pdfs

        mock_pdf = {"name": "test.pdf", "bytes": b"pdf content"}
        mock_exists.return_value = False

        # Setup loader
        mock_loader = MagicMock()
        mock_loader.load.return_value = [Document(page_content="doc1")]
        mock_pdf_loader_cls.return_value = mock_loader

        # Setup splitter (SemanticChunker)
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [Document(page_content="chunk1")]
        mock_chunker_cls.return_value = mock_splitter

        # Setup FAISS
        mock_faiss_instance = MagicMock()
        mock_faiss_from_docs.return_value = mock_faiss_instance

        # Setup temp dir
        mock_temp_dir = MagicMock()
        mock_temp_dir.__enter__.return_value = "mock_temp_dir"
        mock_temp_dir_cls.return_value = mock_temp_dir

        # Correctly mock the open() for filename creation
        # Since we use 'with open(tmp_file_path, "wb") as f:', we need to patch builtins.open

        mock_handler = MagicMock()
        mock_handler.gcs_enabled = True
        mock_embeddings = MagicMock()

        with patch("builtins.open", mock_open()):
            success, msg, count, db = rebuild_vectorstore_from_pdfs(
                [mock_pdf], mock_embeddings, mock_handler
            )

        assert success is True
        assert count == 1
        assert db == mock_faiss_instance
        mock_faiss_instance.save_local.assert_called_once()
        mock_handler.upload_faiss_index.assert_called_once()

    def test_no_pdfs(self):
        from src.rag.engine import rebuild_vectorstore_from_pdfs

        success, msg, count, db = rebuild_vectorstore_from_pdfs([], None)
        assert success is False
        assert "No files provided" in msg
