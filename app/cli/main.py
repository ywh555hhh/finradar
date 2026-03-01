import asyncio
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.core import settings
from app.workflows import daily_financial_scan, weekly_startup_discovery, earnings_monitor
from app.sources import YahooFinanceSource, CrunchbaseSource

app = typer.Typer(name="finradar", help="FinRadar CLI - Financial Intelligence Agent")
console = Console()


@app.command()
def scan(
    tickers: list[str] = typer.Argument(..., help="Stock tickers to scan"),
    years: int = typer.Option(1, "--years", "-y", help="Years of filings to analyze"),
    alerts: bool = typer.Option(True, "--alerts/--no-alerts", help="Generate alerts"),
):
    daily_financial_scan(
        tickers=tickers,
        years_back=years,
        generate_alerts=alerts,
    )
    console.print(f"[green]Scan complete for {len(tickers)} tickers[/green]")


@app.command()
def discover(
    industry: str = typer.Option("AI", "--industry", "-i", help="Industry to search"),
    stage: str = typer.Option("Series A", "--stage", "-s", help="Funding stage"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max startups to analyze"),
):
    async def _discover():
        results = await weekly_startup_discovery(
            industries=[industry],
            funding_stages=[stage],
            max_startups=limit,
        )
        return results
    
    results = asyncio.run(_discover())
    
    console.print(f"\n[bold green]Discovered {results['startups_discovered']} startups[/bold green]")
    console.print(f"High potential: {results['high_potential_count']}")
    
    if results["top_startups"]:
        table = Table(title="Top Startups")
        table.add_column("Name", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Thesis", style="white")
        
        for startup in results["top_startups"][:5]:
            table.add_row(
                startup.get("name", "Unknown"),
                str(startup.get("evaluation", {}).get("overall_score", 0)),
                startup.get("evaluation", {}).get("investment_thesis", "")[:50] + "...",
            )
        
        console.print(table)


@app.command()
def monitor(
    tickers: list[str] = typer.Argument(..., help="Tickers to monitor"),
    news: bool = typer.Option(True, "--news/--no-news", help="Analyze news"),
):
    async def _monitor():
        return await earnings_monitor(
            tickers=tickers,
            check_earnings_dates=True,
            analyze_news=news,
        )
    
    results = asyncio.run(_monitor())
    
    console.print(f"\n[bold]Earnings Monitor Results[/bold]")
    console.print(f"Companies checked: {results['companies_checked']}")
    console.print(f"Alerts sent: {results['alerts_sent']}")
    
    if results["upcoming_earnings"]:
        table = Table(title="Upcoming Earnings")
        table.add_column("Ticker", style="cyan")
        table.add_column("Date", style="yellow")
        
        for earning in results["upcoming_earnings"]:
            table.add_row(earning["ticker"], earning["date"])
        
        console.print(table)


@app.command()
def info(ticker: str = typer.Argument(..., help="Stock ticker")):
    async def _info():
        yf = YahooFinanceSource()
        info = await yf.get_company_info(ticker)
        return info
    
    data = asyncio.run(_info())
    
    table = Table(title=f"Company Info: {ticker}")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    fields = [
        ("Name", data.get("longName", "N/A")),
        ("Sector", data.get("sector", "N/A")),
        ("Industry", data.get("industry", "N/A")),
        ("Market Cap", f"${data.get('marketCap', 0):,.0f}"),
        ("Employees", str(data.get("fullTimeEmployees", "N/A"))),
        ("Website", data.get("website", "N/A")),
    ]
    
    for field, value in fields:
        table.add_row(field, str(value))
    
    console.print(table)


@app.command()
def config():
    table = Table(title="FinRadar Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    config_items = [
        ("Project Name", settings.project_name),
        ("Version", settings.version),
        ("DSPy Model", settings.dspy_lm_model),
        ("Daily Report Time", settings.daily_report_time),
        ("Weekly Scan Day", settings.weekly_scan_day),
        ("Log Level", settings.log_level),
    ]
    
    for setting, value in config_items:
        table.add_row(setting, str(value))
    
    console.print(table)


if __name__ == "__main__":
    app()
