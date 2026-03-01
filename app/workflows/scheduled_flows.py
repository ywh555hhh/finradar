from datetime import datetime, timedelta
from typing import Any

from prefect import flow, task, get_run_logger
from prefect.cache_policies import NONE

from app.core import settings
from app.sources import YahooFinanceSource, SECSource
from app.agents.dspy_signatures import FinancialAnalysisAgent, configure_dspy


@task(cache_policy=NONE, retries=3, retry_delay_seconds=60)
async def fetch_company_financials(ticker: str) -> dict[str, Any]:
    yf = YahooFinanceSource()
    info = await yf.get_company_info(ticker)
    financials = await yf.get_financials(ticker)
    return {"info": info, "financials": financials}


@task(cache_policy=NONE, retries=2, retry_delay_seconds=30)
async def analyze_financial_data(ticker: str, data: dict) -> dict[str, Any]:
    configure_dspy()
    agent = FinancialAnalysisAgent()
    
    description = data["info"].get("longBusinessSummary", "")
    sentiment = agent.analyze_sentiment(description) if description else {}
    
    return {
        "ticker": ticker,
        "company_name": data["info"].get("longName", ticker),
        "sentiment": sentiment,
        "market_cap": data["info"].get("marketCap", 0),
        "sector": data["info"].get("sector", "Unknown"),
    }


@flow(name="Daily Financial Scan", log_prints=True)
async def daily_financial_scan(
    tickers: list[str] | None = None,
    years_back: int = 1,
    generate_alerts: bool = True,
) -> dict[str, Any]:
    logger = get_run_logger()
    
    if not tickers:
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
    
    results = {
        "companies_scanned": 0,
        "reports_processed": 0,
        "alerts_generated": 0,
        "analysis": [],
    }
    
    for ticker in tickers:
        try:
            data = await fetch_company_financials(ticker)
            analysis = await analyze_financial_data(ticker, data)
            results["analysis"].append(analysis)
            results["companies_scanned"] += 1
            logger.info(f"Analyzed {ticker}: {analysis['company_name']}")
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
    
    return results


@flow(name="Weekly Startup Discovery", log_prints=True)
async def weekly_startup_discovery(
    industries: list[str] | None = None,
    funding_stages: list[str] | None = None,
    max_startups: int = 50,
    min_score: float = 60.0,
) -> dict[str, Any]:
    from app.workflows.discovery_flow import continuous_discovery
    
    return await continuous_discovery(
        industries=industries,
        funding_stages=funding_stages,
        min_fit_score=min_score,
        notify_startups=True,
        notify_user=True,
        max_discoveries=max_startups,
    )


@flow(name="Earnings Monitor", log_prints=True)
async def earnings_monitor(
    tickers: list[str] | None = None,
    check_earnings_dates: bool = True,
    analyze_news: bool = True,
) -> dict[str, Any]:
    logger = get_run_logger()
    
    if not tickers:
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    
    yf = YahooFinanceSource()
    
    results = {
        "companies_checked": 0,
        "upcoming_earnings": [],
        "alerts_sent": 0,
    }
    
    for ticker in tickers:
        try:
            if check_earnings_dates:
                earnings = await yf.get_earnings_dates(ticker)
                if earnings:
                    results["upcoming_earnings"].extend(earnings[:3])
            
            if analyze_news:
                news = await yf.get_news(ticker, limit=5)
                for article in news:
                    if article.get("sentiment") == "negative":
                        results["alerts_sent"] += 1
                        break
            
            results["companies_checked"] += 1
            
        except Exception as e:
            logger.error(f"Error monitoring {ticker}: {e}")
    
    return results


@flow(name="SEC Filing Monitor", log_prints=True)
async def sec_filing_monitor(
    tickers: list[str] | None = None,
    filing_types: list[str] | None = None,
) -> dict[str, Any]:
    logger = get_run_logger()
    
    if not tickers:
        tickers = ["AAPL", "MSFT", "GOOGL"]
    if not filing_types:
        filing_types = ["10-K", "10-Q", "8-K"]
    
    sec = SECSource()
    
    results = {
        "filings_downloaded": 0,
        "filings_analyzed": 0,
        "alerts": [],
    }
    
    for ticker in tickers:
        try:
            if "10-K" in filing_types:
                filings = await sec.download_10k(ticker, years=1)
                results["filings_downloaded"] += len(filings)
            
            if "10-Q" in filing_types:
                filings = await sec.download_10q(ticker, quarters=4)
                results["filings_downloaded"] += len(filings)
            
            if "8-K" in filing_types:
                filings = await sec.download_8k(ticker, days=30)
                results["filings_downloaded"] += len(filings)
                
            logger.info(f"Downloaded filings for {ticker}")
            
        except Exception as e:
            logger.error(f"Error downloading SEC filings for {ticker}: {e}")
    
    return results


if __name__ == "__main__":
    import asyncio
    
    result = asyncio.run(daily_financial_scan())
    print(result)
