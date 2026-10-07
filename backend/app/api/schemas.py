from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from app.services.company_data import NormalizedCompanyData
from app.services.financial_metrics import FinancialMetricsResult
from app.services.investment_principles import PrincipleEvaluationReport

class PrincipleSchema(BaseModel):
    identifier: str
    name: str
    metric: str
    operator: str
    threshold: float
    description: str
    model_config = ConfigDict(from_attributes=True)

class PrincipleUpdate(BaseModel):
    threshold: float

class VisualThesisSummary(BaseModel):
    financial_quality: str
    valuation: str
    key_strengths: List[str]
    key_concerns: List[str]
    data_completeness: str

class AIResearchReport(BaseModel):
    visual_summary: VisualThesisSummary
    investment_thesis: str
    strengthens_thesis: str
    weakens_thesis: str
    important_financial_risk: str
    valuation_concerns: str
    concerns: str
    data_limitations: str
    investigate_next: str
    invalidate_thesis: str
    disclaimer: str

class AnalyzeRequest(BaseModel):
    ticker: str

class AnalyzeResponse(BaseModel):
    company_data: NormalizedCompanyData
    metrics: FinancialMetricsResult
    evaluation: PrincipleEvaluationReport
    ai_report: Optional[AIResearchReport] = None

class AskRequest(BaseModel):
    question: str
    context: Dict[str, Any]

class AskResponse(BaseModel):
    answer: str

class CompareRequest(BaseModel):
    tickers: List[str]

class ComparisonData(BaseModel):
    ticker: str
    metrics: Dict[str, Any]
    evaluations: Dict[str, Any]

class CompareResponse(BaseModel):
    companies: List[ComparisonData]
    ai_comparison: str
