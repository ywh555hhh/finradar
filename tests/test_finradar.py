import pytest


def test_config_import():
    from app.core import settings
    assert settings.project_name == "FinRadar"


def test_models_import():
    from app.core import Company, FinancialReport, StartupTeam
    assert Company is not None
    assert FinancialReport is not None
    assert StartupTeam is not None


@pytest.mark.asyncio
async def test_yahoo_source():
    from app.sources import YahooFinanceSource
    
    yf = YahooFinanceSource()
    info = await yf.get_company_info("AAPL")
    assert info is not None
    assert "symbol" in info or "shortName" in info


@pytest.mark.asyncio
async def test_techcrunch_source():
    from app.sources import TechCrunchSource
    
    tc = TechCrunchSource()
    articles = await tc.get_funding_news(days=7)
    assert isinstance(articles, list)
