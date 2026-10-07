import React from 'react';

export default function AISection({ aiReport }) {
    if (!aiReport) {
        return (
            <div className="mt-8 bg-slate-50 border border-dashed border-slate-300 rounded p-6 text-center">
                <p className="text-sm text-slate-500 font-medium">AI Research Report is unavailable. The API key may not be configured, or a network timeout occurred.</p>
            </div>
        );
    }

    const { visual_summary } = aiReport;

    return (
        <div className="mt-8 space-y-6">
            
            {/* Visual Thesis Summary */}
            <div className="bg-slate-900 text-white rounded-lg shadow-lg overflow-hidden">
                <div className="p-4 border-b border-slate-700 bg-slate-800">
                    <h3 className="text-lg font-bold">Visual Thesis Summary</h3>
                </div>
                <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">Financial Quality</p>
                        <p className="text-xl font-bold mt-1 text-blue-400">{visual_summary.financial_quality}</p>
                    </div>
                    <div>
                        <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">Valuation</p>
                        <p className="text-xl font-bold mt-1 text-emerald-400">{visual_summary.valuation}</p>
                    </div>
                    <div>
                        <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">Data Completeness</p>
                        <p className="text-xl font-bold mt-1 text-amber-400">{visual_summary.data_completeness}</p>
                    </div>
                </div>
                <div className="p-6 border-t border-slate-700 grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-800/50">
                    <div>
                        <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-2">Key Strengths</p>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-slate-200">
                            {visual_summary.key_strengths.map((str, i) => <li key={i}>{str}</li>)}
                        </ul>
                    </div>
                    <div>
                        <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-2">Key Concerns</p>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-slate-200">
                            {visual_summary.key_concerns.map((con, i) => <li key={i}>{con}</li>)}
                        </ul>
                    </div>
                </div>
            </div>

            {/* Explainable Investment Thesis */}
            <div className="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                <h3 className="text-xl font-bold text-blue-900 mb-2">Explainable Investment Thesis</h3>
                <p className="text-blue-800 leading-relaxed whitespace-pre-wrap">{aiReport.investment_thesis}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-emerald-800 mb-2">What Strengthens the Thesis?</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.strengthens_thesis}</p>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-red-800 mb-2">What Weakens the Thesis?</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.weakens_thesis}</p>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-800 mb-2">Valuation Concerns</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.valuation_concerns}</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-800 mb-2">Important Financial Risk</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.important_financial_risk}</p>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-800 mb-2">General Concerns</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.concerns}</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-amber-800 mb-2">Data Limitations</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.data_limitations}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-50 p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-800 mb-3">What the Investor Should Investigate Next</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.investigate_next}</p>
                </div>

                <div className="bg-slate-50 p-6 rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-800 mb-2">What Could Invalidate the Current Thesis?</h3>
                    <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{aiReport.invalidate_thesis}</p>
                </div>
            </div>

            <div className="mt-4 p-4 bg-slate-100 rounded text-center border border-slate-200">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{aiReport.disclaimer}</p>
            </div>
        </div>
    );
}
