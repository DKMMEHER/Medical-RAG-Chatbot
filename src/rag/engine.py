import os
import tempfile
from typing import List, Tuple, Any, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from src.utils.logger import get_logger
from src.content_analyzer.utils import sanitize_filename

logger = get_logger(__name__)

from src.observability import trace_retrieval

# Cross-encoder model for re-ranking retrieved documents
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def rerank_documents(
    query: str,
    docs: List[Any],
    cross_encoder,
    top_k: int = 5,
) -> List[Any]:
    """
    Re-rank retrieved documents using a CrossEncoder model.

    The cross-encoder reads (query, document) pairs together and assigns a
    relevance score to each pair — far more accurate than the vector-distance
    approximation used by FAISS or BM25.

    Args:
        query:         The user's question.
        docs:          Candidate documents from the retrieval step.
        cross_encoder: A loaded `sentence_transformers.CrossEncoder` instance.
                       If None, docs are returned unchanged (graceful fallback).
        top_k:         Number of best documents to keep after re-ranking.

    Returns:
        A list of up to `top_k` documents, sorted by re-rank score (best first).
    """
    if cross_encoder is None or not docs:
        logger.debug("⚠️ Re-ranker not available — returning docs as-is")
        return docs[:top_k]

    try:
        pairs = [(query, doc.page_content) for doc in docs]
        scores = cross_encoder.predict(pairs)  # shape: (len(docs),)
        ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
        reranked = [doc for _, doc in ranked[:top_k]]
        logger.info(
            f"🎯 Re-ranked {len(docs)} → top {len(reranked)} docs "
            f"(best score: {ranked[0][0]:.3f})"
        )
        return reranked
    except Exception as exc:
        logger.warning(f"⚠️ Re-ranking failed — falling back to original order: {exc}")
        return docs[:top_k]


def build_bm25_retriever(vectorstore, k: int = 5):
    """
    Build a BM25Retriever from the documents stored in a FAISS vectorstore.
    Extracts raw documents from the FAISS docstore so BM25 can index them.
    """
    from langchain_community.retrievers.bm25 import BM25Retriever

    docs = list(vectorstore.docstore._dict.values())
    if not docs:
        logger.warning(
            "⚠️ BM25: No documents found in vectorstore docstore — BM25 skipped"
        )
        return None
    bm25 = BM25Retriever.from_documents(docs, k=k)
    logger.info(f"🔍 BM25 retriever built from {len(docs)} documents")
    return bm25


@trace_retrieval(name="medical_docs_retrieval")
def prepare_rag_context(
    query: str,
    vectorstore,
    prompt_template: str,
    history_str: str = "",
    bm25_retriever=None,
    cross_encoder=None,
    retrieval_k: int = 20,
    rerank_top_k: int = 5,
) -> Tuple[str, List[Any]]:
    """
    Retrieves relevant documents and builds the final RAG prompt.

    Pipeline:
      1. Retrieve a broad candidate set (retrieval_k=20) via hybrid or FAISS search.
      2. Re-rank with CrossEncoder to the best rerank_top_k=5 docs.
      3. Assemble context and format the final prompt.

    Falls back gracefully at each step when components are unavailable.
    """
    # ── Step 1: Broad retrieval ────────────────────────────────────────────
    if bm25_retriever is not None:
        try:
            from langchain.retrievers import EnsembleRetriever
        except ImportError:
            try:
                from langchain_community.retrievers import EnsembleRetriever
            except ImportError:
                # Fallback for newer LangChain v1.x structures
                from langchain_classic.retrievers import EnsembleRetriever

        faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": retrieval_k})
        ensemble = EnsembleRetriever(
            retrievers=[faiss_retriever, bm25_retriever],
            weights=[0.6, 0.4],
        )
        retrieved_docs = ensemble.invoke(query)
        logger.info(f"🔀 Hybrid retrieval (FAISS+BM25): {len(retrieved_docs)} docs")
    else:
        retrieved_docs = vectorstore.similarity_search(query, k=retrieval_k)
        logger.info(f"🔍 FAISS-only retrieval: {len(retrieved_docs)} docs")

    # ── Step 2: Re-rank ───────────────────────────────────────────────────
    final_docs = rerank_documents(
        query, retrieved_docs, cross_encoder, top_k=rerank_top_k
    )

    # ── Step 3: Build prompt ──────────────────────────────────────────────
    context = "\n---\n".join([doc.page_content for doc in final_docs])

    final_prompt = prompt_template.format(
        context=context,
        chat_history=history_str,
        input=query,
    )
    return final_prompt, final_docs


def rebuild_vectorstore_from_pdfs(
    pdf_files: list, embedding_model, _gcs_handler=None, mode: str = "add"
) -> Tuple[bool, str, int, Optional[Any]]:
    """
    Build or update the FAISS index from PDF files.
    """
    if not pdf_files:
        return False, "No files provided.", 0

    # Sanitize filenames for safety
    for pdf in pdf_files:
        original_name = pdf.get("name", "unknown.pdf")
        pdf["name"] = sanitize_filename(original_name)

    from langchain_experimental.text_splitter import SemanticChunker

    try:
        all_chunks = []
        # Use semantic chunking based on embeddings
        splitter = SemanticChunker(
            embedding_model, breakpoint_threshold_type="percentile"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            for pdf in pdf_files:
                tmp_file_path = os.path.join(tmp_dir, pdf["name"])
                with open(tmp_file_path, "wb") as f:
                    f.write(pdf["bytes"])

                try:
                    loader = PyPDFLoader(tmp_file_path)
                    docs = loader.load()
                    # Clean the source path metadata to be just the filename
                    for doc in docs:
                        doc.metadata["source"] = pdf["name"]

                    chunks = splitter.split_documents(docs)
                    all_chunks.extend(chunks)
                    logger.info(
                        f"📄 Processed {pdf['name']}: {len(chunks)} semantic chunks"
                    )
                except Exception as loader_err:
                    logger.error(f"Failed to load {pdf['name']}: {loader_err}")

        if not all_chunks:
            return False, "No chunks extracted from PDFs.", 0

        # Build index
        BATCH_SIZE = 100
        final_db = None

        # If adding to existing index, we need to load or start from it
        # Actually, in this function, we assume embedding_model is passed in.

        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i : i + BATCH_SIZE]
            batch_db = FAISS.from_documents(batch, embedding_model)
            if final_db is None:
                final_db = batch_db
            else:
                final_db.merge_from(batch_db)

        # Upload if GCS is enabled
        if _gcs_handler and _gcs_handler.gcs_enabled:
            with tempfile.TemporaryDirectory() as upload_dir:
                final_db.save_local(upload_dir)
                _gcs_handler.upload_faiss_index(upload_dir)

        return True, "Index updated successfully", len(all_chunks), final_db

    except Exception as e:
        logger.error(f"rebuild_vectorstore_from_pdfs failed: {e}", exc_info=True)
        return False, str(e), 0, None


def validate_response(
    llm_answer: str, original_query: str, retrieved_docs: list, guardrails
) -> Tuple[bool, str]:
    """
    Validates LLM output using guardrails and handles fallbacks.
    """
    if not guardrails:
        return True, llm_answer

    is_safe, issues, safe_output = guardrails.validate_output(
        llm_answer, original_query, [doc.page_content for doc in retrieved_docs]
    )

    if not is_safe:
        logger.error("❌ Output blocked by guardrails")
        if any(issue.issue_type.startswith("PII_") for issue in issues):
            fallback = guardrails.get_fallback_response("pii")
        elif any(issue.issue_type.startswith("TOXIC_") for issue in issues):
            fallback = guardrails.get_fallback_response("toxic")
        else:
            fallback = guardrails.get_fallback_response("safety")
        return False, fallback

    logger.info("✅ Output validated and safe")
    return True, safe_output
