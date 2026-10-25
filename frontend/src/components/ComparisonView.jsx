import React from 'react';
import { GitCompare, Sparkles, CheckCircle2 } from 'lucide-react';
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
            <div className="bg-[#131B2F] p-6 rounded-xl shadow-lg border border-slate-800 overflow-x-auto">
                <div className="flex items-center gap-2 mb-6">
                    <GitCompare className="w-5 h-5 text-blue-400" />
                    <h3 className="text-xl font-bold text-white">Head-to-Head Quantitative Comparison</h3>
                </div>
                <table className="w-full text-sm text-left border-collapse">
                    <thead className="text-xs uppercase bg-[#0A0F1C] border-b border-slate-800 text-slate-400">
                        <tr>
                            <th className="px-5 py-3.5 font-semibold">Financial Metric</th>
                            <th className="px-5 py-3.5 font-bold text-blue-400 text-base">{c1.ticker}</th>
                            <th className="px-5 py-3.5 font-bold text-emerald-400 text-base">{c2.ticker}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                        {metricsList.map((m, i) => (
                            <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                                <td className="px-5 py-3.5 font-medium text-slate-300">{m.label}</td>
                                <td className="px-5 py-3.5 font-semibold text-white">{m.format(c1.metrics[m.key])}</td>
                                <td className="px-5 py-3.5 font-semibold text-white">{m.format(c2.metrics[m.key])}</td>
                            </tr>
                        ))}
                        <tr className="bg-[#0A0F1C]/60 border-t-2 border-slate-700">
                            <td className="px-5 py-4 font-bold text-white flex items-center gap-2">
                                <CheckCircle2 className="w-4 h-4 text-purple-400" />
                                Principles Passed
                            </td>
                            <td className="px-5 py-4 font-bold text-blue-400 text-lg">{c1.evaluations.passed_count} / {c1.evaluations.total_count}</td>
                            <td className="px-5 py-4 font-bold text-emerald-400 text-lg">{c2.evaluations.passed_count} / {c2.evaluations.total_count}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div className="bg-[#131B2F] p-6 rounded-xl shadow-lg border border-blue-900/40">
                <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-bold text-white">AI Comparative Research Analysis</h3>
                </div>
                <p className="text-slate-300 whitespace-pre-wrap leading-relaxed text-sm">
                    {data.ai_comparison || "AI Comparison unavailable. API key may be unconfigured."}
                </p>
            </div>
        </div>
    );
}
