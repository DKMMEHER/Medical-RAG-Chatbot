"""
Demo: Comparing REGEX vs PRESIDIO vs HYBRID Detection Modes
Shows the differences in PII detection capabilities

Run from project root:
    python -m spacy download en_core_web_sm  # First time only
    uv run demo_detection_modes.py
"""

import logging
from Content_Analyzer import ContentValidator, ValidationConfig, PIIDetectionMode

# Set up logging to see which detector finds what
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_results(mode_name: str, is_safe: bool, issues: list):
    """Print validation results"""
    print(f"\n🔍 {mode_name} Mode Results:")
    print("-" * 80)
    
    if issues:
        print(f"Found {len(issues)} PII instance(s):\n")
        for i, issue in enumerate(issues, 1):
            confidence = ""
            if issue.metadata and 'confidence' in issue.metadata:
                confidence = f" (confidence: {issue.metadata['confidence']:.2f})"
            
            print(f"  {i}. [{issue.severity.value.upper()}] {issue.issue_type}")
            print(f"     Description: {issue.description}{confidence}")
            if issue.matched_text:
                print(f"     Matched: {issue.matched_text}")
        
        print(f"\n{'✅ SAFE' if is_safe else '❌ BLOCKED'} - Safe to process: {is_safe}")
    else:
        print("✅ No PII detected - Content is clean")


def demo_comparison():
    """Compare all three detection modes"""
    
    print_header("PII DETECTION MODES COMPARISON DEMO")
    
    # Test cases with different types of PII
    test_cases = [
        {
            "name": "Test 1: Structured Data (SSN, Email, Phone)",
            "text": "Contact info: SSN 123-45-6789, email john@test.com, phone 555-123-4567"
        },
        {
            "name": "Test 2: Person Names (Unstructured)",
            "text": "Dr. Sarah Johnson treated patient Michael Smith at Memorial Hospital"
        },
        {
            "name": "Test 3: Mixed Content",
            "text": "Patient John Doe (SSN: 987-65-4321) was seen by Dr. Emily Chen. Contact: john.doe@hospital.com"
        },
        {
            "name": "Test 4: Medical Context",
            "text": "Dr. Robert Martinez prescribed medication for patient ID MRN-123456. Follow-up scheduled."
        },
        {
            "name": "Test 5: Clean Medical Text",
            "text": "Diabetes is managed through diet, exercise, and medication. Regular monitoring is important."
        }
    ]
    
    for test in test_cases:
        print_header(test["name"])
        print(f"Text: {test['text']}\n")
        
        # Test 1: REGEX Mode
        print("┌─────────────────────────────────────────────────────────────────────┐")
        print("│ MODE 1: REGEX (Fast, Pattern-based)                                │")
        print("└─────────────────────────────────────────────────────────────────────┘")
        
        config_regex = ValidationConfig(
            pii_detection_mode=PIIDetectionMode.REGEX,
            verbose=False
        )
        validator_regex = ContentValidator(config_regex)
        is_safe_regex, issues_regex = validator_regex.validate(test['text'])
        print_results("REGEX", is_safe_regex, issues_regex)
        
        # Test 2: PRESIDIO Mode
        print("\n┌─────────────────────────────────────────────────────────────────────┐")
        print("│ MODE 2: PRESIDIO (ML-based, Context-aware)                         │")
        print("└─────────────────────────────────────────────────────────────────────┘")
        
        try:
            config_presidio = ValidationConfig(
                pii_detection_mode=PIIDetectionMode.PRESIDIO,
                presidio_score_threshold=0.5,
                verbose=False
            )
            validator_presidio = ContentValidator(config_presidio)
            is_safe_presidio, issues_presidio = validator_presidio.validate(test['text'])
            print_results("PRESIDIO", is_safe_presidio, issues_presidio)
        except Exception as e:
            print(f"⚠️  Presidio not available: {e}")
            print("   Install with: pip install presidio-analyzer presidio-anonymizer")
            print("   Then: python -m spacy download en_core_web_sm")
            issues_presidio = []
        
        # Test 3: HYBRID Mode
        print("\n┌─────────────────────────────────────────────────────────────────────┐")
        print("│ MODE 3: HYBRID (Best of Both Worlds)                               │")
        print("└─────────────────────────────────────────────────────────────────────┘")
        
        try:
            config_hybrid = ValidationConfig(
                pii_detection_mode=PIIDetectionMode.HYBRID,
                presidio_score_threshold=0.5,
                verbose=False
            )
            validator_hybrid = ContentValidator(config_hybrid)
            is_safe_hybrid, issues_hybrid = validator_hybrid.validate(test['text'])
            print_results("HYBRID", is_safe_hybrid, issues_hybrid)
        except Exception as e:
            print(f"⚠️  Hybrid mode not available (requires Presidio): {e}")
            issues_hybrid = []
        
        # Summary comparison
        print("\n" + "─" * 80)
        print("📊 SUMMARY COMPARISON:")
        print("─" * 80)
        print(f"  REGEX Mode:    {len(issues_regex)} PII instance(s) detected")
        if issues_presidio:
            print(f"  PRESIDIO Mode: {len(issues_presidio)} PII instance(s) detected")
        if issues_hybrid:
            print(f"  HYBRID Mode:   {len(issues_hybrid)} PII instance(s) detected")
        
        # Show what each mode caught
        if issues_presidio or issues_hybrid:
            print("\n  What each mode caught:")
            regex_types = set(i.issue_type for i in issues_regex)
            presidio_types = set(i.issue_type for i in issues_presidio) if issues_presidio else set()
            hybrid_types = set(i.issue_type for i in issues_hybrid) if issues_hybrid else set()
            
            print(f"    REGEX:    {', '.join(regex_types) if regex_types else 'None'}")
            if presidio_types:
                print(f"    PRESIDIO: {', '.join(presidio_types) if presidio_types else 'None'}")
            if hybrid_types:
                print(f"    HYBRID:   {', '.join(hybrid_types) if hybrid_types else 'None'}")
            
            # Show unique findings
            if presidio_types:
                presidio_only = presidio_types - regex_types
                if presidio_only:
                    print(f"\n  ✨ Presidio found additionally: {', '.join(presidio_only)}")
        
        print("\n")
        input("Press Enter to continue to next test...")


def demo_performance():
    """Show performance characteristics"""
    
    print_header("PERFORMANCE COMPARISON")
    
    import time
    
    text = "Dr. Sarah Johnson (SSN: 123-45-6789) treated patient John Doe at john@hospital.com"
    iterations = 10
    
    print(f"Testing with {iterations} iterations...\n")
    
    # REGEX timing
    config_regex = ValidationConfig(pii_detection_mode=PIIDetectionMode.REGEX)
    validator_regex = ContentValidator(config_regex)
    
    start = time.time()
    for _ in range(iterations):
        validator_regex.validate(text)
    regex_time = (time.time() - start) / iterations
    
    print(f"⚡ REGEX Mode:    {regex_time*1000:.2f}ms per validation")
    
    # PRESIDIO timing
    try:
        config_presidio = ValidationConfig(pii_detection_mode=PIIDetectionMode.PRESIDIO)
        validator_presidio = ContentValidator(config_presidio)
        
        start = time.time()
        for _ in range(iterations):
            validator_presidio.validate(text)
        presidio_time = (time.time() - start) / iterations
        
        print(f"🐢 PRESIDIO Mode: {presidio_time*1000:.2f}ms per validation")
        print(f"   Slowdown: {presidio_time/regex_time:.1f}x slower than REGEX")
        
        # HYBRID timing
        config_hybrid = ValidationConfig(pii_detection_mode=PIIDetectionMode.HYBRID)
        validator_hybrid = ContentValidator(config_hybrid)
        
        start = time.time()
        for _ in range(iterations):
            validator_hybrid.validate(text)
        hybrid_time = (time.time() - start) / iterations
        
        print(f"🔄 HYBRID Mode:   {hybrid_time*1000:.2f}ms per validation")
        print(f"   Slowdown: {hybrid_time/regex_time:.1f}x slower than REGEX")
        
    except Exception as e:
        print(f"\n⚠️  Presidio not available for performance test: {e}")


def demo_recommendations():
    """Show recommendations for each mode"""
    
    print_header("WHEN TO USE EACH MODE")
    
    recommendations = """
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🚀 REGEX MODE (Default)                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✅ Development and testing                                                  │
│ ✅ Quick prototyping                                                        │
│ ✅ When speed is critical (real-time processing)                           │
│ ✅ No ML dependencies available                                            │
│ ✅ Structured data only (SSN, emails, phones)                              │
│                                                                             │
│ Speed:    ⚡⚡⚡⚡⚡ Very Fast                                                │
│ Accuracy: ⭐⭐⭐ Good (70-80%)                                              │
│ Setup:    ✅ Ready to use (no installation)                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎯 PRESIDIO MODE                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✅ Production deployment                                                    │
│ ✅ Medical/healthcare applications                                         │
│ ✅ When accuracy is critical                                               │
│ ✅ Need to detect person names, organizations                              │
│ ✅ Context-aware detection required                                        │
│ ✅ Multi-language support needed                                           │
│                                                                             │
│ Speed:    ⚡⚡ Slower                                                       │
│ Accuracy: ⭐⭐⭐⭐⭐ Excellent (90-95%)                                      │
│ Setup:    📦 Requires installation (presidio + spacy)                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ HYBRID MODE (Best of Both)                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✅ Maximum security requirements                                           │
│ ✅ Compliance-critical applications (HIPAA, GDPR)                          │
│ ✅ Can't afford to miss ANY PII                                            │
│ ✅ Audit requirements                                                       │
│ ✅ When you need both structured AND unstructured PII detection            │
│                                                                             │
│ Speed:    ⚡⚡ Slower (runs both detectors)                                │
│ Accuracy: ⭐⭐⭐⭐⭐ Maximum (95%+)                                          │
│ Setup:    📦 Requires installation (presidio + spacy)                      │
│ Coverage: 🎯 Maximum - catches everything both detectors find              │
└─────────────────────────────────────────────────────────────────────────────┘
    """
    
    print(recommendations)


def main():
    """Run all demos"""
    
    print("\n" + "=" * 80)
    print("  PII DETECTION MODES DEMONSTRATION")
    print("  Comparing REGEX vs PRESIDIO vs HYBRID")
    print("=" * 80)
    
    print("\nThis demo will show you:")
    print("  1. How each mode detects different types of PII")
    print("  2. Performance characteristics")
    print("  3. When to use each mode")
    print("\n")
    
    try:
        # Main comparison demo
        demo_comparison()
        
        # Performance comparison
        input("\n\nPress Enter to see performance comparison...")
        demo_performance()
        
        # Recommendations
        input("\n\nPress Enter to see recommendations...")
        demo_recommendations()
        
        print("\n" + "=" * 80)
        print("  ✅ DEMO COMPLETE")
        print("=" * 80)
        
        print("\n📚 Next Steps:")
        print("  1. Choose the mode that fits your needs")
        print("  2. Update your ValidationConfig")
        print("  3. Test with your actual data")
        print("  4. Monitor performance in production")
        print("\n  See docs/PRESIDIO_INTEGRATION.md for more details!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
