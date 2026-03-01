from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    SEC_10K = "10-K"
    SEC_10Q = "10-Q"
    SEC_8K = "8-K"
    EARNINGS_CALL = "earnings_call"
    PRESS_RELEASE = "press_release"
    INVESTOR_PRESENTATION = "investor_presentation"


class CompanySize(str, Enum):
    STARTUP = "startup"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class FundingStage(str, Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D = "series_d_plus"
    PUBLIC = "public"


class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    ticker: str | None = None
    name: str
    cik: str | None = None
    industry: str | None = None
    sector: str | None = None
    market_cap: float | None = None
    employees: int | None = None
    founded_year: int | None = None
    headquarters: str | None = None
    website: str | None = None
    size: CompanySize = CompanySize.ENTERPRISE
    funding_stage: FundingStage | None = None
    funding_total: float | None = None
    last_funding_date: datetime | None = None
    key_executives: list[dict[str, str]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FinancialReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    company_id: str
    report_type: ReportType
    filing_date: datetime
    period_end_date: datetime | None = None
    fiscal_year: int | None = None
    fiscal_quarter: int | None = None
    source_url: str
    local_path: str | None = None
    raw_text: str | None = None
    summary: str | None = None
    key_metrics: dict[str, Any] = Field(default_factory=dict)
    sentiment_score: float | None = None
    risk_factors: list[str] = Field(default_factory=list)
    management_outlook: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    processed_at: datetime | None = None


class StartupTeam(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    company_name: str
    description: str | None = None
    industry: str | None = None
    funding_stage: FundingStage = FundingStage.SEED
    funding_total: float | None = None
    last_funding_round: str | None = None
    last_funding_date: datetime | None = None
    valuation: float | None = None
    employees_count: int | None = None
    founded_year: int | None = None
    location: str | None = None
    website: str | None = None
    crunchbase_url: str | None = None
    linkedin_url: str | None = None
    founders: list[dict[str, str]] = Field(default_factory=list)
    key_hires: list[dict[str, str]] = Field(default_factory=list)
    notable_investors: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    hiring_signals: list[str] = Field(default_factory=list)
    growth_signals: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    overall_score: float | None = None
    investment_thesis: str | None = None
    sources: list[str] = Field(default_factory=list)
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    alert_type: str
    severity: Literal["low", "medium", "high", "critical"]
    title: str
    message: str
    company_id: str | None = None
    startup_id: str | None = None
    report_id: str | None = None
    action_required: bool = False
    action_description: str | None = None
    sent_at: datetime | None = None
    acknowledged_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    query: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    companies_mentioned: list[str] = Field(default_factory=list)
    reports_referenced: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
