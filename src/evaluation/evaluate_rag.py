"""
RAG Evaluation Script for Medical Chatbot

This script evaluates the RAG system using RAGAS metrics:
- Faithfulness: Measures factual consistency of the answer with the context
- Answer Relevancy: Measures how relevant the answer is to the question
- Context Precision: Measures if relevant context is ranked higher
- Context Recall: Measures if all relevant information is retrieved
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from dotenv import load_dotenv

# Add project root to sys.path to allow consistent imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from src.model.llm_factory import load_config, get_generation_llm
except ImportError:
    # Fallback for different execution contexts
    try:
        from llm_factory import load_config, get_generation_llm
    except ImportError:
        logger.error("Could not import llm_factory. Ensure src/model is in PYTHONPATH.")
        sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/evaluation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Load configuration
CONFIG = load_config()

# Constants from config
DB_FAISS_PATH = CONFIG["vectorstore"]["path"]
TEST_DATASET_PATH = CONFIG["evaluation"]["test_dataset_path"]
RESULTS_DIR = CONFIG["evaluation"]["results_dir"]
DEFAULT_EMBEDDING_MODEL = CONFIG["embedding"]["model"]


class EvaluationError(Exception):
    """Custom exception for evaluation errors"""

    pass


def load_test_dataset(dataset_path: str) -> List[Dict]:
    """
    Load test dataset from JSON file.

    Args:
        dataset_path: Path to test dataset JSON file

    Returns:
        List[Dict]: List of test cases

    Raises:
        EvaluationError: If dataset loading fails
    """
    try:
        logger.info(f"Loading test dataset from {dataset_path}")

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Test dataset not found: {dataset_path}")

        with open(dataset_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)

        if not test_data:
            raise ValueError("Test dataset is empty")

        logger.info(f"Loaded {len(test_data)} test cases")
        return test_data

    except Exception as e:
        error_msg = f"Failed to load test dataset: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def initialize_rag_components():
    """
    Initialize RAG components (vectorstore, LLM, prompt).

    Returns:
        tuple: (vectorstore, llm, prompt)

    Raises:
        EvaluationError: If initialization fails
    """
    try:
        logger.info("Initializing RAG components...")

        # Load embedding model
        logger.info(f"Loading embedding model: {DEFAULT_EMBEDDING_MODEL}")
        embedding_model = HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL)

        # Load vector store
        logger.info(f"Loading vector store from {DB_FAISS_PATH}")
        if not os.path.exists(DB_FAISS_PATH):
            raise FileNotFoundError(f"Vector store not found: {DB_FAISS_PATH}")

        vectorstore = FAISS.load_local(
            DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True
        )

        # Initialize LLM from config
        active_llm = CONFIG.get("active_llm", "groq")
        logger.info(f"Initializing LLM from config: {active_llm}")
        llm = get_generation_llm(CONFIG)

        # Create prompt template
        template = """You are a helpful medical assistant. Use the following context to answer the user's question.
If you don't know the answer based on the context, say so - don't make up information.

Context:
{context}

Question: {input}

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        logger.info("RAG components initialized successfully")
        return vectorstore, llm, prompt

    except Exception as e:
        error_msg = f"Failed to initialize RAG components: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def generate_answers(test_data: List[Dict], vectorstore, llm, prompt) -> List[Dict]:
    """
    Generate answers for test questions using the RAG system.

    Args:
        test_data: List of test cases
        vectorstore: FAISS vector store
        llm: Language model
        prompt: Prompt template

    Returns:
        List[Dict]: Test data with generated answers and contexts
    """
    try:
        logger.info("Generating answers for test questions...")

        results = []

        for i, test_case in enumerate(test_data, 1):
            question = test_case["question"]
            logger.info(f"Processing question {i}/{len(test_data)}: {question[:50]}...")

            # Retrieve relevant documents
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)

            # Format context
            context = "\n\n".join(doc.page_content for doc in docs)

            # Create RAG chain
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            rag_chain = (
                {"context": retriever | format_docs, "input": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            # Generate answer
            answer = rag_chain.invoke(question)

            # Store result
            results.append(
                {
                    "question": question,
                    "answer": answer,
                    "contexts": [doc.page_content for doc in docs],
                    "ground_truth": test_case["ground_truth"],
                }
            )

            logger.info(f"Generated answer: {answer[:100]}...")

        logger.info(f"Successfully generated {len(results)} answers")
        return results

    except Exception as e:
        error_msg = f"Failed to generate answers: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def evaluate_rag_system(results: List[Dict]) -> Dict:
    """
    Evaluate RAG system using RAGAS metrics.

    Args:
        results: List of results with questions, answers, contexts, and ground truths

    Returns:
        Dict: Evaluation results

    Raises:
        EvaluationError: If evaluation fails
    """
    try:
        logger.info("Evaluating RAG system with RAGAS metrics...")

        # Prepare dataset for RAGAS
        data = {
            "question": [r["question"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results],
        }

        dataset = Dataset.from_dict(data)

        # Get evaluation LLM from config
        eval_llm_name = CONFIG.get("evaluation_llm", "groq")
        logger.info(f"Using evaluation LLM from config: {eval_llm_name}")

        # RAGAS 0.4.3 uses OpenAI by default
        # We need to set OPENAI_API_KEY for RAGAS to work
        # If using Groq, we can set it to use Groq's OpenAI-compatible endpoint
        if eval_llm_name == "groq":
            # RAGAS will use OpenAI client, but we can't easily override it
            # Best option: Use OpenAI for evaluation or accept default behavior
            logger.warning(
                "RAGAS 0.4.3 primarily supports OpenAI. Using default OpenAI configuration."
            )
            logger.warning(
                "For best results, set OPENAI_API_KEY or use evaluation_llm: 'openai' in config.yaml"
            )

        # Run evaluation with default RAGAS configuration
        logger.info("Running RAGAS evaluation...")
        evaluation_result = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )

        logger.info("Evaluation completed successfully")
        return evaluation_result

    except Exception as e:
        error_msg = f"Failed to evaluate RAG system: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def save_results(results: List[Dict], evaluation_result, results_dir: str):
    """
    Save evaluation results to files.

    Args:
        results: List of results with questions, answers, contexts
        evaluation_result: RAGAS evaluation results
        results_dir: Directory to save results
    """
    try:
        logger.info(f"Saving results to {results_dir}")

        # Create results directory
        Path(results_dir).mkdir(parents=True, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        detailed_results_path = os.path.join(
            results_dir, f"detailed_results_{timestamp}.json"
        )
        with open(detailed_results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved detailed results to {detailed_results_path}")

        # Convert evaluation results to DataFrame
        df = evaluation_result.to_pandas()

        # Save as CSV
        csv_path = os.path.join(results_dir, f"evaluation_metrics_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved metrics to {csv_path}")

        # Save summary
        summary_path = os.path.join(results_dir, f"summary_{timestamp}.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("RAG EVALUATION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of test cases: {len(results)}\n\n")
            f.write("RAGAS Metrics:\n")
            f.write("-" * 60 + "\n")

            # Calculate average scores
            for metric in [
                "faithfulness",
                "answer_relevancy",
                "context_precision",
                "context_recall",
            ]:
                if metric in df.columns:
                    avg_score = df[metric].mean()
                    f.write(f"{metric.replace('_', ' ').title()}: {avg_score:.4f}\n")

            f.write("\n" + "=" * 60 + "\n")

        logger.info(f"Saved summary to {summary_path}")

        # Print summary to console
        print("\n" + "=" * 60)
        print("RAG EVALUATION SUMMARY")
        print("=" * 60)
        print(f"\nNumber of test cases: {len(results)}\n")
        print("RAGAS Metrics:")
        print("-" * 60)

        for metric in [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ]:
            if metric in df.columns:
                avg_score = df[metric].mean()
                print(f"{metric.replace('_', ' ').title()}: {avg_score:.4f}")

        print("\n" + "=" * 60)
        print(f"\nResults saved to: {results_dir}")
        print("=" * 60 + "\n")

    except Exception as e:
        error_msg = f"Failed to save results: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def main():
    """Main evaluation function"""

    # Extra check for API keys in CI
    if not os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        logger.error(
            "❌ No API keys found (neither GROQ_API_KEY nor OPENAI_API_KEY). Evaluation cannot proceed."
        )
        return 1

    print("=" * 60)
    print("MEDICAL CHATBOT - RAG EVALUATION")
    print("=" * 60)
    print()

    try:
        # Step 1: Load test dataset
        print("📋 Step 1: Loading test dataset...")
        test_data = load_test_dataset(TEST_DATASET_PATH)
        print(f"✅ Loaded {len(test_data)} test cases")
        print()

        # Step 2: Initialize RAG components
        print("🔧 Step 2: Initializing RAG components...")
        vectorstore, llm, prompt = initialize_rag_components()
        print("✅ RAG components initialized")
        print()

        # Step 3: Generate answers
        print("🤖 Step 3: Generating answers...")
        results = generate_answers(test_data, vectorstore, llm, prompt)
        print(f"✅ Generated {len(results)} answers")
        print()

        # Step 4: Evaluate with RAGAS
        print("📊 Step 4: Evaluating with RAGAS metrics...")
        evaluation_result = evaluate_rag_system(results)
        print("✅ Evaluation completed")
        print()

        # Step 5: Save results
        print("💾 Step 5: Saving results...")
        save_results(results, evaluation_result, RESULTS_DIR)
        print("✅ Results saved")
        print()

        logger.info("Evaluation completed successfully")
        return 0

    except EvaluationError as e:
        print()
        print("=" * 60)
        print("❌ EVALUATION ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        print("💡 Suggestions:")
        print("  - Ensure vector store is created (run create_memory_for_llm.py)")
        print("  - Check GROQ_API_KEY in .env file")
        print("  - Verify test dataset exists")
        print()
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        return 1

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
