import React from 'react';
import { formatPercentage, formatNumber, formatCurrency } from '../utils/formatters';

export default function ComparisonView({ data }) {
    if (!data || !data.companies || data.companies.length < 2) return null;
    const [c1, c2] = data.companies;

    const metricsList = [
        { label: 'Revenue Growth', key: 'revenue_growth', format: formatPercentage },
        { label: 'ROE', key: 'roe', format: formatPercentage },
        { label: 'ROCE', key: 'roce', format: formatPercentage },
        { label: 'Debt to Equity', key: 'debt_to_equity', format: formatNumber },
        { label: 'Operating Margin', key: 'operating_margin', format: formatPercentage },
        { label: 'P/E Ratio', key: 'pe_ratio', format: formatNumber },
        { label: 'Free Cash Flow', key: 'free_cash_flow', format: formatCurrency }
    ];

    return (
        <div className="space-y-6 animate-in fade-in">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 overflow-x-auto">
                <h3 className="text-xl font-bold text-slate-800 mb-6">Head-to-Head Quantitative Comparison</h3>
                <table className="w-full text-sm text-left border-collapse">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                        <tr>
                            <th className="px-4 py-3">Metric</th>
                            <th className="px-4 py-3 text-blue-700">{c1.ticker}</th>
                            <th className="px-4 py-3 text-emerald-700">{c2.ticker}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {metricsList.map((m, i) => (
                            <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                                <td className="px-4 py-3 font-medium text-slate-700">{m.label}</td>
                                <td className="px-4 py-3 font-semibold text-slate-900">{m.format(c1.metrics[m.key])}</td>
                                <td className="px-4 py-3 font-semibold text-slate-900">{m.format(c2.metrics[m.key])}</td>
                            </tr>
                        ))}
                        <tr className="bg-slate-50 border-t-2 border-slate-200">
                            <td className="px-4 py-4 font-bold text-slate-800">Principles Passed</td>
                            <td className="px-4 py-4 font-bold text-blue-700 text-lg">{c1.evaluations.passed_count} / {c1.evaluations.total_count}</td>
                            <td className="px-4 py-4 font-bold text-emerald-700 text-lg">{c2.evaluations.passed_count} / {c2.evaluations.total_count}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div className="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                <h3 className="text-lg font-bold text-blue-900 mb-3">AI Comparison Analysis</h3>
                <p className="text-blue-800 whitespace-pre-wrap leading-relaxed">
                    {data.ai_comparison || "AI Comparison unavailable. API key may be unconfigured."}
                </p>
            </div>
        </div>
    );
}

