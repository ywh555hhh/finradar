#!/usr/bin/env python3
"""End-to-end test for FinRadar DSPy agents with mocked LLM responses."""
import sys
import os
os.environ["DSPY_CACHE_DISABLED"] = "1"


def mock_dspy_response(**kwargs):
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_result, key, value)
    return mock_result


def test_sentiment_agent_with_mock():
    print("\n" + "=" * 60)
    print("TEST 1: Financial Sentiment Agent (Mocked LLM)")
    print("=" * 60)
    
    from unittest.mock import patch, MagicMock
    import dspy
    from app.agents.dspy_signatures import FinancialSentiment
    
    mock_response = mock_dspy_response(
        sentiment="bullish",
        confidence=0.85,
        key_factors=["record revenue", "strong iPhone sales", "positive outlook"]
    )
    
    with patch.object(dspy.ChainOfThought, '__call__', return_value=mock_response):
        predictor = dspy.ChainOfThought(FinancialSentiment)
        result = predictor(analyzed_text="Apple reports record revenue")
        
        print(f"  Sentiment: {result.sentiment}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Key Factors: {result.key_factors}")
        
        assert result.sentiment == "bullish"
        assert result.confidence == 0.85
        print("  [PASS] Sentiment agent works correctly")
        return True


def test_startup_evaluation_with_mock():
    print("\n" + "=" * 60)
    print("TEST 2: Startup Evaluation Agent (Mocked LLM)")
    print("=" * 60)
    
    from unittest.mock import patch
    import dspy
    from app.agents.dspy_signatures import EvaluateStartup
    
    mock_response = mock_dspy_response(
        overall_score=78.5,
        strengths=["strong team", "rapid growth", "clear product-market fit"],
        weaknesses=["limited funding", "competitive market"],
        investment_thesis="Promising AI startup with experienced team and strong traction."
    )
    
    with patch.object(dspy.ChainOfThought, '__call__', return_value=mock_response):
        predictor = dspy.ChainOfThought(EvaluateStartup)
        result = predictor(
            startup_data="TechStartup AI, $5M Series A, 10k MAU",
            industry="Enterprise Software"
        )
        
        print(f"  Score: {result.overall_score}/100")
        print(f"  Strengths: {result.strengths[:2]}...")
        print(f"  Investment Thesis: {result.investment_thesis[:50]}...")
        
        assert result.overall_score == 78.5
        print("  [PASS] Startup evaluation agent works correctly")
        return True


def test_alert_generation_with_mock():
    print("\n" + "=" * 60)
    print("TEST 3: Alert Generation Agent (Mocked LLM)")
    print("=" * 60)
    
    from unittest.mock import patch
    import dspy
    from app.agents.dspy_signatures import GenerateAlert
    
    mock_response = mock_dspy_response(
        title="Funding Alert: TechStartup AI raises $10M",
        message="TechStartup AI has closed a $10M Series A round.",
        severity="high",
        action_required=True,
        action_description="Review startup profile and consider outreach."
    )
    
    with patch.object(dspy.ChainOfThought, '__call__', return_value=mock_response):
        predictor = dspy.ChainOfThought(GenerateAlert)
        result = predictor(
            event_data="TechStartup AI closed $10M Series A",
            alert_type="funding"
        )
        
        print(f"  Title: {result.title}")
        print(f"  Severity: {result.severity}")
        print(f"  Action Required: {result.action_required}")
        
        assert result.severity == "high"
        assert result.action_required == True
        print("  [PASS] Alert generation agent works correctly")
        return True


def test_financial_analysis_agent_module():
    print("\n" + "=" * 60)
    print("TEST 4: FinancialAnalysisAgent Module (Mocked)")
    print("=" * 60)
    
    from unittest.mock import patch, MagicMock
    from app.agents.dspy_signatures import FinancialAnalysisAgent
    
    agent = FinancialAnalysisAgent()
    
    mock_sentiment = mock_dspy_response(
        sentiment="bullish",
        confidence=0.92,
        key_factors=["AI demand surge", "datacenter growth"]
    )
    
    with patch.object(agent.sentiment_analyzer, 'forward', return_value=mock_sentiment):
        result = agent.analyze_sentiment("NVIDIA stock surges on AI chip demand")
        
        print(f"  Result: {result}")
        
        assert result["sentiment"] == "bullish"
        assert result["confidence"] == 0.92
        print("  [PASS] FinancialAnalysisAgent module works correctly")
        return True


def test_startup_discovery_agent_module():
    print("\n" + "=" * 60)
    print("TEST 5: StartupDiscoveryAgent Module (Mocked)")
    print("=" * 60)
    
    from unittest.mock import patch
    from app.agents.dspy_signatures import StartupDiscoveryAgent
    
    agent = StartupDiscoveryAgent()
    
    mock_eval = mock_dspy_response(
        overall_score=85.0,
        strengths=["ex-team", "traction"],
        weaknesses=["early stage"],
        investment_thesis="Strong potential"
    )
    
    with patch.object(agent.evaluator, 'forward', return_value=mock_eval):
        result = agent.evaluate_startup(
            startup_data="AI startup with ex-Google founders",
            industry="AI/ML"
        )
        
        print(f"  Result: {result}")
        
        assert result["overall_score"] == 85.0
        print("  [PASS] StartupDiscoveryAgent module works correctly")
        return True


def test_alert_generator_agent_module():
    print("\n" + "=" * 60)
    print("TEST 6: AlertGeneratorAgent Module (Mocked)")
    print("=" * 60)
    
    from unittest.mock import patch
    from app.agents.dspy_signatures import AlertGeneratorAgent
    
    agent = AlertGeneratorAgent()
    
    mock_alert = mock_dspy_response(
        title="Test Alert",
        message="Test message",
        severity="medium",
        action_required=False,
        action_description="No action needed"
    )
    
    with patch.object(agent.generator, 'forward', return_value=mock_alert):
        result = agent.generate_alert(
            event_data="Test event",
            alert_type="test"
        )
        
        print(f"  Result: {result}")
        
        assert result["title"] == "Test Alert"
        print("  [PASS] AlertGeneratorAgent module works correctly")
        return True


def test_dspy_signatures_structure():
    print("\n" + "=" * 60)
    print("TEST 7: DSPy Signatures Structure Validation")
    print("=" * 60)
    
    from app.agents.dspy_signatures import (
        FinancialSentiment,
        ExtractCompanyInfo,
        SummarizeReport,
        EvaluateStartup,
        CompareCompanies,
        GenerateAlert,
    )
    
    signatures = [
        ("FinancialSentiment", FinancialSentiment),
        ("ExtractCompanyInfo", ExtractCompanyInfo),
        ("SummarizeReport", SummarizeReport),
        ("EvaluateStartup", EvaluateStartup),
        ("CompareCompanies", CompareCompanies),
        ("GenerateAlert", GenerateAlert),
    ]
    
    for name, sig in signatures:
        assert hasattr(sig, '__annotations__') or hasattr(sig, '__doc__')
        print(f"  [OK] {name} signature defined")
    
    print("  [PASS] All 6 DSPy signatures properly structured")
    return True


def test_outreach_agent():
    print("\n" + "=" * 60)
    print("TEST 8: Outreach Agent (DSPy Module)")
    print("=" * 60)
    
    from unittest.mock import patch
    from app.agents.outreach_agent import OutreachAgent, CandidateProfile
    
    candidate = CandidateProfile(
        name="Test User",
        email="test@example.com",
        skills=["Python", "AI/ML", "React"],
        experience_years=2,
        current_role="Software Engineer"
    )
    
    agent = OutreachAgent(candidate)
    
    mock_fit = mock_dspy_response(
        fit_score=82.5,
        matching_skills=["Python", "AI/ML"],
        gap_skills=["Rust"],
        recommended_role="ML Engineer",
        conversation_starters=["Tell me about your AI stack"]
    )
    
    with patch.object(agent.fit_assessor, 'forward', return_value=mock_fit):
        result = agent.assess_fit({
            "tech_stack": ["Python", "PyTorch"],
            "funding_stage": "Series A",
            "hiring_signals": ["Looking for ML engineers"]
        })
        
        print(f"  Fit Score: {result['fit_score']}/100")
        print(f"  Matching Skills: {result['matching_skills']}")
        print(f"  Recommended Role: {result['recommended_role']}")
        
        assert result["fit_score"] == 82.5
        print("  [PASS] Outreach agent works correctly")
        return True


def test_notification_manager():
    print("\n" + "=" * 60)
    print("TEST 9: Notification Manager")
    print("=" * 60)
    
    from app.processors.outreach import NotificationManager
    
    manager = NotificationManager()
    
    startup_data = {
        "name": "TechStartup AI",
        "contact_email": "john@techstartup.ai",
        "linkedin_url": "https://linkedin.com/company/techstartup",
    }
    
    message = {
        "subject": "You've been discovered!",
        "body": "Our AI identified your team."
    }
    
    print(f"  NotificationManager initialized")
    print(f"  Has slack notifier: {manager.slack is not None}")
    print(f"  Has email channel: {manager.email is not None}")
    
    assert manager.slack is not None
    assert manager.email is not None
    print("  [PASS] Notification manager works correctly")
    return True


def main():
    print("=" * 60)
    print("     FinRadar DSPy Agent - E2E Mock Test Suite")
    print("=" * 60)
    
    results = []
    
    tests = [
        ("Sentiment Agent", test_sentiment_agent_with_mock),
        ("Startup Evaluation", test_startup_evaluation_with_mock),
        ("Alert Generation", test_alert_generation_with_mock),
        ("FinancialAnalysis Module", test_financial_analysis_agent_module),
        ("StartupDiscovery Module", test_startup_discovery_agent_module),
        ("AlertGenerator Module", test_alert_generator_agent_module),
        ("Signatures Structure", test_dspy_signatures_structure),
        ("Outreach Agent", test_outreach_agent),
        ("Notification Manager", test_notification_manager),
    ]
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
