import pytest
from app.models.principles import InvestmentPrinciple, Operator
from app.services.investment_principles import evaluate_principles, EvaluationStatus

@pytest.fixture
def test_principles():
    """Provides test principles to the engine."""
    return [
        InvestmentPrinciple(
            identifier="ROE_GT_15", 
            name="ROE Rule", 
            metric="roe", 
            operator=Operator.GREATER_THAN, 
            threshold=0.15, 
            description="ROE > 15%"
        ),
        InvestmentPrinciple(
            identifier="DEBT_LT_05", 
            name="Debt Rule", 
            metric="debt_to_equity", 
            operator=Operator.LESS_THAN, 
            threshold=0.5, 
            description="D/E < 0.5"
        ),
        InvestmentPrinciple(
            identifier="PE_LT_30", 
            name="PE Rule", 
            metric="pe_ratio", 
            operator=Operator.LESS_THAN, 
            threshold=30.0, 
            description="PE < 30"
        )
    ]

def test_engine_pass_fail_unavailable(test_principles):
    """
    Tests the fundamental compliance rules:
    - Passed checks increment the counter.
    - Failed checks process correctly.
    - Missing metrics resolve strictly to UNAVAILABLE without failing or faking zeros.
    - Disclaimers are attached.
    """
    metrics = {
        "roe": 0.20,             # Expected to Pass (0.20 > 0.15)
        "debt_to_equity": 0.60,  # Expected to Fail (0.60 > 0.5 required)
        "pe_ratio": None         # Expected to be UNAVAILABLE
    }

    report = evaluate_principles(metrics, test_principles)

    assert report.total_count == 3
    assert report.passed_count == 1
    
    # 1. Test Pass Scenario
    assert report.evaluations[0].principle_name == "ROE Rule"
    assert report.evaluations[0].status == EvaluationStatus.PASS
    assert report.evaluations[0].actual_value == 0.20

    # 2. Test Fail Scenario
    assert report.evaluations[1].principle_name == "Debt Rule"
    assert report.evaluations[1].status == EvaluationStatus.FAIL
    assert report.evaluations[1].actual_value == 0.60

    # 3. Test Unavailable Scenario (Missing Data)
    assert report.evaluations[2].principle_name == "PE Rule"
    assert report.evaluations[2].status == EvaluationStatus.UNAVAILABLE
    assert report.evaluations[2].actual_value is None
    assert "unavailable for this company" in report.evaluations[2].explanation

    # 4. Test Summary and Compliance Disclaimer
    assert "1 out of 3 principles passed" in report.summary_text
    assert "not a buy signal" in report.summary_text.lower()
    assert "investment recommendation" in report.summary_text.lower()

