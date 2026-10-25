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
        model = genai.GenerativeModel('gemini-3.5-flash', generation_config={"response_mime_type": "application/json"})
        
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
        model = genai.GenerativeModel('gemini-3.5-flash')
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
        return model.generate_content(prompt).text
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        return "Failed to generate an answer due to an AI service error."

def generate_comparison_report(context1: dict, context2: dict) -> Union[Dict[str, Any], str]:
    """Generates an institutional AI comparison report highlighting differences in metrics."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "AI service is not configured. Please add GEMINI_API_KEY to your environment."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-3.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
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
        response = model.generate_content(prompt)
        try:
            parsed = json.loads(response.text)
            parsed["disclaimer"] = DISCLAIMER
            return parsed
        except Exception:
            return response.text
    except Exception as e:
        logger.error(f"Failed to generate comparison: {e}")
        return "Failed to generate comparison due to an AI service error."
