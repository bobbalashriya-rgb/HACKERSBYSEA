import pytest
from app.services.company_data import (
    NormalizedCompanyData, 
    CompanyProfile, 
    FinancialStatements, 
    HistoricalPrice
)
from app.services.financial_metrics import calculate_metrics

@pytest.fixture
def dummy_company_data():
    """Provides a controlled dataset mimicking yfinance's normalized output."""
    profile = CompanyProfile(
        ticker="TEST",
        market_cap=1000000
    )
    
    financials = FinancialStatements(
        income_statement={
            "2023-12-31": {
                "Total Revenue": 500000.0,
                "Net Income": 50000.0,
                "EBIT": 70000.0,
                "Operating Income": 60000.0
            },
            "2022-12-31": {
                "Total Revenue": 400000.0,
                "Net Income": 40000.0,
                "EBIT": 60000.0,
                "Operating Income": 50000.0
            }
        },
        balance_sheet={
            "2023-12-31": {
                "Total Assets": 1000000.0,
                "Current Liabilities": 200000.0,
                "Stockholders Equity": 500000.0,
                "Total Debt": 100000.0
            }
        },
        cash_flow={
            "2023-12-31": {
                "Operating Cash Flow": 80000.0,
                "Capital Expenditure": -20000.0  # CapEx is usually negative
            }
        }
    )
    
    return NormalizedCompanyData(
        profile=profile,
        financials=financials,
        historical_prices=[]
    )

@pytest.fixture
def missing_company_data():
    """Provides a dataset missing several key metrics to test null safety."""
    profile = CompanyProfile(ticker="MISSING", market_cap=None)
    financials = FinancialStatements(
        income_statement={"2023-12-31": {"Total Revenue": 500000.0}},
        balance_sheet={"2023-12-31": {"Total Assets": 1000000.0}},
        cash_flow={"2023-12-31": {}}
    )
    return NormalizedCompanyData(profile=profile, financials=financials, historical_prices=[])

def test_calculate_metrics_success(dummy_company_data):
    """Tests if all financial metrics are calculated correctly from valid source data."""
    result = calculate_metrics(dummy_company_data)
    metrics = result.metrics
    
    # Assert Current Values
    assert metrics.revenue == 500000.0
    assert metrics.net_profit == 50000.0
    
    # Assert Growth
    # Revenue Growth: (500k - 400k) / 400k = 25%
    assert metrics.revenue_growth == 0.25
    # Profit Growth: (50k - 40k) / 40k = 25%
    assert metrics.profit_growth == 0.25
    
    # Assert Ratios
    # ROE: Net Income / Equity = 50k / 500k = 10%
    assert metrics.roe == 0.10
    
    # ROCE: EBIT / (Assets - Current Liab) = 70k / (1000k - 200k) = 70k / 800k = 8.75%
    assert metrics.roce == 0.0875
    
    # Debt to Equity: Debt / Equity = 100k / 500k = 20%
    assert metrics.debt_to_equity == 0.20
    
    # Operating Margin: Op Income / Revenue = 60k / 500k = 12%
    assert metrics.operating_margin == 0.12
    
    # Free Cash Flow: OCF - abs(CapEx) = 80k - 20k = 60k
    assert metrics.free_cash_flow == 60000.0
    
    # P/E Ratio: Market Cap / Net Profit = 1m / 50k = 20
    assert metrics.pe_ratio == 20.0

def test_historical_datasets_ordering(dummy_company_data):
    """Tests if the historical data is sorted ascendingly for frontend charts."""
    result = calculate_metrics(dummy_company_data)
    history = result.historical_data
    
    assert len(history) == 2
    # Ensure chronological order (oldest first)
    assert history[0].date == "2022-12-31"
    assert history[1].date == "2023-12-31"
    
    assert history[0].revenue == 400000.0
    assert history[1].revenue == 500000.0

def test_calculate_metrics_missing_data(missing_company_data):
    """Tests if missing input data safely results in None without estimating or crashing."""
    result = calculate_metrics(missing_company_data)
    metrics = result.metrics
    
    assert metrics.revenue == 500000.0
    assert metrics.revenue_growth is None
    assert metrics.net_profit is None
    assert metrics.profit_growth is None
    assert metrics.roe is None
    assert metrics.roce is None
    assert metrics.free_cash_flow is None
    assert metrics.pe_ratio is None

