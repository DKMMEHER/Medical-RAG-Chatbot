"""
Complete RAG Pipeline with Content Validation
Demonstrates input validation, context validation, AND output validation

Run from project root:
    uv run example_complete_pipeline.py
"""

from Content_Analyzer import ContentValidator, OutputGuardrails, ValidationConfig


def complete_rag_pipeline_with_guardrails():
    """
    Complete RAG pipeline with 3-layer validation:
    1. Input Validation (user query)
    2. Context Validation (retrieved documents)
    3. Output Validation (LLM response)
    """
    
    print("\n" + "="*80)
    print("COMPLETE RAG PIPELINE WITH GUARDRAILS")
    print("="*80 + "\n")
    
    # Initialize validators
    input_validator = ContentValidator(
        ValidationConfig(
            enable_pii_detection=True,
            enable_toxic_detection=True,
            pii_block_on_critical=True,
            pii_block_on_high=False,
            log_issues=True
        )
    )
    
    output_guardrails = OutputGuardrails(
        enable_pii_check=True,
        enable_toxic_check=True,
        enable_hallucination_check=True,
        require_medical_disclaimer=True,
        block_on_pii=True,
        block_on_toxic=True
    )
    
    # ========================================================================
    # LAYER 1: INPUT VALIDATION
    # ========================================================================
    print("🔒 LAYER 1: INPUT VALIDATION")
    print("-" * 80)
    
    user_query = "What are the symptoms of diabetes?"
    print(f"User Query: {user_query}")
    
    is_safe, issues = input_validator.validate(user_query)
    
    if not is_safe:
        print("❌ Query BLOCKED due to validation issues")
        for issue in issues:
            print(f"  - {issue}")
        return
    else:
        print("✅ Query is safe to process\n")
    
    # ========================================================================
    # LAYER 2: CONTEXT VALIDATION
    # ========================================================================
    print("\n🔒 LAYER 2: CONTEXT VALIDATION")
    print("-" * 80)
    
    # Simulate retrieved documents from vector store
    retrieved_docs = [
        "Diabetes is a chronic disease that affects blood sugar levels.",
        "Patient John Doe, SSN: 123-45-6789, has type 2 diabetes.",  # Contains PII
        "Common symptoms include increased thirst and frequent urination.",
        "Contact support@hospital.com for more information.",  # Contains email
        "Treatment includes diet, exercise, and medication."
    ]
    
    print(f"Retrieved {len(retrieved_docs)} documents from vector store")
    print("Validating each document...\n")
    
    safe_context = []
    for i, doc in enumerate(retrieved_docs, 1):
        is_safe, issues = input_validator.validate(doc)
        
        if is_safe:
            safe_context.append(doc)
            print(f"  ✅ Doc {i}: Safe")
        else:
            print(f"  ❌ Doc {i}: BLOCKED ({len(issues)} issue(s))")
            for issue in issues:
                print(f"      - {issue.issue_type}")
    
    print(f"\n✅ {len(safe_context)}/{len(retrieved_docs)} documents safe to send to LLM\n")
    
    if not safe_context:
        print("❌ No safe context available - cannot proceed")
        return
    
    # ========================================================================
    # SIMULATE LLM CALL
    # ========================================================================
    print("\n🤖 CALLING LLM...")
    print("-" * 80)
    
    # Simulate different LLM responses
    llm_responses = [
        {
            "name": "Good response with disclaimer",
            "text": (
                "Common symptoms of diabetes include increased thirst, frequent urination, "
                "and unexplained weight loss. Please consult a healthcare professional "
                "for proper diagnosis and treatment."
            )
        },
        {
            "name": "Response without medical disclaimer",
            "text": (
                "Diabetes symptoms include increased thirst and frequent urination. "
                "You should take metformin 500mg twice daily."
            )
        },
        {
            "name": "Response with PII leakage",
            "text": (
                "Based on patient John Doe's record (SSN: 123-45-6789), "
                "the symptoms indicate type 2 diabetes."
            )
        },
        {
            "name": "Overconfident response (hallucination risk)",
            "text": (
                "This treatment will definitely cure your diabetes in 30 days guaranteed! "
                "You will never have diabetes again."
            )
        }
    ]
    
    # Test each response
    for i, response in enumerate(llm_responses, 1):
        print(f"\n{'='*80}")
        print(f"RESPONSE {i}: {response['name']}")
        print(f"{'='*80}")
        
        llm_output = response['text']
        print(f"\nLLM Output: {llm_output[:100]}...")
        
        # ====================================================================
        # LAYER 3: OUTPUT VALIDATION (GUARDRAILS)
        # ====================================================================
        print(f"\n🔒 LAYER 3: OUTPUT VALIDATION")
        print("-" * 80)
        
        is_safe, issues, safe_output = output_guardrails.validate_output(
            llm_output,
            original_query=user_query,
            retrieved_context=safe_context
        )
        
        if issues:
            print(f"⚠️  Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No issues found")
        
        print(f"\nSafe to show: {'YES ✓' if is_safe else 'NO ✗'}")
        
        if not is_safe:
            # Show fallback response
            print("\n❌ OUTPUT BLOCKED - Showing fallback response:")
            print("-" * 80)
            fallback = output_guardrails.get_fallback_response("safety")
            print(fallback)
        else:
            # Show output (possibly modified)
            if safe_output != llm_output:
                print("\n✅ OUTPUT MODIFIED - Showing safe version:")
                print("-" * 80)
                print(safe_output[:200] + "...")
            else:
                print("\n✅ OUTPUT APPROVED - Showing to user:")
                print("-" * 80)
                print(safe_output[:200] + "...")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print("""
    ✅ 3-Layer Validation Complete:
    
    Layer 1: INPUT VALIDATION
      - Validates user queries for PII and toxic content
      - Blocks malicious or sensitive queries
    
    Layer 2: CONTEXT VALIDATION
      - Validates retrieved documents before sending to LLM
      - Filters out documents with PII or toxic content
      - Ensures only safe context reaches the LLM
    
    Layer 3: OUTPUT VALIDATION (GUARDRAILS)
      - Validates LLM responses before showing to users
      - Checks for PII leakage
      - Detects toxic content generation
      - Identifies hallucination risks
      - Ensures medical disclaimers are present
      - Provides fallback responses when needed
    
    This creates a DEFENSE-IN-DEPTH approach for safe RAG systems! 🛡️
    """)


def simple_integration_example():
    """Simple example for integration into main.py"""
    
    print("\n" + "="*80)
    print("SIMPLE INTEGRATION EXAMPLE")
    print("="*80 + "\n")
    
    print("""
# ============================================================================
# Integration into main.py (Streamlit app)
# ============================================================================

import streamlit as st
from Content_Analyzer import ContentValidator, OutputGuardrails

# Initialize once
if 'input_validator' not in st.session_state:
    st.session_state.input_validator = ContentValidator()
    st.session_state.output_guardrails = OutputGuardrails(
        require_medical_disclaimer=True
    )

def process_query(user_query):
    # Layer 1: Validate input
    is_safe, issues = st.session_state.input_validator.validate(user_query)
    if not is_safe:
        st.error("⚠️ Your query contains sensitive information")
        return
    
    # Layer 2: Retrieve and validate context
    docs = vectorstore.similarity_search(user_query, k=5)
    safe_docs = []
    for doc in docs:
        is_safe, _ = st.session_state.input_validator.validate(doc.page_content)
        if is_safe:
            safe_docs.append(doc)
    
    if not safe_docs:
        st.warning("No safe content available")
        return
    
    # Call LLM
    llm_response = llm.invoke(safe_docs)
    
    # Layer 3: Validate output (GUARDRAILS)
    is_safe, issues, safe_output = st.session_state.output_guardrails.validate_output(
        llm_response,
        original_query=user_query,
        retrieved_context=[d.page_content for d in safe_docs]
    )
    
    if not is_safe:
        # Show fallback
        fallback = st.session_state.output_guardrails.get_fallback_response("safety")
        st.error(fallback)
    else:
        # Show safe output (possibly with disclaimer added)
        st.success(safe_output)

# ============================================================================
    """)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run complete demo
    complete_rag_pipeline_with_guardrails()
    
    # Show integration example
    input("\n\nPress Enter to see integration example...")
    simple_integration_example()
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80 + "\n")
