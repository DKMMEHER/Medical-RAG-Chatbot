"""
Human Evaluation Interface for RAG System

This script provides a Streamlit-based interface for human annotators to evaluate
RAG-generated answers. It implements gold standard evaluation with:
- Multi-dimensional rating scales
- Multiple annotator support
- Inter-annotator agreement calculation
- Comparison with automated metrics
"""

import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from sklearn.metrics import cohen_kappa_score

# Detect project root (where config.yaml is)
current_dir = Path(__file__).parent
if (current_dir / "config.yaml").exists():
    PROJECT_ROOT = current_dir
elif (current_dir.parent / "config.yaml").exists():
    PROJECT_ROOT = current_dir.parent
else:
    PROJECT_ROOT = current_dir

# Constants
EVALUATION_DIR = PROJECT_ROOT / "evaluation" / "human_annotations"
RESULTS_FILE = PROJECT_ROOT / "evaluation" / "human_annotations" / "annotations.json"
GUIDELINES_FILE = PROJECT_ROOT / "evaluation" / "human_annotations" / "guidelines.md"

# Rating scales
RATING_SCALES = {
    "accuracy": {
        "label": "Accuracy",
        "description": "Is the answer factually correct based on the context?",
        "scale": {
            1: "Completely incorrect",
            2: "Mostly incorrect",
            3: "Partially correct",
            4: "Mostly correct",
            5: "Completely correct",
        },
    },
    "completeness": {
        "label": "Completeness",
        "description": "Does the answer cover all important aspects of the question?",
        "scale": {
            1: "Missing all key points",
            2: "Missing most key points",
            3: "Covers some key points",
            4: "Covers most key points",
            5: "Covers all key points",
        },
    },
    "relevance": {
        "label": "Relevance",
        "description": "Is the answer relevant to the question asked?",
        "scale": {
            1: "Not relevant at all",
            2: "Slightly relevant",
            3: "Moderately relevant",
            4: "Very relevant",
            5: "Perfectly relevant",
        },
    },
    "clarity": {
        "label": "Clarity",
        "description": "Is the answer clear and easy to understand?",
        "scale": {
            1: "Very confusing",
            2: "Somewhat confusing",
            3: "Acceptable clarity",
            4: "Clear",
            5: "Very clear",
        },
    },
    "helpfulness": {
        "label": "Helpfulness",
        "description": "Would this answer be helpful to someone asking this question?",
        "scale": {
            1: "Not helpful at all",
            2: "Slightly helpful",
            3: "Moderately helpful",
            4: "Very helpful",
            5: "Extremely helpful",
        },
    },
}


def initialize_directories():
    """Create necessary directories for human evaluation."""
    Path(EVALUATION_DIR).mkdir(parents=True, exist_ok=True)


def load_test_cases() -> List[Dict]:
    """Load test cases from the evaluation dataset."""
    test_dataset_path = PROJECT_ROOT / "evaluation" / "test_dataset.json"

    if not test_dataset_path.exists():
        st.error(f"Test dataset not found: {test_dataset_path}")
        st.info(
            "Please make sure you're running this from the project directory and have run an evaluation first."
        )
        return []

    with open(test_dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_generated_answers() -> Optional[pd.DataFrame]:
    """Load the most recent evaluation results."""
    results_dir = PROJECT_ROOT / "evaluation" / "results"

    if not results_dir.exists():
        return None

    # Find most recent CSV file
    csv_files = list(results_dir.glob("evaluation_metrics_*.csv"))
    if not csv_files:
        # Try simple results
        csv_files = list(results_dir.glob("simple_results_*.csv"))

    if not csv_files:
        return None

    latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
    return pd.read_csv(latest_file)


def load_annotations() -> Dict:
    """Load existing annotations."""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"annotations": [], "metadata": {"created": datetime.now().isoformat()}}


def save_annotation(annotation: Dict):
    """Save a new annotation."""
    data = load_annotations()

    # Check if this question was already annotated by this annotator
    existing_idx = None
    for idx, ann in enumerate(data["annotations"]):
        if (
            ann["question_id"] == annotation["question_id"]
            and ann["annotator_id"] == annotation["annotator_id"]
        ):
            existing_idx = idx
            break

    if existing_idx is not None:
        # Update existing annotation
        data["annotations"][existing_idx] = annotation
    else:
        # Add new annotation
        data["annotations"].append(annotation)

    data["metadata"]["last_updated"] = datetime.now().isoformat()

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_inter_annotator_agreement(annotations: List[Dict]) -> Dict:
    """Calculate inter-annotator agreement using Cohen's Kappa."""
    if len(annotations) < 2:
        return {"error": "Need at least 2 annotators"}

    # Group by question
    by_question = {}
    for ann in annotations:
        q_id = ann["question_id"]
        if q_id not in by_question:
            by_question[q_id] = []
        by_question[q_id].append(ann)

    # Calculate agreement for each dimension
    agreements = {}

    for dimension in RATING_SCALES.keys():
        # Get all pairs of annotators for each question
        all_ratings_a = []
        all_ratings_b = []

        for q_id, anns in by_question.items():
            if len(anns) >= 2:
                # Take first two annotators for simplicity
                all_ratings_a.append(anns[0]["ratings"][dimension])
                all_ratings_b.append(anns[1]["ratings"][dimension])

        if len(all_ratings_a) > 0:
            kappa = cohen_kappa_score(all_ratings_a, all_ratings_b)
            agreements[dimension] = {
                "kappa": round(kappa, 3),
                "interpretation": interpret_kappa(kappa),
            }

    return agreements


def interpret_kappa(kappa: float) -> str:
    """Interpret Cohen's Kappa value."""
    if kappa < 0:
        return "Poor (worse than random)"
    elif kappa < 0.20:
        return "Slight agreement"
    elif kappa < 0.40:
        return "Fair agreement"
    elif kappa < 0.60:
        return "Moderate agreement"
    elif kappa < 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"


def create_guidelines():
    """Create annotation guidelines document."""
    guidelines = """# Human Evaluation Guidelines for Medical Chatbot RAG System

## Purpose
This evaluation helps us understand how well our RAG system answers medical questions. Your honest, careful ratings are crucial for improving the system.

## Important Notes
- **Medical Accuracy**: You are NOT expected to verify medical facts. Rate based on whether the answer seems consistent with the provided context.
- **Context-Based**: Judge answers based on the retrieved context shown, not your personal medical knowledge.
- **Be Consistent**: Try to apply the same standards across all questions.

## Rating Dimensions

### 1. Accuracy (1-5)
**Question**: Is the answer factually correct based on the context?

- **5 - Completely correct**: All facts match the context perfectly
- **4 - Mostly correct**: Minor inaccuracies or missing details
- **3 - Partially correct**: Some correct info, but significant errors
- **2 - Mostly incorrect**: More wrong than right
- **1 - Completely incorrect**: Contradicts the context or is totally wrong

**Example**:
- Context says: "Diabetes symptoms include frequent urination and thirst"
- Answer: "Symptoms are frequent urination and excessive thirst" → **5** (Correct)
- Answer: "Symptoms are headache and fever" → **1** (Incorrect)

### 2. Completeness (1-5)
**Question**: Does the answer cover all important aspects?

- **5 - Covers all key points**: Nothing important is missing
- **4 - Covers most key points**: One minor point missing
- **3 - Covers some key points**: Several important points missing
- **2 - Missing most key points**: Only mentions 1-2 points
- **1 - Missing all key points**: Doesn't address the question

**Example**:
- Question: "What are the symptoms of diabetes?"
- Context lists: thirst, urination, hunger, fatigue, blurred vision
- Answer mentions all 5 → **5**
- Answer mentions 3-4 → **4**
- Answer mentions 1-2 → **2**

### 3. Relevance (1-5)
**Question**: Is the answer relevant to what was asked?

- **5 - Perfectly relevant**: Directly answers the question
- **4 - Very relevant**: Answers the question with minor tangents
- **3 - Moderately relevant**: Partially answers, some off-topic info
- **2 - Slightly relevant**: Mostly off-topic
- **1 - Not relevant**: Doesn't address the question at all

**Example**:
- Question: "How is diabetes diagnosed?"
- Answer about diagnosis methods → **5**
- Answer about diabetes symptoms → **2** (Wrong topic)

### 4. Clarity (1-5)
**Question**: Is the answer clear and easy to understand?

- **5 - Very clear**: Simple, well-organized, easy to follow
- **4 - Clear**: Understandable with minor awkward phrasing
- **3 - Acceptable**: Understandable but could be clearer
- **2 - Somewhat confusing**: Hard to follow in places
- **1 - Very confusing**: Difficult to understand

### 5. Helpfulness (1-5)
**Question**: Would this answer help someone asking this question?

- **5 - Extremely helpful**: Provides exactly what's needed
- **4 - Very helpful**: Useful with minor gaps
- **3 - Moderately helpful**: Some useful info
- **2 - Slightly helpful**: Limited usefulness
- **1 - Not helpful**: Wouldn't help at all

## Tips for Good Annotations

1. **Read Carefully**: Read the question, context, and answer thoroughly
2. **Be Objective**: Don't let personal opinions influence ratings
3. **Use the Full Scale**: Don't just use 3-5; use 1-2 when appropriate
4. **Take Breaks**: Fatigue affects judgment; take breaks every 10-15 questions
5. **Ask Questions**: If unsure about guidelines, ask before rating

## Common Pitfalls to Avoid

❌ **Don't**: Rate based on your medical knowledge
✅ **Do**: Rate based on the provided context

❌ **Don't**: Give high scores just because the answer is long
✅ **Do**: Consider quality over quantity

❌ **Don't**: Rate all answers the same
✅ **Do**: Differentiate between good and bad answers

## Quality Checks

We may ask you to re-rate some questions to check consistency. This is normal and helps ensure data quality.

## Questions?

If you're unsure about how to rate something, make your best judgment and add a note in the comments field.
"""

    with open(GUIDELINES_FILE, "w", encoding="utf-8") as f:
        f.write(guidelines)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Human Evaluation - Medical Chatbot", page_icon="📝", layout="wide"
    )

    # Initialize
    initialize_directories()
    create_guidelines()

    # Sidebar
    st.sidebar.title("📝 Human Evaluation")
    st.sidebar.markdown("---")

    # Annotator ID
    annotator_id = st.sidebar.text_input(
        "Your Annotator ID",
        value=st.session_state.get("annotator_id", ""),
        help="Enter a unique identifier (e.g., your name or initials)",
    )

    if annotator_id:
        st.session_state.annotator_id = annotator_id

    # Mode selection
    mode = st.sidebar.radio(
        "Mode", ["Annotate", "View Results", "Guidelines", "Statistics"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Progress")

    # Load data
    annotations_data = load_annotations()
    test_cases = load_test_cases()
    generated_answers = load_generated_answers()

    if not annotator_id and mode == "Annotate":
        st.warning("⚠️ Please enter your Annotator ID in the sidebar to begin.")
        return

    # Show progress
    if mode == "Annotate":
        user_annotations = [
            a
            for a in annotations_data["annotations"]
            if a["annotator_id"] == annotator_id
        ]
        progress = len(user_annotations) / len(test_cases) if test_cases else 0
        st.sidebar.progress(progress)
        st.sidebar.write(f"{len(user_annotations)}/{len(test_cases)} completed")

    # Main content
    if mode == "Annotate":
        show_annotation_interface(test_cases, generated_answers, annotations_data)
    elif mode == "View Results":
        show_results(annotations_data)
    elif mode == "Guidelines":
        show_guidelines()
    elif mode == "Statistics":
        show_statistics(annotations_data)


def show_annotation_interface(test_cases, generated_answers, annotations_data):
    """Show the annotation interface."""
    st.title("📝 Answer Annotation")

    if not test_cases:
        st.error("No test cases found. Please run evaluation first.")
        return

    # Question selector
    question_ids = list(range(len(test_cases)))

    # Find next unannotated question
    annotator_id = st.session_state.annotator_id
    annotated_ids = {
        a["question_id"]
        for a in annotations_data["annotations"]
        if a["annotator_id"] == annotator_id
    }

    next_unannotated = None
    for qid in question_ids:
        if qid not in annotated_ids:
            next_unannotated = qid
            break

    default_idx = next_unannotated if next_unannotated is not None else 0

    selected_idx = st.selectbox(
        "Select Question",
        question_ids,
        index=default_idx,
        format_func=lambda x: f"Question {x + 1}"
        + (" ✅" if x in annotated_ids else ""),
    )

    test_case = test_cases[selected_idx]

    # Display question and context
    st.markdown("### Question")
    st.info(test_case["question"])

    # Get generated answer
    answer = None
    contexts = []

    if generated_answers is not None:
        try:
            row = generated_answers.iloc[selected_idx]
            answer = row.get("response", row.get("generated_answer", ""))

            # Parse contexts
            contexts_str = row.get("retrieved_contexts", row.get("contexts", ""))
            if isinstance(contexts_str, str):
                import ast

                try:
                    contexts = ast.literal_eval(contexts_str)
                except:
                    contexts = [contexts_str]
            elif isinstance(contexts_str, list):
                contexts = contexts_str
        except:
            pass

    if not answer:
        st.warning("No generated answer found. Please run evaluation first.")
        return

    # Display context
    with st.expander("📚 Retrieved Context", expanded=False):
        for i, ctx in enumerate(contexts, 1):
            st.markdown(f"**Context {i}:**")
            st.text(ctx[:500] + "..." if len(ctx) > 500 else ctx)
            st.markdown("---")

    # Display answer
    st.markdown("### Generated Answer")
    st.success(answer)

    # Display ground truth
    with st.expander("✅ Ground Truth (Reference Answer)", expanded=False):
        st.write(test_case["ground_truth"])

    st.markdown("---")

    # Rating interface
    st.markdown("### Rate This Answer")
    st.markdown("*Rate each dimension from 1 (worst) to 5 (best)*")

    # Load existing annotation if any
    existing_annotation = None
    for ann in annotations_data["annotations"]:
        if ann["question_id"] == selected_idx and ann["annotator_id"] == annotator_id:
            existing_annotation = ann
            break

    ratings = {}
    cols = st.columns(2)

    for idx, (dim_key, dim_info) in enumerate(RATING_SCALES.items()):
        col = cols[idx % 2]

        with col:
            st.markdown(f"**{dim_info['label']}**")
            st.caption(dim_info["description"])

            default_value = 3
            if existing_annotation:
                default_value = existing_annotation["ratings"].get(dim_key, 3)

            rating = st.radio(
                f"{dim_key}_rating",
                options=[1, 2, 3, 4, 5],
                index=default_value - 1,
                format_func=lambda x: f"{x} - {dim_info['scale'][x]}",
                key=f"rating_{dim_key}",
                label_visibility="collapsed",
            )
            ratings[dim_key] = rating

    # Comments
    st.markdown("### Additional Comments (Optional)")
    default_comments = existing_annotation["comments"] if existing_annotation else ""
    comments = st.text_area(
        "Any additional observations or notes?", value=default_comments, height=100
    )

    # Save button
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Save Annotation", type="primary", use_container_width=True):
            annotation = {
                "question_id": selected_idx,
                "question": test_case["question"],
                "annotator_id": annotator_id,
                "ratings": ratings,
                "comments": comments,
                "timestamp": datetime.now().isoformat(),
            }

            save_annotation(annotation)
            st.success("✅ Annotation saved!")
            st.rerun()

    with col2:
        if selected_idx < len(test_cases) - 1:
            if st.button("Next Question →", use_container_width=True):
                st.session_state.selected_idx = selected_idx + 1
                st.rerun()


def show_results(annotations_data):
    """Show annotation results."""
    st.title("📊 Annotation Results")

    if not annotations_data["annotations"]:
        st.info("No annotations yet. Start annotating to see results!")
        return

    # Convert to DataFrame
    df = pd.DataFrame(annotations_data["annotations"])

    # Summary statistics
    st.markdown("### Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Annotations", len(df))

    with col2:
        unique_annotators = df["annotator_id"].nunique()
        st.metric("Unique Annotators", unique_annotators)

    with col3:
        unique_questions = df["question_id"].nunique()
        st.metric("Questions Annotated", unique_questions)

    # Ratings breakdown
    st.markdown("### Average Ratings by Dimension")

    # Extract ratings
    ratings_df = pd.DataFrame(
        [ann["ratings"] for ann in annotations_data["annotations"]]
    )
    avg_ratings = ratings_df.mean().sort_values(ascending=False)

    # Display as bar chart
    st.bar_chart(avg_ratings)

    # Detailed table
    st.markdown("### Detailed Ratings")

    for dim in RATING_SCALES.keys():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{RATING_SCALES[dim]['label']}**")
        with col2:
            st.write(f"Avg: {avg_ratings[dim]:.2f}")
        with col3:
            st.write(f"Std: {ratings_df[dim].std():.2f}")

    # Show all annotations
    st.markdown("### All Annotations")
    st.dataframe(df, use_container_width=True)

    # Export button
    if st.button("📥 Export to CSV"):
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "annotations.csv", "text/csv")


def show_guidelines():
    """Show annotation guidelines."""
    st.title("📖 Annotation Guidelines")

    if os.path.exists(GUIDELINES_FILE):
        with open(GUIDELINES_FILE, "r", encoding="utf-8") as f:
            guidelines = f.read()
        st.markdown(guidelines)
    else:
        st.error("Guidelines file not found.")


def show_statistics(annotations_data):
    """Show statistical analysis."""
    st.title("📈 Statistical Analysis")

    if len(annotations_data["annotations"]) < 2:
        st.info("Need at least 2 annotations to calculate statistics.")
        return

    # Inter-annotator agreement
    st.markdown("### Inter-Annotator Agreement (Cohen's Kappa)")
    st.markdown("*Measures how much annotators agree with each other*")

    agreements = calculate_inter_annotator_agreement(annotations_data["annotations"])

    if "error" in agreements:
        st.warning(agreements["error"])
    else:
        for dim, stats in agreements.items():
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.write(f"**{RATING_SCALES[dim]['label']}**")
            with col2:
                st.metric("κ", stats["kappa"])
            with col3:
                st.write(stats["interpretation"])

    # Distribution of ratings
    st.markdown("### Rating Distributions")

    ratings_df = pd.DataFrame(
        [ann["ratings"] for ann in annotations_data["annotations"]]
    )

    for dim in RATING_SCALES.keys():
        st.markdown(f"**{RATING_SCALES[dim]['label']}**")
        dist = ratings_df[dim].value_counts().sort_index()
        st.bar_chart(dist)


if __name__ == "__main__":
    main()
