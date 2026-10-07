import enum
from typing import List, Optional, Dict
from pydantic import BaseModel
from app.models.principles import Operator, InvestmentPrinciple

class EvaluationStatus(str, enum.Enum):
    PASS = "Pass"
    FAIL = "Fail"
    UNAVAILABLE = "Unavailable"

class PrincipleEvaluation(BaseModel):
    principle_name: str
    required_threshold: float
    actual_value: Optional[float]
    status: EvaluationStatus
    explanation: Optional[str] = None

class PrincipleEvaluationReport(BaseModel):
    evaluations: List[PrincipleEvaluation]
    passed_count: int
    total_count: int
    summary_text: str

def evaluate_principles(metrics: Dict[str, Optional[float]], principles: List[InvestmentPrinciple]) -> PrincipleEvaluationReport:
    """
    Evaluates a set of financial metrics against configured investment principles.
    Metrics parameter is expected to be a dictionary representation of CalculatedMetrics.
    """
    evaluations = []
    passed_count = 0
    total_count = len(principles)

    for p in principles:
        actual_value = metrics.get(p.metric)
        
        # Missing Data Rule: Never treat as zero, never fail, explicitly flag as UNAVAILABLE
        if actual_value is None:
            evaluations.append(PrincipleEvaluation(
                principle_name=p.name,
                required_threshold=p.threshold,
                actual_value=None,
                status=EvaluationStatus.UNAVAILABLE,
                explanation=f"The required financial metric '{p.metric}' is currently unavailable for this company."
            ))
            continue

        # Mathematical Evaluation Rule
        is_pass = False
        if p.operator == Operator.GREATER_THAN:
            is_pass = actual_value > p.threshold
        elif p.operator == Operator.LESS_THAN:
            is_pass = actual_value < p.threshold
        elif p.operator == Operator.GREATER_THAN_OR_EQUAL:
            is_pass = actual_value >= p.threshold
        elif p.operator == Operator.LESS_THAN_OR_EQUAL:
            is_pass = actual_value <= p.threshold

        status = EvaluationStatus.PASS if is_pass else EvaluationStatus.FAIL
        if is_pass:
            passed_count += 1

        evaluations.append(PrincipleEvaluation(
            principle_name=p.name,
            required_threshold=p.threshold,
            actual_value=actual_value,
            status=status,
            explanation=None
        ))

    # Strict compliance: Calculate count, add absolute disclaimer
    summary_text = (
        f"{passed_count} out of {total_count} principles passed. "
        "Disclaimer: This score represents only the evaluation of user-configured rules against available data. "
        "It is strictly not a buy signal, a sell signal, or a guaranteed investment recommendation."
    )

    return PrincipleEvaluationReport(
        evaluations=evaluations,
        passed_count=passed_count,
        total_count=total_count,
        summary_text=summary_text
    )

