import os
import json
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)

DISCLAIMER = "This analysis is for research and educational purposes only and is not financial advice."

def generate_research_report(company_data: Any, metrics_dict: Dict, evaluation_report: Dict) -> Optional[Dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("Gemini API key is not configured. Skipping AI report generation.")
        return None
        
    try:
        genai.configure(api_key=api_key)
        
        profile_str = json.dumps(company_data.profile.model_dump(), default=str)
        metrics_str = json.dumps(metrics_dict, default=str)
        eval_str = json.dumps(evaluation_report, default=str)
        
        prompt = f"""
        You are an expert, purely analytical investment research assistant. Generate an Explainable Investment Thesis strictly based on the verifiable financial data provided below.
        
        CRITICAL RULES:
        1. NO HALLUCINATIONS: Do NOT invent, estimate, or hallucinate financial numbers, metrics, probabilities, or facts.
        2. EXPLICIT EVIDENCE: Use ONLY the financial values and principle results supplied below.
        3. FACT SEPARATION: Distinguish clearly between raw facts, calculated metrics, and your AI interpretation.
        4. JUSTIFY WITH RULES: Explain the relationship between the user's criteria and the evidence. If a principle passed/failed, explicitly state the metric and threshold (e.g. "ROE of 18% passed the user's threshold of 15%").
        5. DATA LIMITATIONS: If a metric is missing/null, explicitly identify the limitation (e.g., "Data Limitation: P/E Ratio is unavailable"). Do NOT guess missing numbers.
        6. NO RECOMMENDATIONS: Do NOT generate buy, sell, or hold recommendations. Do NOT state the principles are guaranteed investment recommendations.
        7. QUALITATIVE LABELS: Use labels (e.g. 'Strong', 'Weak') ONLY when justified directly by the underlying principle results and data completeness.
        
        DATA CONTEXT:
        Company Profile: {profile_str}
        Calculated Metrics: {metrics_str}
        Investment Principles Evaluation: {eval_str}
        
        REQUIRED JSON STRUCTURE:
        {{
            "visual_summary": {{
                "financial_quality": "string",
                "valuation": "string",
                "key_strengths": ["string"],
                "key_concerns": ["string"],
                "data_completeness": "string"
            }},
            "investment_thesis": "string",
            "strengthens_thesis": "string",
            "weakens_thesis": "string",
            "important_financial_risk": "string",
            "valuation_concerns": "string",
            "concerns": "string",
            "data_limitations": "string",
            "investigate_next": "string",
            "invalidate_thesis": "string",
            "disclaimer": "{DISCLAIMER}"
        }}
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
        except Exception:
            model = genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)

        result = json.loads(response.text)
        result['disclaimer'] = DISCLAIMER
        return result
        
    except Exception as e:
        logger.error(f"AI Generation failed gracefully: {str(e)}", exc_info=True)
        return None

def answer_financial_question(context: dict, question: str) -> str:
    """Answers a user question strictly bounded by the provided context."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "AI service is not configured. Please add GEMINI_API_KEY to your environment."
    try:
        genai.configure(api_key=api_key)
        prompt = f"""
        You are 'Finolitics', an AI financial assistant. Answer the user's question using ONLY the provided financial context.
        
        CONTEXT: {json.dumps(context, default=str)}
        
        RULES:
        1. Do NOT invent financial facts, metrics, or company history.
        2. If the answer cannot be determined from the available data, clearly state: "The information required to answer this is unavailable in the current data."
        3. Do not generate buy, sell, or hold recommendations.
        4. Focus heavily on why principles failed or succeeded based on the threshold criteria.
        
        QUESTION: {question}
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        except Exception:
            model = genai.GenerativeModel('gemini-2.0-flash')
            return model.generate_content(prompt).text
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}", exc_info=True)
        return f"Failed to generate answer: {str(e)}"

def build_algorithmic_comparison(context1: dict, context2: dict) -> dict:
    """Builds a deterministic institutional quantitative comparison tear-sheet from verified statement data."""
    t1 = context1.get("profile", {}).get("ticker", "Company 1")
    t2 = context2.get("profile", {}).get("ticker", "Company 2")
    m1 = context1.get("metrics", {})
    m2 = context2.get("metrics", {})
    ev1 = context1.get("evaluations", {})
    ev2 = context2.get("evaluations", {})

    def fmt_pct(v):
        return f"{v * 100:.1f}%" if v is not None else "N/A"
    def fmt_num(v):
        return f"{v:.2f}" if v is not None else "N/A"
    def fmt_cur(v):
        if v is None: return "N/A"
        if abs(v) >= 1e9: return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6: return f"${v/1e6:.2f}M"
        return f"${v:,.0f}"

    rev1, rev2 = m1.get("revenue_growth"), m2.get("revenue_growth")
    roe1, roe2 = m1.get("roe"), m2.get("roe")
    roce1, roce2 = m1.get("roce"), m2.get("roce")
    op1, op2 = m1.get("operating_margin"), m2.get("operating_margin")
    de1, de2 = m1.get("debt_to_equity"), m2.get("debt_to_equity")
    fcf1, fcf2 = m1.get("free_cash_flow"), m2.get("free_cash_flow")
    pe1, pe2 = m1.get("pe_ratio"), m2.get("pe_ratio")

    growth_leader = "Tied"
    if rev1 is not None and rev2 is not None:
        growth_leader = t1 if rev1 > rev2 else (t2 if rev2 > rev1 else "Tied")

    roe_avg1 = ((roe1 or 0) + (roce1 or 0)) / 2
    roe_avg2 = ((roe2 or 0) + (roce2 or 0)) / 2
    moat_leader = t1 if roe_avg1 > roe_avg2 else (t2 if roe_avg2 > roe_avg1 else "Tied")

    solvency_leader = "Tied"
    if de1 is not None and de2 is not None:
        solvency_leader = t1 if de1 < de2 else (t2 if de2 < de1 else "Tied")

    cash_leader = "Tied"
    if op1 is not None and op2 is not None:
        cash_leader = t1 if op1 > op2 else (t2 if op2 > op1 else "Tied")

    c1_edges, c2_edges = [], []
    if rev1 is not None and rev2 is not None:
        if rev1 > rev2: c1_edges.append(f"Higher revenue expansion rate ({fmt_pct(rev1)} vs {fmt_pct(rev2)}).")
        elif rev2 > rev1: c2_edges.append(f"Faster top-line revenue momentum ({fmt_pct(rev2)} vs {fmt_pct(rev1)}).")
    if roe1 is not None and roe2 is not None:
        if roe1 > roe2: c1_edges.append(f"Superior return on shareholder equity ({fmt_pct(roe1)} vs {fmt_pct(roe2)}).")
        elif roe2 > roe1: c2_edges.append(f"Stronger return on equity efficiency ({fmt_pct(roe2)} vs {fmt_pct(roe1)}).")
    if op1 is not None and op2 is not None:
        if op1 > op2: c1_edges.append(f"Higher operating margin buffer ({fmt_pct(op1)} vs {fmt_pct(op2)}).")
        elif op2 > op1: c2_edges.append(f"More profitable operating margin ({fmt_pct(op2)} vs {fmt_pct(op1)}).")
    if de1 is not None and de2 is not None:
        if de1 < de2: c1_edges.append(f"More conservative leverage with lower Debt-to-Equity ({fmt_num(de1)} vs {fmt_num(de2)}).")
        elif de2 < de1: c2_edges.append(f"Cleaner balance sheet leverage ({fmt_num(de2)} vs {fmt_num(de1)}).")
    if fcf1 is not None and fcf2 is not None:
        if fcf1 > fcf2: c1_edges.append(f"Higher annual free cash flow generation ({fmt_cur(fcf1)} vs {fmt_cur(fcf2)}).")
        elif fcf2 > fcf1: c2_edges.append(f"Substantially higher free cash generation ({fmt_cur(fcf2)} vs {fmt_cur(fcf1)}).")

    if not c1_edges: c1_edges.append(f"Passed {ev1.get('passed_count', 0)} of {ev1.get('total_count', 0)} investment principle thresholds.")
    if not c2_edges: c2_edges.append(f"Passed {ev2.get('passed_count', 0)} of {ev2.get('total_count', 0)} investment principle thresholds.")

    c1_risks, c2_risks = [], []
    if rev1 is not None and rev1 < 0.05: c1_risks.append(f"Subdued revenue growth at {fmt_pct(rev1)}.")
    if rev2 is not None and rev2 < 0.05: c2_risks.append(f"Subdued revenue growth at {fmt_pct(rev2)}.")
    if de1 is not None and de1 > 0.5: c1_risks.append(f"Elevated debt-to-equity ratio of {fmt_num(de1)}.")
    if de2 is not None and de2 > 0.5: c2_risks.append(f"Elevated debt-to-equity ratio of {fmt_num(de2)}.")
    if pe1 is not None and pe1 > 35: c1_risks.append(f"Premium earnings multiple (P/E {fmt_num(pe1)}).")
    if pe2 is not None and pe2 > 35: c2_risks.append(f"Premium earnings multiple (P/E {fmt_num(pe2)}).")
    if not c1_risks: c1_risks.append(f"Failed {ev1.get('total_count', 0) - ev1.get('passed_count', 0)} institutional criteria.")
    if not c2_risks: c2_risks.append(f"Failed {ev2.get('total_count', 0) - ev2.get('passed_count', 0)} institutional criteria.")

    p1_pass = ev1.get('passed_count', 0)
    p2_pass = ev2.get('passed_count', 0)
    if p1_pass > p2_pass:
        verdict = f"{t1} demonstrates stronger overall institutional alignment passing {p1_pass} criteria compared to {t2}'s {p2_pass}. While {t2} offers specific metric strengths, {t1} maintains a more balanced quantitative profile across return on capital and balance sheet safety."
    elif p2_pass > p1_pass:
        verdict = f"{t2} outperforms on institutional principle adherence passing {p2_pass} criteria versus {t1}'s {p1_pass}. {t2} exhibits key structural advantages, though investors must evaluate trade-offs in valuation multiples and capital allocation."
    else:
        verdict = f"{t1} and {t2} present a closely contested institutional duel, each meeting {p1_pass} principle thresholds. The decision centers on prioritizing {t1}'s specific capital structure against {t2}'s growth and profitability dynamics."

    return {
        "executive_verdict": verdict,
        "category_battles": [
            {
                "category": "Growth & Scale",
                "leader": growth_leader,
                "analysis": f"{t1} posted revenue growth of {fmt_pct(rev1)}, compared to {t2} at {fmt_pct(rev2)}."
            },
            {
                "category": "Capital Efficiency & Moat",
                "leader": moat_leader,
                "analysis": f"{t1} generated an ROE of {fmt_pct(roe1)} and ROCE of {fmt_pct(roce1)}, against {t2}'s ROE of {fmt_pct(roe2)} and ROCE of {fmt_pct(roce2)}."
            },
            {
                "category": "Financial Resilience & Solvency",
                "leader": solvency_leader,
                "analysis": f"{t1} operates with a Debt-to-Equity ratio of {fmt_num(de1)}, while {t2} maintains {fmt_num(de2)}."
            },
            {
                "category": "Operating Margins & Cash Flow",
                "leader": cash_leader,
                "analysis": f"{t1} delivered an operating margin of {fmt_pct(op1)} with Free Cash Flow of {fmt_cur(fcf1)}, versus {t2} at {fmt_pct(op2)} and {fmt_cur(fcf2)}."
            }
        ],
        "company_edges": {
            "c1_edges": c1_edges,
            "c2_edges": c2_edges
        },
        "vulnerabilities": {
            "c1_risks": c1_risks,
            "c2_risks": c2_risks
        },
        "investor_scenarios": {
            "bull_case_c1": f"Investors prioritizing {t1}'s relative profile in {growth_leader if growth_leader == t1 else moat_leader} and principle execution.",
            "bull_case_c2": f"Investors seeking {t2}'s comparative positioning in {growth_leader if growth_leader == t2 else moat_leader} and operational discipline."
        },
        "disclaimer": DISCLAIMER
    }

def generate_comparison_report(context1: dict, context2: dict) -> Union[Dict[str, Any], str]:
    """Generates an institutional AI comparison report highlighting differences in metrics."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return build_algorithmic_comparison(context1, context2)

    try:
        genai.configure(api_key=api_key)
        t1 = context1.get("profile", {}).get("ticker", "Company 1")
        t2 = context2.get("profile", {}).get("ticker", "Company 2")
        
        prompt = f"""
        You are a senior equity research analyst at an institutional quantitative fund.
        Perform an institutional-grade, highly engaging comparative research analysis between {t1} and {t2} based STRICTLY on the verifiable financial data and principle evaluations provided below.

        CRITICAL RULES:
        1. NO HALLUCINATIONS: Use ONLY the numbers and metrics supplied. Do NOT invent or estimate unverified financial facts.
        2. SPECIFIC NUMERICAL EVIDENCE: Whenever discussing a metric (e.g. ROE, ROCE, Margin, Debt/Equity, Revenue Growth, Free Cash Flow), quote the exact numerical value and how it compares to the peer.
        3. OBJECTIVE & UNBIASED: Do NOT produce a definitive buy, sell, or hold recommendation. Analyze the trade-offs rigorously.
        4. PRINCIPLE THRESHOLDS: Explicitly reference how each company performed against the institutional principles.

        DATA CONTEXT:
        {t1} DATA: {json.dumps(context1, default=str)}
        {t2} DATA: {json.dumps(context2, default=str)}

        REQUIRED JSON OUTPUT FORMAT:
        {{
            "executive_verdict": "Comprehensive 2-3 sentence executive synthesis comparing overall financial quality, competitive positioning, and core trade-offs between {t1} and {t2}.",
            "category_battles": [
                {{
                    "category": "Growth & Scale",
                    "leader": "{t1}" or "{t2}" or "Tied",
                    "analysis": "Specific comparison of revenue growth and scale with exact numbers."
                }},
                {{
                    "category": "Capital Efficiency & Moat",
                    "leader": "{t1}" or "{t2}" or "Tied",
                    "analysis": "Specific comparison of ROE, ROCE, and moat durability with exact numbers."
                }},
                {{
                    "category": "Financial Resilience & Solvency",
                    "leader": "{t1}" or "{t2}" or "Tied",
                    "analysis": "Specific comparison of Debt to Equity, leverage, and balance sheet safety."
                }},
                {{
                    "category": "Operating Margins & Cash Flow",
                    "leader": "{t1}" or "{t2}" or "Tied",
                    "analysis": "Specific comparison of operating margin and Free Cash Flow generation."
                }}
            ],
            "company_edges": {{
                "c1_edges": [
                    "Key quantifiable advantage 1 for {t1} with metric numbers",
                    "Key quantifiable advantage 2 for {t1} with metric numbers"
                ],
                "c2_edges": [
                    "Key quantifiable advantage 1 for {t2} with metric numbers",
                    "Key quantifiable advantage 2 for {t2} with metric numbers"
                ]
            }},
            "vulnerabilities": {{
                "c1_risks": [
                    "Primary financial risk or weak metric for {t1}",
                    "Secondary concern or failed principle for {t1}"
                ],
                "c2_risks": [
                    "Primary financial risk or weak metric for {t2}",
                    "Secondary concern or failed principle for {t2}"
                ]
            }},
            "investor_scenarios": {{
                "bull_case_c1": "When an institutional investor would favor {t1} (e.g. higher stability, lower debt, or specific moat).",
                "bull_case_c2": "When an institutional investor would favor {t2} (e.g. faster growth, higher capital returns, or value discount)."
            }},
            "disclaimer": "{DISCLAIMER}"
        }}
        """

        model_names = ['gemini-3.5-flash', 'gemini-flash-latest', 'gemini-1.5-flash']
        response = None
        for m_name in model_names:
            try:
                model = genai.GenerativeModel(
                    m_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    parsed = json.loads(response.text)
                    parsed["disclaimer"] = DISCLAIMER
                    return parsed
            except Exception as model_err:
                logger.warning(f"Model {m_name} failed: {model_err}")
                continue

        # If LLM failed or was rate limited, fall back to institutional algorithmic comparison
        return build_algorithmic_comparison(context1, context2)

    except Exception as e:
        logger.error(f"Failed to generate comparison: {e}", exc_info=True)
        return build_algorithmic_comparison(context1, context2)
