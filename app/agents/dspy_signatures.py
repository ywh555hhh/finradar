import dspy
from pydantic import BaseModel, Field
from app.core.config import settings


class FinancialSentiment(dspy.Signature):
    analyzed_text: str = dspy.InputField(desc="Financial text to analyze")
    sentiment: str = dspy.OutputField(desc="Sentiment: bullish, bearish, or neutral")
    confidence: float = dspy.OutputField(desc="Confidence score 0-1")
    key_factors: list[str] = dspy.OutputField(desc="Key factors affecting sentiment")


class ExtractCompanyInfo(dspy.Signature):
    document_text: str = dspy.InputField(desc="SEC filing or financial document")
    company_name: str = dspy.OutputField()
    ticker: str = dspy.OutputField()
    fiscal_year: int = dspy.OutputField()
    revenue: float | None = dspy.OutputField()
    net_income: float | None = dspy.OutputField()
    key_risks: list[str] = dspy.OutputField()
    management_outlook: str = dspy.OutputField()


class SummarizeReport(dspy.Signature):
    report_text: str = dspy.InputField(desc="Full text of financial report")
    max_words: int = dspy.InputField(desc="Maximum words in summary")
    summary: str = dspy.OutputField(desc="Executive summary of the report")
    key_highlights: list[str] = dspy.OutputField(desc="Top 3-5 key highlights")
    action_items: list[str] = dspy.OutputField(desc="Recommended actions based on report")


class EvaluateStartup(dspy.Signature):
    startup_data: str = dspy.InputField(desc="Startup information including funding, team, traction")
    industry: str = dspy.InputField(desc="Industry context")
    overall_score: float = dspy.OutputField(desc="Investment potential score 0-100")
    strengths: list[str] = dspy.OutputField(desc="Key strengths")
    weaknesses: list[str] = dspy.OutputField(desc="Key weaknesses or risks")
    investment_thesis: str = dspy.OutputField(desc="Brief investment thesis")


class CompareCompanies(dspy.Signature):
    companies_data: str = dspy.InputField(desc="Data for multiple companies")
    comparison_criteria: list[str] = dspy.InputField(desc="Metrics to compare")
    comparison_matrix: dict[str, dict[str, float | str]] = dspy.OutputField()
    winner: str = dspy.OutputField(desc="Best company based on criteria")
    rationale: str = dspy.OutputField(desc="Explanation of comparison")


class GenerateAlert(dspy.Signature):
    event_data: str = dspy.InputField(desc="Event that triggered the alert")
    alert_type: str = dspy.InputField(desc="Type of alert (earnings, funding, risk)")
    title: str = dspy.OutputField(desc="Alert title")
    message: str = dspy.OutputField(desc="Detailed alert message")
    severity: str = dspy.OutputField(desc="Severity: low, medium, high, or critical")
    action_required: bool = dspy.OutputField()
    action_description: str = dspy.OutputField()


def configure_dspy():
    lm = dspy.LM(
        model=settings.dspy_lm_model,
        temperature=settings.dspy_lm_temperature,
    )
    dspy.configure(lm=lm)
    return lm


class FinancialAnalysisAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.sentiment_analyzer = dspy.ChainOfThought(FinancialSentiment)
        self.company_extractor = dspy.ChainOfThought(ExtractCompanyInfo)
        self.report_summarizer = dspy.ChainOfThought(SummarizeReport)
        
    def analyze_sentiment(self, text: str) -> dict:
        result = self.sentiment_analyzer(analyzed_text=text)
        return {
            "sentiment": result.sentiment,
            "confidence": result.confidence,
            "key_factors": result.key_factors,
        }
    
    def extract_company(self, document: str) -> dict:
        result = self.company_extractor(document_text=document)
        return {
            "company_name": result.company_name,
            "ticker": result.ticker,
            "fiscal_year": result.fiscal_year,
            "revenue": result.revenue,
            "net_income": result.net_income,
            "key_risks": result.key_risks,
            "management_outlook": result.management_outlook,
        }
    
    def summarize_report(self, report: str, max_words: int = 300) -> dict:
        result = self.report_summarizer(report_text=report, max_words=max_words)
        return {
            "summary": result.summary,
            "key_highlights": result.key_highlights,
            "action_items": result.action_items,
        }


class StartupDiscoveryAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.evaluator = dspy.ChainOfThought(EvaluateStartup)
        self.comparator = dspy.ChainOfThought(CompareCompanies)
        
    def evaluate_startup(self, startup_data: str, industry: str) -> dict:
        result = self.evaluator(startup_data=startup_data, industry=industry)
        return {
            "overall_score": result.overall_score,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "investment_thesis": result.investment_thesis,
        }
    
    def compare_startups(self, startups: list[dict], criteria: list[str]) -> dict:
        import json
        startups_json = json.dumps(startups, indent=2)
        result = self.comparator(companies_data=startups_json, comparison_criteria=criteria)
        return {
            "comparison_matrix": result.comparison_matrix,
            "winner": result.winner,
            "rationale": result.rationale,
        }


class AlertGeneratorAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought(GenerateAlert)
        
    def generate_alert(self, event_data: str, alert_type: str) -> dict:
        result = self.generator(event_data=event_data, alert_type=alert_type)
        return {
            "title": result.title,
            "message": result.message,
            "severity": result.severity,
            "action_required": result.action_required,
            "action_description": result.action_description,
        }
