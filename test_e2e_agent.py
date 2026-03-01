#!/usr/bin/env python3
"""
End-to-end test for FinRadar DSPy agents.
Tests actual LLM integration with real API calls.
"""
import os
import sys

# Ensure environment variables are available
os.environ.setdefault("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

def test_dspy_configuration():
    """Test that DSPy can be configured with OpenAI."""
    import dspy
    
    print("=" * 60)
    print("TEST 1: DSPy Configuration")
    print("=" * 60)
    
    try:
        lm = dspy.LM(
            model="openai/gpt-4o-mini",
            temperature=0.0,
        )
        dspy.configure(lm=lm)
        print(f"[OK] DSPy configured with model: gpt-4o-mini")
        return True
    except Exception as e:
        print(f"[FAIL] DSPy configuration failed: {e}")
        return False


def test_financial_sentiment_agent():
    """Test the FinancialSentiment signature with real LLM call."""
    import dspy
    from app.agents.dspy_signatures import FinancialSentiment
    
    print("\n" + "=" * 60)
    print("TEST 2: Financial Sentiment Analysis (Real LLM)")
    print("=" * 60)
    
    test_text = """
    Apple Inc. reported record quarterly revenue of $123.9 billion, 
    up 11 percent year over year, and quarterly earnings per diluted share of $2.10.
    The company expects strong iPhone sales to continue into the next quarter.
    """
    
    try:
        predictor = dspy.ChainOfThought(FinancialSentiment)
        result = predictor(analyzed_text=test_text)
        
        print(f"Input: Financial news about Apple...")
        print(f"Output:")
        print(f"  - Sentiment: {result.sentiment}")
        print(f"  - Confidence: {result.confidence}")
        print(f"  - Key Factors: {result.key_factors}")
        
        # Verify the response makes sense
        sentiment_valid = result.sentiment.lower() in ["bullish", "bearish", "neutral"]
        confidence_valid = isinstance(result.confidence, (int, float)) and 0 <= result.confidence <= 1
        
        if sentiment_valid and confidence_valid:
            print(f"[OK] Sentiment analysis returned valid response")
            return True
        else:
            print(f"[FAIL] Invalid response structure")
            return False
            
    except Exception as e:
        print(f"[FAIL] Sentiment analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_evaluation_agent():
    """Test the EvaluateStartup signature with real LLM call."""
    import dspy
    from app.agents.dspy_signatures import EvaluateStartup
    
    print("\n" + "=" * 60)
    print("TEST 3: Startup Evaluation (Real LLM)")
    print("=" * 60)
    
    startup_data = """
    Company: TechStartup AI
    Founded: 2023
    Funding: $5M Series A
    Team: 3 ex-Google engineers, 1 ex-Meta PM
    Traction: 10k monthly active users, 200% MoM growth
    Product: AI-powered code review tool
    """
    
    try:
        predictor = dspy.ChainOfThought(EvaluateStartup)
        result = predictor(
            startup_data=startup_data,
            industry="Enterprise Software / AI Developer Tools"
        )
        
        print(f"Input: Startup info for TechStartup AI...")
        print(f"Output:")
        print(f"  - Score: {result.overall_score}/100")
        print(f"  - Strengths: {result.strengths[:2]}...")  # Show first 2
        print(f"  - Weaknesses: {result.weaknesses[:2]}...")
        print(f"  - Thesis: {result.investment_thesis[:100]}...")
        
        # Verify response
        score_valid = isinstance(result.overall_score, (int, float)) and 0 <= result.overall_score <= 100
        
        if score_valid:
            print(f"[OK] Startup evaluation returned valid response")
            return True
        else:
            print(f"[FAIL] Invalid score value")
            return False
            
    except Exception as e:
        print(f"[FAIL] Startup evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_financial_analysis_agent_module():
    """Test the full FinancialAnalysisAgent module."""
    from app.agents.dspy_signatures import FinancialAnalysisAgent, configure_dspy
    
    print("\n" + "=" * 60)
    print("TEST 4: FinancialAnalysisAgent Module (Real LLM)")
    print("=" * 60)
    
    try:
        configure_dspy()
        agent = FinancialAnalysisAgent()
        
        test_text = "NVIDIA stock surges 10% after announcing breakthrough AI chip architecture."
        result = agent.analyze_sentiment(test_text)
        
        print(f"Input: '{test_text}'")
        print(f"Output: {result}")
        
        if "sentiment" in result and "confidence" in result:
            print(f"[OK] FinancialAnalysisAgent module works")
            return True
        else:
            print(f"[FAIL] Missing expected keys in response")
            return False
            
    except Exception as e:
        print(f"[FAIL] Agent module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     FinRadar DSPy Agent - End-to-End Test Suite           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[ERROR] OPENAI_API_KEY not set. Cannot run E2E tests.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return 1
    
    results = []
    
    results.append(("DSPy Configuration", test_dspy_configuration()))
    results.append(("Financial Sentiment", test_financial_sentiment_agent()))
    results.append(("Startup Evaluation", test_startup_evaluation_agent()))
    results.append(("Agent Module", test_financial_analysis_agent_module()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
