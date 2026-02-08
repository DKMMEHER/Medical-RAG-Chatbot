"""
NER/NLP vs Pattern-Based Detection Comparison Demo
Demonstrates the difference between regex patterns and NER/NLP techniques
"""

import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_section(title: str):
    """Print a formatted section"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)

def demo_pii_detection():
    """Demonstrate PII detection with different approaches"""
    print_header("PII DETECTION: Pattern-Based vs NER/NLP")
    
    # Test cases
    test_cases = [
        {
            "name": "Structured Data (SSN, Email, Phone)",
            "text": "Contact: SSN 123-45-6789, email john@test.com, phone 555-123-4567"
        },
        {
            "name": "Unstructured Data (Person Names)",
            "text": "Dr. Sarah Johnson treated patient Michael Smith at Memorial Hospital"
        },
        {
            "name": "Mixed Content",
            "text": "Patient John Doe (SSN: 987-65-4321) was seen by Dr. Emily Chen. Contact: john.doe@hospital.com"
        },
        {
            "name": "Medical Context",
            "text": "Dr. Robert Martinez from Mayo Clinic prescribed medication for patient ID MRN-123456"
        },
        {
            "name": "Clean Text",
            "text": "Diabetes is managed through diet, exercise, and medication"
        }
    ]
    
    # Try to import detectors
    try:
        from Content_Analyzer import PIIDetector
        from Content_Analyzer.config import PIIDetectionMode
        regex_available = True
    except ImportError:
        print("❌ PIIDetector not available")
        regex_available = False
    
    try:
        from Content_Analyzer.pii_detector_presidio import PIIDetectorPresidio
        presidio_available = True
    except ImportError:
        print("⚠️  Presidio not available (install: pip install presidio-analyzer presidio-anonymizer)")
        print("   Then: python -m spacy download en_core_web_sm")
        presidio_available = False
    
    try:
        from Content_Analyzer.ner_detector import NERDetector
        ner_available = True
    except ImportError:
        print("⚠️  NER Detector not available")
        ner_available = False
    
    if not regex_available:
        print("\n❌ Cannot run demo - Content_Analyzer not available")
        return
    
    # Initialize detectors
    print("\n📦 Initializing Detectors...")
    regex_detector = PIIDetector() if regex_available else None
    presidio_detector = PIIDetectorPresidio() if presidio_available else None
    ner_detector = NERDetector() if ner_available else None
    
    # Run tests
    for i, test in enumerate(test_cases, 1):
        print_section(f"Test {i}: {test['name']}")
        print(f"Text: \"{test['text']}\"\n")
        
        # Pattern-based detection
        if regex_detector:
            regex_issues = regex_detector.detect(test['text'])
            print(f"🔍 PATTERN-BASED (Regex):")
            if regex_issues:
                print(f"   Found {len(regex_issues)} issue(s):")
                for issue in regex_issues:
                    print(f"   • {issue.issue_type}: {issue.matched_text}")
            else:
                print(f"   ❌ No PII detected")
        
        # NER-based detection (Presidio)
        if presidio_detector:
            presidio_issues = presidio_detector.detect(test['text'])
            print(f"\n🧠 NER/NLP-BASED (Presidio + spaCy):")
            if presidio_issues:
                print(f"   Found {len(presidio_issues)} issue(s):")
                for issue in presidio_issues:
                    conf = issue.metadata.get('confidence', 0) if issue.metadata else 0
                    print(f"   • {issue.issue_type}: {issue.matched_text} (confidence: {conf:.2f})")
            else:
                print(f"   ✅ No PII detected")
        
        # Pure NER detection
        if ner_detector:
            entities = ner_detector.detect_entities(test['text'])
            print(f"\n🎯 PURE NER (spaCy):")
            if entities:
                print(f"   Found {len(entities)} entity/entities:")
                for entity in entities:
                    print(f"   • {entity.label}: {entity.text}")
            else:
                print(f"   ✅ No entities detected")
        
        # Analysis
        print(f"\n💡 Analysis:")
        regex_count = len(regex_issues) if regex_detector and regex_issues else 0
        presidio_count = len(presidio_issues) if presidio_detector and presidio_issues else 0
        ner_count = len(entities) if ner_detector and entities else 0
        
        if presidio_count > regex_count:
            print(f"   ⭐ NER/NLP detected {presidio_count - regex_count} additional PII that patterns missed!")
        elif regex_count == presidio_count and regex_count > 0:
            print(f"   ✅ Both approaches found the same structured PII")
        elif regex_count == 0 and presidio_count == 0:
            print(f"   ✅ Clean text - no PII found by either approach")

def demo_toxic_detection():
    """Demonstrate toxic content detection with different approaches"""
    print_header("TOXIC CONTENT DETECTION: Word-List vs ML/NLP")
    
    test_cases = [
        {
            "name": "Medical Context (False Positive Test)",
            "text": "Sexual dysfunction is a common symptom of diabetes"
        },
        {
            "name": "Clinical Language",
            "text": "This medication can kill harmful bacteria in the intestines"
        },
        {
            "name": "Mild Profanity",
            "text": "This damn disease is really hard to manage"
        },
        {
            "name": "Actually Toxic",
            "text": "You're a stupid idiot and I hate you"
        },
        {
            "name": "Clean Medical Text",
            "text": "Diabetes is managed through diet, exercise, and medication"
        }
    ]
    
    # Try to import detectors
    try:
        from Content_Analyzer import ToxicContentDetector
        wordlist_available = True
    except ImportError:
        print("❌ ToxicContentDetector not available")
        wordlist_available = False
    
    try:
        from Content_Analyzer.toxic_detector_ml import ToxicContentDetectorML
        ml_available = True
    except ImportError:
        print("⚠️  Detoxify not available (install: pip install detoxify)")
        ml_available = False
    
    if not wordlist_available:
        print("\n❌ Cannot run demo - Content_Analyzer not available")
        return
    
    # Initialize detectors
    print("\n📦 Initializing Detectors...")
    wordlist_detector = ToxicContentDetector() if wordlist_available else None
    ml_detector = ToxicContentDetectorML() if ml_available else None
    
    # Run tests
    for i, test in enumerate(test_cases, 1):
        print_section(f"Test {i}: {test['name']}")
        print(f"Text: \"{test['text']}\"\n")
        
        # Word-list detection
        if wordlist_detector:
            wordlist_issues = wordlist_detector.detect(test['text'])
            print(f"📝 WORD-LIST BASED (Pattern Matching):")
            if wordlist_issues:
                print(f"   Found {len(wordlist_issues)} issue(s):")
                for issue in wordlist_issues:
                    print(f"   • {issue.issue_type}: {issue.severity.value}")
            else:
                print(f"   ✅ No toxic content detected")
        
        # ML-based detection
        if ml_detector:
            ml_issues = ml_detector.detect(test['text'])
            scores = ml_detector.get_detailed_scores(test['text'])
            
            print(f"\n🧠 ML/NLP-BASED (BERT/Detoxify):")
            if ml_issues:
                print(f"   Found {len(ml_issues)} issue(s):")
                for issue in ml_issues:
                    conf = issue.metadata.get('confidence', 0) if issue.metadata else 0
                    print(f"   • {issue.issue_type}: {issue.severity.value} (confidence: {conf:.2f})")
            else:
                print(f"   ✅ No toxic content detected")
            
            # Show top scores
            if scores:
                top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"\n   Top Toxicity Scores:")
                for category, score in top_scores:
                    emoji = "🔴" if score > 0.5 else "🟡" if score > 0.3 else "🟢"
                    print(f"   {emoji} {category}: {score:.3f}")
            
            # Medical context check
            is_safe = ml_detector.is_safe_for_medical_context(test['text'])
            print(f"\n   Medical Context Safe: {'YES ✓' if is_safe else 'NO ✗'}")
        
        # Analysis
        print(f"\n💡 Analysis:")
        wordlist_count = len(wordlist_issues) if wordlist_detector and wordlist_issues else 0
        ml_count = len(ml_issues) if ml_detector and ml_issues else 0
        
        if wordlist_count > 0 and ml_count == 0:
            print(f"   ⭐ ML/NLP correctly identified this as safe (word-list had false positive)")
        elif ml_count > 0 and wordlist_count == 0:
            print(f"   ⚠️  ML/NLP detected toxicity that word-list missed")
        elif wordlist_count > 0 and ml_count > 0:
            print(f"   ✅ Both approaches detected toxic content")
        else:
            print(f"   ✅ Clean text - no toxicity detected")

def demo_hybrid_mode():
    """Demonstrate hybrid detection mode"""
    print_header("HYBRID MODE: Combining Pattern-Based + NER/NLP")
    
    try:
        from Content_Analyzer import ContentValidator, ValidationConfig, PIIDetectionMode, ToxicDetectionMode
    except ImportError:
        print("❌ ContentValidator not available")
        return
    
    test_text = """
    Patient John Doe (SSN: 987-65-4321) was seen by Dr. Emily Chen at Memorial Hospital.
    Contact: john.doe@hospital.com, Phone: 555-123-4567
    Diagnosis: Type 2 diabetes with sexual dysfunction complications.
    """
    
    print(f"Test Text:\n{test_text}\n")
    
    # Test different modes
    modes = [
        ("REGEX Only", PIIDetectionMode.REGEX, ToxicDetectionMode.WORDLIST),
        ("PRESIDIO Only (NER/NLP)", PIIDetectionMode.PRESIDIO, ToxicDetectionMode.ML),
        ("HYBRID (Best of Both)", PIIDetectionMode.HYBRID, ToxicDetectionMode.HYBRID)
    ]
    
    for mode_name, pii_mode, toxic_mode in modes:
        print_section(mode_name)
        
        try:
            config = ValidationConfig(
                pii_detection_mode=pii_mode,
                toxic_detection_mode=toxic_mode,
                verbose=False
            )
            validator = ContentValidator(config)
            
            is_safe, issues = validator.validate(test_text)
            
            print(f"Issues Found: {len(issues)}")
            
            # Group by type
            pii_issues = [i for i in issues if i.issue_type.startswith("PII_")]
            toxic_issues = [i for i in issues if i.issue_type.startswith("TOXIC_")]
            
            if pii_issues:
                print(f"\nPII Issues ({len(pii_issues)}):")
                for issue in pii_issues:
                    print(f"  • {issue.issue_type}: {issue.matched_text}")
            
            if toxic_issues:
                print(f"\nToxic Issues ({len(toxic_issues)}):")
                for issue in toxic_issues:
                    print(f"  • {issue.issue_type}: {issue.severity.value}")
            
            print(f"\nSafe to Process: {'YES ✓' if is_safe else 'NO ✗'}")
            
        except Exception as e:
            print(f"⚠️  Mode not available: {e}")

def main():
    """Main demo function"""
    print("\n" + "🎯" * 40)
    print("NER/NLP TECHNIQUES DEMONSTRATION")
    print("Medical Chatbot - Content Analyzer")
    print("🎯" * 40)
    
    print("\nThis demo shows the difference between:")
    print("  1. Pattern-based detection (regex, word lists)")
    print("  2. NER/NLP-based detection (spaCy, Presidio, BERT/Detoxify)")
    print("  3. Hybrid approach (combining both)")
    
    # Run demos
    demo_pii_detection()
    demo_toxic_detection()
    demo_hybrid_mode()
    
    # Summary
    print_header("SUMMARY: Why NER/NLP Matters")
    
    print("""
✅ NER/NLP ADVANTAGES:
   • Context-aware: Understands "Dr. Smith" is a person, not just a pattern
   • Handles variations: Different name formats, titles, multi-word entities
   • Reduces false positives: Knows "sexual dysfunction" is medical, not toxic
   • Better accuracy: ML models trained on real-world data
   • Detects unstructured PII: Person names, organizations, locations
   
❌ PATTERN-BASED LIMITATIONS:
   • No context: Just looks for regex patterns
   • Misses variations: Can't handle different formats
   • High false positives: Flags medical terms as toxic
   • Rigid: Can't adapt to new patterns
   • Misses unstructured data: Can't detect person names reliably
   
🎯 RECOMMENDATION:
   • Development/Testing: Use REGEX (fast)
   • Production/Medical: Use HYBRID (maximum coverage + accuracy)
   • HIPAA/Compliance: Use HYBRID (can't miss any PII)
    """)
    
    print("\n" + "=" * 80)
    print("Demo Complete! Check the analysis report:")
    print("  📄 NER_NLP_TECHNIQUES_ANALYSIS.md")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
