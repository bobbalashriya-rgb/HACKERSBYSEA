import sys
import os

# Ensure backend directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.api.schemas import AnalyzeRequest
from app.api.routes import analyze_ticker
from app.core.database import SessionLocal
from fastapi import HTTPException

def test_ticker(ticker_name):
    print(f"\n=== Testing Ticker: {ticker_name} ===")
    db = SessionLocal()
    req = AnalyzeRequest(ticker=ticker_name)
    try:
        res = analyze_ticker(req, db)
        print(f"SUCCESS! Found company: {res.company_data.profile.name}")
        print(f"Market Cap: {res.company_data.profile.market_cap}")
        print(f"Revenue: {res.metrics.metrics.revenue}")
        print(f"Principles Passed: {res.evaluation.passed_count} / {res.evaluation.total_count}")
        
        # Check unavailable logic
        unavailable = [p.principle_name for p in res.evaluation.evaluations if p.status == 'Unavailable']
        if unavailable:
            print(f"Unavailable metrics for principles: {', '.join(unavailable)}")
            
    except HTTPException as e:
        print(f"HTTP ERROR ({e.status_code}): {e.detail}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_ticker("TCS.NS")
    test_ticker("INFI.NS")
    test_ticker("INVALID_TICKER_999")
