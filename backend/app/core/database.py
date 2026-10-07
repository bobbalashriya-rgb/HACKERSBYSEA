from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.principles import Base, InvestmentPrinciple, Operator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finolitics.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DEFAULT_PRINCIPLES = [
    {
        "identifier": "ROE_GT_15", 
        "name": "High Return on Equity", 
        "metric": "roe", 
        "operator": Operator.GREATER_THAN, 
        "threshold": 0.15, 
        "description": "Checks if Return on Equity is strictly greater than 15%."
    },
    {
        "identifier": "DEBT_EQ_LT_05", 
        "name": "Low Debt to Equity", 
        "metric": "debt_to_equity", 
        "operator": Operator.LESS_THAN, 
        "threshold": 0.5, 
        "description": "Checks if Debt to Equity ratio is less than 0.5."
    },
    {
        "identifier": "REV_GROWTH_GT_10", 
        "name": "Strong Revenue Growth", 
        "metric": "revenue_growth", 
        "operator": Operator.GREATER_THAN, 
        "threshold": 0.10, 
        "description": "Checks if year-over-year revenue growth is greater than 10%."
    },
    {
        "identifier": "OP_MARGIN_GT_15", 
        "name": "Healthy Operating Margin", 
        "metric": "operating_margin", 
        "operator": Operator.GREATER_THAN, 
        "threshold": 0.15, 
        "description": "Checks if the operating margin is greater than 15%."
    },
    {
        "identifier": "FCF_POSITIVE", 
        "name": "Positive Free Cash Flow", 
        "metric": "free_cash_flow", 
        "operator": Operator.GREATER_THAN, 
        "threshold": 0.0, 
        "description": "Checks if the free cash flow is strictly positive."
    },
    {
        "identifier": "PE_LT_30", 
        "name": "Reasonable Valuation (P/E)", 
        "metric": "pe_ratio", 
        "operator": Operator.LESS_THAN, 
        "threshold": 30.0, 
        "description": "Checks if the Price to Earnings ratio is less than 30."
    }
]

def init_db():
    """Initializes the database schema and seeds default investment principles if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(InvestmentPrinciple).count() == 0:
        for p_dict in DEFAULT_PRINCIPLES:
            db.add(InvestmentPrinciple(**p_dict))
        db.commit()
    db.close()

