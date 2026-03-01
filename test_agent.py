import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_models():
    from app.core.models import Company, StartupTeam, FundingStage, ReportType
    
    company = Company(
        name="Test Startup",
        industry="AI",
        funding_stage=FundingStage.SEED,
    )
    assert company.name == "Test Startup"
    assert company.funding_stage == FundingStage.SEED
    
    startup = StartupTeam(
        company_name="TechCo",
        industry="Fintech",
    )
    assert startup.company_name == "TechCo"
    
    print("[PASS] Models work correctly")
    return True


def test_config():
    from app.core.config import settings
    
    assert settings.project_name == "FinRadar"
    assert settings.version == "0.1.0"
    assert settings.dspy_lm_model == "openai/gpt-4o-mini"
    print("[PASS] Config loaded correctly")
    return True


def test_dspy_signatures():
    from app.agents.dspy_signatures import (
        FinancialSentiment,
        ExtractCompanyInfo,
        SummarizeReport,
        EvaluateStartup,
        FinancialAnalysisAgent,
        StartupDiscoveryAgent,
        AlertGeneratorAgent,
    )
    
    assert FinancialSentiment is not None
    assert ExtractCompanyInfo is not None
    assert SummarizeReport is not None
    assert EvaluateStartup is not None
    assert FinancialAnalysisAgent is not None
    assert StartupDiscoveryAgent is not None
    assert AlertGeneratorAgent is not None
    
    print("[PASS] DSPy signatures and agents defined correctly")
    return True


def test_outreach_agent():
    from app.agents.outreach_agent import (
        CandidateProfile,
        GenerateOutreachEmail,
        AssessTeamFit,
        OutreachAgent,
    )
    
    profile = CandidateProfile(
        name="Test User",
        email="test@example.com",
        skills=["Python", "TypeScript"],
        experience_years=3,
    )
    
    assert profile.name == "Test User"
    assert len(profile.skills) == 2
    assert profile.experience_years == 3
    
    agent = OutreachAgent(profile)
    assert agent.candidate.name == "Test User"
    
    print("[PASS] Outreach agent structures work")
    return True


def test_sources_structure():
    from app.sources.financial_sources import SECSource, YahooFinanceSource, AlphaVantageSource
    from app.sources.startup_sources import CrunchbaseSource, TechCrunchSource, ProductHuntSource
    
    yf = YahooFinanceSource()
    assert yf is not None
    assert hasattr(yf, 'get_company_info')
    assert hasattr(yf, 'get_financials')
    assert hasattr(yf, 'get_news')
    
    sec = SECSource()
    assert hasattr(sec, 'download_10k')
    assert hasattr(sec, 'download_10q')
    
    tc = TechCrunchSource()
    assert hasattr(tc, 'search_startups')
    assert hasattr(tc, 'get_funding_news')
    
    print("[PASS] Source classes instantiate correctly")
    return True


def test_prefect_flows():
    from app.workflows.scheduled_flows import daily_financial_scan, earnings_monitor, sec_filing_monitor
    from app.workflows.discovery_flow import continuous_discovery, weekly_deep_scan
    
    assert callable(daily_financial_scan)
    assert callable(earnings_monitor)
    assert callable(sec_filing_monitor)
    assert callable(continuous_discovery)
    assert callable(weekly_deep_scan)
    
    print("[PASS] Prefect flows defined correctly")
    return True


def test_notification_manager():
    from app.processors.outreach import NotificationManager, SlackNotifier, EmailOutreach
    
    nm = NotificationManager()
    assert hasattr(nm, 'notify_startup')
    assert hasattr(nm, 'notify_user')
    
    sn = SlackNotifier()
    assert hasattr(sn, 'notify_user')
    
    print("[PASS] Notification manager structures work")
    return True


def run_all_tests():
    tests = [
        ("Models", test_models),
        ("Config", test_config),
        ("DSPy Signatures", test_dspy_signatures),
        ("Outreach Agent", test_outreach_agent),
        ("Sources", test_sources_structure),
        ("Prefect Flows", test_prefect_flows),
        ("Notification Manager", test_notification_manager),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            test_fn()
            results.append((name, True, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"[FAIL] {name} failed: {e}")
    
    print("\n" + "="*50)
    print("FINRADAR TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    
    for name, ok, err in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if err:
            print(f"         Error: {err[:100]}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
