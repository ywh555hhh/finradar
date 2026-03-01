from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

from app.core import settings
from app.workflows import daily_financial_scan, weekly_startup_discovery, earnings_monitor


app = FastAPI(
    title=settings.project_name,
    description="AI-powered financial intelligence with scheduled reports and startup discovery",
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    tickers: list[str]
    years_back: int = 1
    generate_alerts: bool = True


class StartupDiscoveryRequest(BaseModel):
    industries: list[str] | None = None
    funding_stages: list[str] | None = None
    max_startups: int = 50
    min_score: float = 60.0


class EarningsMonitorRequest(BaseModel):
    tickers: list[str]
    check_earnings_dates: bool = True
    analyze_news: bool = True


class QueryRequest(BaseModel):
    query: str
    context: dict | None = None


@app.get("/")
async def root():
    return {
        "name": settings.project_name,
        "version": settings.version,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/scan/daily")
async def trigger_daily_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        daily_financial_scan.fn,
        tickers=request.tickers,
        years_back=request.years_back,
        generate_alerts=request.generate_alerts,
    )
    return {
        "status": "initiated",
        "message": f"Daily scan started for {len(request.tickers)} tickers",
    }


@app.post("/api/v1/scan/startups")
async def trigger_startup_discovery(request: StartupDiscoveryRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        weekly_startup_discovery.fn,
        industries=request.industries,
        funding_stages=request.funding_stages,
        max_startups=request.max_startups,
        min_score=request.min_score,
    )
    return {
        "status": "initiated",
        "message": "Startup discovery scan started",
    }


@app.post("/api/v1/monitor/earnings")
async def trigger_earnings_monitor(request: EarningsMonitorRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        earnings_monitor.fn,
        tickers=request.tickers,
        check_earnings_dates=request.check_earnings_dates,
        analyze_news=request.analyze_news,
    )
    return {
        "status": "initiated",
        "message": f"Earnings monitor started for {len(request.tickers)} tickers",
    }


@app.get("/api/v1/companies/{ticker}")
async def get_company(ticker: str):
    from app.sources import YahooFinanceSource
    
    yf = YahooFinanceSource()
    info = await yf.get_company_info(ticker)
    financials = await yf.get_financials(ticker)
    
    return {
        "info": info,
        "financials": financials,
    }


@app.get("/api/v1/companies/{ticker}/news")
async def get_company_news(ticker: str, limit: int = 10):
    from app.sources import YahooFinanceSource
    
    yf = YahooFinanceSource()
    news = await yf.get_news(ticker, limit=limit)
    return {"news": news}


@app.get("/api/v1/startups/search")
async def search_startups(
    query: str,
    industries: str | None = None,
    funding_stages: str | None = None,
):
    from app.sources import CrunchbaseSource
    
    cb = CrunchbaseSource()
    startups = await cb.search_organizations(
        query=query,
        industries=industries.split(",") if industries else None,
        funding_stages=funding_stages.split(",") if funding_stages else None,
    )
    return {"startups": startups}


@app.post("/api/v1/query")
async def query_financial_data(request: QueryRequest):
    from app.agents.dspy_signatures import configure_dspy, FinancialAnalysisAgent
    
    configure_dspy()
    agent = FinancialAnalysisAgent()
    
    sentiment = agent.analyze_sentiment(request.query)
    return {
        "query": request.query,
        "sentiment": sentiment,
    }
