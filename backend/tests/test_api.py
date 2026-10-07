from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.services.company_data import FinancialDataError, NormalizedCompanyData, CompanyProfile, FinancialStatements

client = TestClient(app)

@patch("app.api.routes.fetch_company_data")
def test_analyze_success(mock_fetch):
    """Verifies that the /analyze endpoint correctly connects all 3 layers and returns a combined response."""
    # Mocking the layer 1 output to avoid real network calls to yfinance during tests
    mock_fetch.return_value = NormalizedCompanyData(
        profile=CompanyProfile(ticker="AAPL", market_cap=2000000),
        financials=FinancialStatements(
            income_statement={"2023-12-31": {"Total Revenue": 380000.0, "Net Income": 97000.0}},
            balance_sheet={"2023-12-31": {"Stockholders Equity": 60000.0}},
            cash_flow={"2023-12-31": {}}
        ),
        historical_prices=[]
    )
    
    response = client.post("/api/analyze", json={"ticker": "AAPL"})
    assert response.status_code == 200
    data = response.json()
    
    # Assert Layer 1 returned
    assert data["company_data"]["profile"]["ticker"] == "AAPL"
    
    # Assert Layer 2 calculated
    assert data["metrics"]["metrics"]["revenue"] == 380000.0
    
    # Assert Layer 3 evaluated
    assert "evaluations" in data["evaluation"]
    assert data["evaluation"]["total_count"] == 6  # 6 seeded principles

@patch("app.api.routes.fetch_company_data")
def test_analyze_invalid_ticker(mock_fetch):
    """Verifies that an invalid ticker cleanly returns a 404 HTTP Error."""
    mock_fetch.side_effect = FinancialDataError("Data unavailable for ticker INVALID.")
    
    response = client.post("/api/analyze", json={"ticker": "INVALID"})
    
    assert response.status_code == 404
    assert "Data unavailable" in response.json()["detail"]

@patch("app.api.routes.fetch_company_data")
def test_analyze_missing_financial_data(mock_fetch):
    """Verifies that missing financials don't break the API, yielding None metrics and Unavailable principles."""
    # Mock empty financial statements
    mock_fetch.return_value = NormalizedCompanyData(
        profile=CompanyProfile(ticker="NO_FIN"),
        financials=FinancialStatements(income_statement={}, balance_sheet={}, cash_flow={}),
        historical_prices=[]
    )
    
    response = client.post("/api/analyze", json={"ticker": "NO_FIN"})
    assert response.status_code == 200
    data = response.json()
    
    # Metrics should safely be None
    assert data["metrics"]["metrics"]["revenue"] is None
    
    # Evaluations should cleanly report 'Unavailable'
    evals = data["evaluation"]["evaluations"]
    assert len(evals) == 6
    assert all(e["status"] == "Unavailable" for e in evals)

def test_analyze_empty_request():
    """Verifies standard request validation."""
    response = client.post("/api/analyze", json={"ticker": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

