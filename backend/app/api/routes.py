from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import SessionLocal
from app.api.schemas import (
    PrincipleSchema, PrincipleUpdate, AnalyzeRequest, AnalyzeResponse, 
    AskRequest, AskResponse, CompareRequest, CompareResponse, ComparisonData
)
from app.models.principles import InvestmentPrinciple
from app.services.company_data import fetch_company_data, FinancialDataError, NormalizedCompanyData
from app.services.financial_metrics import calculate_metrics
from app.services.investment_principles import evaluate_principles
from app.services.ai_research import generate_research_report, answer_financial_question, generate_comparison_report

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/company/{ticker}", response_model=NormalizedCompanyData)
def get_company(ticker: str):
    try:
        return fetch_company_data(ticker)
    except FinancialDataError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/principles", response_model=List[PrincipleSchema])
def get_principles(db: Session = Depends(get_db)):
    return db.query(InvestmentPrinciple).all()

@router.put("/principles/{identifier}")
def update_principle(identifier: str, req: PrincipleUpdate, db: Session = Depends(get_db)):
    p = db.query(InvestmentPrinciple).filter(InvestmentPrinciple.identifier == identifier).first()
    if not p:
        raise HTTPException(status_code=404, detail="Principle not found")
    p.threshold = req.threshold
    db.commit()
    return {"status": "success", "threshold": p.threshold}

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_ticker(req: AnalyzeRequest, db: Session = Depends(get_db)):
    ticker = req.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker cannot be empty.")
    try:
        company_data = fetch_company_data(ticker)
        metrics_result = calculate_metrics(company_data)
        metrics_dict = metrics_result.metrics.model_dump()
        principles = db.query(InvestmentPrinciple).all()
        evaluation_report = evaluate_principles(metrics_dict, principles)
        
        ai_report_dict = generate_research_report(
            company_data, metrics_dict, evaluation_report.model_dump()
        )
        return AnalyzeResponse(
            company_data=company_data,
            metrics=metrics_result,
            evaluation=evaluation_report,
            ai_report=ai_report_dict
        )
    except FinancialDataError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    """Processes interactive Q&A utilizing bounded application context."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    ans = answer_financial_question(req.context, req.question)
    return AskResponse(answer=ans)

@router.post("/compare", response_model=CompareResponse)
def compare_companies(req: CompareRequest, db: Session = Depends(get_db)):
    """Executes a full pipeline analysis on two tickers for a head-to-head comparison."""
    if len(req.tickers) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 tickers are required for comparison.")
    
    principles = db.query(InvestmentPrinciple).all()
    companies = []
    contexts = []
    
    try:
        for t in req.tickers:
            t_clean = t.strip().upper()
            c_data = fetch_company_data(t_clean)
            c_metrics = calculate_metrics(c_data)
            c_evals = evaluate_principles(c_metrics.metrics.model_dump(), principles)
            
            companies.append(ComparisonData(
                ticker=t_clean,
                metrics=c_metrics.metrics.model_dump(),
                evaluations=c_evals.model_dump()
            ))
            contexts.append({
                "profile": c_data.profile.model_dump(),
                "metrics": c_metrics.metrics.model_dump(),
                "evaluations": c_evals.model_dump()
            })
            
        ai_comp = generate_comparison_report(contexts[0], contexts[1])
        return CompareResponse(companies=companies, ai_comparison=ai_comp)
        
    except FinancialDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
