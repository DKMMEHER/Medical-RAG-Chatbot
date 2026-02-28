"""
Simple RAG Evaluation Script for Medical Chatbot

This script provides basic evaluation metrics without requiring RAGAS:
- Answer generation for test questions
- Manual review of answers
- Basic similarity metrics
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
import pandas as pd
from datetime import datetime

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
from llm_factory import load_config, get_generation_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/evaluation_simple.log"),
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
    """Load test dataset from JSON file."""
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
    """Initialize RAG components (vectorstore, LLM, prompt)."""
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
    """Generate answers for test questions using the RAG system."""
    try:
        logger.info("Generating answers for test questions...")

        results = []

        for i, test_case in enumerate(test_data, 1):
            question = test_case["question"]
            logger.info(f"Processing question {i}/{len(test_data)}: {question[:50]}...")

            # Retrieve relevant documents
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)

            # # Format context
            # context = "\n\n".join(doc.page_content for doc in docs)

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
                    "question_id": i,
                    "question": question,
                    "generated_answer": answer,
                    "ground_truth": test_case["ground_truth"],
                    "num_contexts_retrieved": len(docs),
                    "contexts": [doc.page_content for doc in docs],
                    "answer_length": len(answer),
                    "context_total_length": sum(len(doc.page_content) for doc in docs),
                }
            )

            logger.info(f"Generated answer: {answer[:100]}...")

        logger.info(f"Successfully generated {len(results)} answers")
        return results

    except Exception as e:
        error_msg = f"Failed to generate answers: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def save_results(results: List[Dict], results_dir: str):
    """Save evaluation results to files."""
    try:
        logger.info(f"Saving results to {results_dir}")

        # Create results directory
        Path(results_dir).mkdir(parents=True, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results as JSON
        detailed_results_path = os.path.join(
            results_dir, f"simple_results_{timestamp}.json"
        )
        with open(detailed_results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved detailed results to {detailed_results_path}")

        # Create DataFrame for CSV
        df_data = []
        for r in results:
            df_data.append(
                {
                    "question_id": r["question_id"],
                    "question": r["question"],
                    "generated_answer": r["generated_answer"],
                    "ground_truth": r["ground_truth"],
                    "num_contexts_retrieved": r["num_contexts_retrieved"],
                    "contexts": r["contexts"],
                    "answer_length": r["answer_length"],
                    "context_total_length": r["context_total_length"],
                }
            )

        df = pd.DataFrame(df_data)

        # Save as CSV
        csv_path = os.path.join(results_dir, f"simple_results_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved CSV to {csv_path}")

        # Create comparison report
        report_path = os.path.join(results_dir, f"comparison_report_{timestamp}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("RAG EVALUATION - ANSWER COMPARISON REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of test cases: {len(results)}\n\n")

            for r in results:
                f.write("=" * 80 + "\n")
                f.write(f"Question {r['question_id']}\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"QUESTION:\n{r['question']}\n\n")
                f.write(f"GROUND TRUTH:\n{r['ground_truth']}\n\n")
                f.write(f"GENERATED ANSWER:\n{r['generated_answer']}\n\n")
                f.write("STATISTICS:\n")
                f.write(f"  - Contexts Retrieved: {r['num_contexts_retrieved']}\n")
                f.write(f"  - Answer Length: {r['answer_length']} characters\n")
                f.write(
                    f"  - Total Context Length: {r['context_total_length']} characters\n\n"
                )
                f.write("RETRIEVED CONTEXTS:\n")
                for idx, ctx in enumerate(r["contexts"], 1):
                    f.write(f"\nContext {idx}:\n{ctx[:200]}...\n")
                f.write("\n")

        logger.info(f"Saved comparison report to {report_path}")

        # Print summary to console
        print("\n" + "=" * 80)
        print("RAG EVALUATION - SUMMARY")
        print("=" * 80)
        print(f"\nNumber of test cases: {len(results)}")

        # Try to print statistics, handle any column name issues
        try:
            print("\nAverage Statistics:")
            print(
                f"  - Average contexts retrieved: {df['num_contexts_retrieved'].mean():.2f}"
            )
            print(
                f"  - Average answer length: {df['answer_length'].mean():.0f} characters"
            )
            print(
                f"  - Average context length: {df['context_total_length'].mean():.0f} characters"
            )
        except KeyError as e:
            logger.warning(f"Could not calculate statistics: {e}")
            print("\nNote: Some statistics could not be calculated")

        print("\n" + "=" * 80)
        print(f"\nResults saved to: {results_dir}")
        print(f"  - Detailed JSON: {detailed_results_path}")
        print(f"  - CSV: {csv_path}")
        print(f"  - Comparison Report: {report_path}")
        print("=" * 80 + "\n")

    except Exception as e:
        error_msg = f"Failed to save results: {str(e)}"
        logger.error(error_msg)
        raise EvaluationError(error_msg)


def main():
    """Main evaluation function"""

    print("=" * 80)
    print("MEDICAL CHATBOT - SIMPLE RAG EVALUATION")
    print("=" * 80)
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

        # Step 4: Save results
        print("💾 Step 4: Saving results...")
        save_results(results, RESULTS_DIR)
        print("✅ Results saved")
        print()

        print("=" * 80)
        print("✅ SUCCESS! Evaluation completed")
        print("=" * 80)
        print()
        print("📝 Next Steps:")
        print("  1. Review the comparison report to see generated vs expected answers")
        print("  2. Check the CSV for quantitative statistics")
        print("  3. For advanced metrics, install RAGAS and run evaluate_rag.py")
        print()

        logger.info("Evaluation completed successfully")
        return 0

    except EvaluationError as e:
        print()
        print("=" * 80)
        print("❌ EVALUATION ERROR")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("💡 Suggestions:")
        print("  - Ensure vector store is created (run create_memory_for_llm.py)")
        print(
            "  - Check API key in .env file (check config.yaml for which LLM is active)"
        )
        print("  - Verify test dataset exists")
        print()
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        return 1

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ UNEXPECTED ERROR")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
