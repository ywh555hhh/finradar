from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from pathlib import Path
import asyncio
import httpx
import yfinance as yf
from sec_edgar_downloader import Downloader

from app.core import settings, FinancialReport, ReportType, Company


@dataclass
class SECSource:
    user_agent: str = field(default_factory=lambda: settings.sec_user_agent)
    download_path: str = "./data/sec_filings"
    _dl: Downloader | None = field(default=None, repr=False)
    
    @property
    def dl(self) -> Downloader:
        if self._dl is None:
            Path(self.download_path).mkdir(parents=True, exist_ok=True)
            self._dl = Downloader(
                company_name="FinRadar",
                email_address="contact@finradar.ai",
                download_path=self.download_path,
            )
        return self._dl
    
    async def download_10k(self, ticker: str, years: int = 3) -> list[str]:
        def _download():
            self.dl.get("10-K", ticker, after=datetime.now() - timedelta(days=years * 365))
            ticker_path = Path(self.download_path) / "sec-edgar-filings" / ticker / "10-K"
            return [str(p) for p in ticker_path.glob("*/*.txt")] if ticker_path.exists() else []
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)
    
    async def download_10q(self, ticker: str, quarters: int = 4) -> list[str]:
        def _download():
            self.dl.get("10-Q", ticker, after=datetime.now() - timedelta(days=quarters * 90))
            ticker_path = Path(self.download_path) / "sec-edgar-filings" / ticker / "10-Q"
            return [str(p) for p in ticker_path.glob("*/*.txt")] if ticker_path.exists() else []
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)
    
    async def download_8k(self, ticker: str, days: int = 30) -> list[str]:
        def _download():
            self.dl.get("8-K", ticker, after=datetime.now() - timedelta(days=days))
            ticker_path = Path(self.download_path) / "sec-edgar-filings" / ticker / "8-K"
            return [str(p) for p in ticker_path.glob("*/*.txt")] if ticker_path.exists() else []
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)
    
    async def get_company_facts(self, cik: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json",
                headers={"User-Agent": self.user_agent},
            )
            resp.raise_for_status()
            return resp.json()


@dataclass
class YahooFinanceSource:
    async def get_company_info(self, ticker: str) -> dict[str, Any]:
        def _get():
            stock = yf.Ticker(ticker)
            return stock.info
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)
    
    async def get_financials(self, ticker: str) -> dict[str, Any]:
        def _get():
            stock = yf.Ticker(ticker)
            return {
                "income_stmt": stock.financials.to_dict() if stock.financials is not None else {},
                "balance_sheet": stock.balance_sheet.to_dict() if stock.balance_sheet is not None else {},
                "cash_flow": stock.cashflow.to_dict() if stock.cashflow is not None else {},
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)
    
    async def get_earnings_dates(self, ticker: str) -> list[dict]:
        def _get():
            stock = yf.Ticker(ticker)
            dates = stock.earnings_dates
            if dates is None or dates.empty:
                return []
            return dates.reset_index().to_dict("records")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)
    
    async def get_news(self, ticker: str, limit: int = 10) -> list[dict]:
        def _get():
            stock = yf.Ticker(ticker)
            return stock.news[:limit] if stock.news else []
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)
    
    async def get_historical_data(
        self, ticker: str, period: str = "1y"
    ) -> list[dict]:
        def _get():
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return []
            return hist.reset_index().to_dict("records")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)


@dataclass
class AlphaVantageSource:
    api_key: str = field(default_factory=lambda: settings.alpha_vantage_key)
    base_url: str = "https://www.alphavantage.co/query"
    
    async def _query(self, function: str, **params) -> dict:
        params = {"function": function, "apikey": self.api_key, **params}
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.base_url, params=params)
            resp.raise_for_status()
            return resp.json()
    
    async def get_company_overview(self, symbol: str) -> dict:
        return await self._query("OVERVIEW", symbol=symbol)
    
    async def get_income_statement(self, symbol: str) -> dict:
        return await self._query("INCOME_STATEMENT", symbol=symbol)
    
    async def get_balance_sheet(self, symbol: str) -> dict:
        return await self._query("BALANCE_SHEET", symbol=symbol)
    
    async def get_cash_flow(self, symbol: str) -> dict:
        return await self._query("CASH_FLOW", symbol=symbol)
    
    async def get_earnings(self, symbol: str) -> dict:
        return await self._query("EARNINGS", symbol=symbol)
    
    async def get_news_sentiment(self, tickers: str | None = None) -> dict:
        params = {}
        if tickers:
            params["tickers"] = tickers
        return await self._query("NEWS_SENTIMENT", **params)
