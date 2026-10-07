import React, { useState, useEffect } from 'react';
import { Search, Loader2, AlertCircle, Settings, Check, GitCompare, Database, Calculator, CheckCircle } from 'lucide-react';
import { analyzeCompany, fetchPrinciples, updatePrinciple, compareCompanies } from '../services/api';
import CompanyOverview from '../components/CompanyOverview';
import MetricGrid from '../components/MetricGrid';
import HistoricalCharts from '../components/HistoricalCharts';
import PrincipleEvaluations from '../components/PrincipleEvaluations';
import AISection from '../components/AISection';
import AskFinolitics from '../components/AskFinolitics';
import ComparisonView from '../components/ComparisonView';

export default function Dashboard({ externalMode, setExternalMode }) {
    const [mode, setMode] = useState('single');
    const [ticker, setTicker] = useState('');
    const [data, setData] = useState(null);
    const [ticker1, setTicker1] = useState('');
    const [ticker2, setTicker2] = useState('');
    const [compareData, setCompareData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [principles, setPrinciples] = useState([]);
    const [showConfig, setShowConfig] = useState(false);
    const [saveStatus, setSaveStatus] = useState({});

    useEffect(() => {
        fetchPrinciples().then(setPrinciples).catch(console.error);
    }, []);

    useEffect(() => {
        if (externalMode === 'single') {
            setMode('single');
            setShowConfig(false);
        } else if (externalMode === 'compare') {
            setMode('compare');
            setShowConfig(false);
        } else if (externalMode === 'config') {
            setShowConfig(true);
        } else if (externalMode === 'overview') {
            setData(null);
            setCompareData(null);
            setShowConfig(false);
        }
    }, [externalMode]);

    const handleAnalyze = async (e) => {
        if (e) e.preventDefault();
        if (mode === 'single' && !ticker.trim()) return;
        if (mode === 'compare' && (!ticker1.trim() || !ticker2.trim())) return;
        
        setLoading(true);
        setError(null);
        setData(null);
        setCompareData(null);
        setShowConfig(false);
        
        try {
            if (mode === 'single') {
                const result = await analyzeCompany(ticker);
                setData(result);
            } else {
                const result = await compareCompanies([ticker1, ticker2]);
                setCompareData(result);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleThresholdChange = async (identifier, newThreshold) => {
        try {
            await updatePrinciple(identifier, newThreshold);
            setSaveStatus({ ...saveStatus, [identifier]: 'saved' });
            setTimeout(() => setSaveStatus({ ...saveStatus, [identifier]: null }), 2000);
            
            const updated = await fetchPrinciples();
            setPrinciples(updated);
            
            if (mode === 'single' && data) {
                setLoading(true);
                const result = await analyzeCompany(data.company_data.profile.ticker);
                setData(result);
                setLoading(false);
            } else if (mode === 'compare' && compareData) {
                setLoading(true);
                const result = await compareCompanies([ticker1, ticker2]);
                setCompareData(result);
                setLoading(false);
            }
        } catch (err) {
            console.error('Failed to update threshold', err);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {!data && !compareData && !loading && !error && !showConfig && (
                <div className="text-center py-20 px-4 mt-8">
                    <h1 className="text-5xl md:text-6xl font-extrabold text-[#C3D2FB] mb-6 tracking-tight max-w-4xl mx-auto leading-tight">
                        Turn financial data into<br/>understandable investment<br/>research.
                    </h1>
                    <p className="text-[#8B9CC3] text-lg max-w-3xl mx-auto mb-10">
                        Evaluate real statements from Yfinance against institutional principles with<br/>complete calculation transparency and zero hallucination.
                    </p>

                    <form onSubmit={handleAnalyze} className="max-w-2xl mx-auto mb-8">
                        <div className="relative flex items-center bg-[#131B2F] border border-[#2A344A] rounded-xl overflow-hidden shadow-lg p-1">
                            <div className="pl-4 text-slate-400">
                                <Search className="h-5 w-5" />
                            </div>
                            <input
                                type="text"
                                value={ticker}
                                onChange={(e) => setTicker(e.target.value)}
                                placeholder="NVDA"
                                className="w-full bg-transparent border-none text-white px-4 py-3 focus:outline-none focus:ring-0 placeholder-slate-500"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={loading || !ticker.trim()}
                                className="bg-[#1C2C4F] hover:bg-[#253966] text-blue-300 font-medium px-6 py-2.5 rounded-lg flex items-center gap-2 transition-colors whitespace-nowrap"
                            >
                                Analyze Company →
                            </button>
                        </div>
                    </form>

                    <div className="flex items-center justify-center gap-3 text-sm">
                        <span className="text-[#64748B]">Popular:</span>
                        <div className="flex flex-wrap justify-center gap-2">
                            {['AAPL', 'MSFT', 'NVDA', 'TCS.NS', 'RELIANCE.NS', 'INFY.NS'].map(t => (
                                <button 
                                    key={t} 
                                    onClick={() => { setTicker(t); }} 
                                    className="bg-[#111827]/80 border border-[#1F2937] hover:bg-[#1F2937] text-slate-300 px-4 py-1.5 rounded-md transition-colors text-xs font-medium"
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {(data || compareData || showConfig) && (
                <div className="mb-6 bg-[#131B2F] p-5 rounded-xl shadow-sm border border-slate-800">
                    <div className="flex flex-col sm:flex-row gap-4 mb-5">
                        <div className="flex gap-2">
                            <button 
                                onClick={() => { setMode('single'); if (setExternalMode) setExternalMode('single'); }} 
                                className={`px-5 py-2 text-sm font-semibold rounded-lg transition-colors ${mode === 'single' ? 'bg-blue-600 text-white shadow' : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800'}`}
                            >
                                Single Analysis
                            </button>
                            <button 
                                onClick={() => { setMode('compare'); if (setExternalMode) setExternalMode('compare'); }} 
                                className={`px-5 py-2 text-sm font-semibold rounded-lg transition-colors flex items-center ${mode === 'compare' ? 'bg-blue-600 text-white shadow' : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800'}`}
                            >
                                <GitCompare className="h-4 w-4 mr-2" />
                                Compare Companies
                            </button>
                        </div>
                        <div className="flex-1"></div>
                        <button 
                            onClick={() => { setShowConfig(!showConfig); if (setExternalMode) setExternalMode(!showConfig ? 'config' : mode); }}
                            className={`inline-flex items-center px-5 py-2 border text-sm font-semibold rounded-lg transition-all ${showConfig ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-[#1A233A] text-slate-300 border-slate-700 hover:bg-slate-800'}`}
                        >
                            <Settings className="h-4 w-4 mr-2" />
                            Configure Criteria
                        </button>
                    </div>

                    <form onSubmit={handleAnalyze} className="flex flex-col sm:flex-row gap-4">
                        {mode === 'single' ? (
                            <div className="relative flex-1">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <Search className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="text"
                                    value={ticker}
                                    onChange={(e) => setTicker(e.target.value)}
                                    placeholder="Enter Company Ticker (e.g. AAPL, TCS.NS)"
                                    className="block w-full pl-11 pr-4 py-3 bg-[#0A0F1C] border border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-white shadow-inner outline-none transition-shadow"
                                    disabled={loading}
                                />
                            </div>
                        ) : (
                            <div className="flex flex-1 gap-4">
                                <input
                                    type="text"
                                    value={ticker1}
                                    onChange={(e) => setTicker1(e.target.value)}
                                    placeholder="Company 1 (e.g. TCS.NS)"
                                    className="block w-1/2 px-4 py-3 bg-[#0A0F1C] border border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-white shadow-inner outline-none transition-shadow"
                                    disabled={loading}
                                />
                                <input
                                    type="text"
                                    value={ticker2}
                                    onChange={(e) => setTicker2(e.target.value)}
                                    placeholder="Company 2 (e.g. INFY.NS)"
                                    className="block w-1/2 px-4 py-3 bg-[#0A0F1C] border border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-white shadow-inner outline-none transition-shadow"
                                    disabled={loading}
                                />
                            </div>
                        )}
                        
                        <button
                            type="submit"
                            disabled={loading}
                            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-semibold rounded-lg shadow text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-all min-w-[140px]"
                        >
                            {loading ? <Loader2 className="animate-spin h-5 w-5 mr-2" /> : null}
                            {mode === 'single' ? 'Analyze' : 'Compare'}
                        </button>
                    </form>
                </div>
            )}

            {showConfig && (
                <div className="mb-8 bg-[#131B2F] p-6 rounded-xl shadow-inner border border-slate-800 animate-in slide-in-from-top-2">
                    <h3 className="text-lg font-bold text-white mb-2">Investment Principle Thresholds</h3>
                    <p className="text-sm text-slate-400 mb-6 max-w-3xl leading-relaxed">Adjusting these mathematical thresholds auto-saves to the database. The system will instantly recalculate the raw yfinance metrics and instruct the Gemini AI to regenerate the qualitative Investment Thesis based on your new strict criteria.</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {principles.map(p => (
                            <div key={p.identifier} className="bg-[#0A0F1C] p-4 rounded-lg shadow-sm border border-slate-800 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 transition-shadow">
                                <label className="block text-sm font-semibold text-slate-300 mb-2">{p.name}</label>
                                <div className="flex items-center gap-3">
                                    <span className="text-slate-400 font-mono text-sm bg-[#131B2F] px-2 py-1 rounded">{p.metric} {p.operator}</span>
                                    <input 
                                        type="number"
                                        step="0.01"
                                        defaultValue={p.threshold}
                                        onBlur={(e) => handleThresholdChange(p.identifier, e.target.value)}
                                        className="block w-full bg-transparent border-b border-slate-700 py-1 focus:border-blue-500 text-white outline-none sm:text-sm font-medium"
                                    />
                                    {saveStatus[p.identifier] === 'saved' && <Check className="h-5 w-5 text-emerald-500 animate-in zoom-in" />}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {loading && (
                <div className="max-w-3xl mx-auto mt-12 bg-[#131B2F] border border-slate-800/60 rounded-2xl p-12 text-center shadow-2xl animate-in fade-in">
                    <div className="relative w-20 h-20 mx-auto mb-6">
                        <div className="absolute inset-0 border-4 border-[#1C2C4F] rounded-full"></div>
                        <div className="absolute inset-0 border-4 border-t-[#3B82F6] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">Analyzing {ticker || 'Company'}...</h3>
                    <p className="text-[#8B9CC3] mb-10 max-w-lg mx-auto text-sm leading-relaxed">
                        Gathering official statements via Yfinance, computing derived metrics, and testing against configured principles.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4 text-xs font-medium">
                        <div className="flex items-center gap-2 bg-[#0A0F1C] border border-slate-800 text-slate-300 px-4 py-2.5 rounded-lg">
                           <Database className="w-4 h-4 text-[#3B82F6]"/> Yfinance Statements
                        </div>
                        <div className="flex items-center gap-2 bg-[#0A0F1C] border border-slate-800 text-slate-300 px-4 py-2.5 rounded-lg">
                           <Calculator className="w-4 h-4 text-[#10B981]"/> Metric Engine
                        </div>
                        <div className="flex items-center gap-2 bg-[#0A0F1C] border border-slate-800 text-slate-300 px-4 py-2.5 rounded-lg">
                           <CheckCircle className="w-4 h-4 text-[#A855F7]"/> Principle Rules
                        </div>
                    </div>
                </div>
            )}

            {error && (
                <div className="rounded-xl bg-red-900/20 p-5 mb-8 border border-red-900/50 flex shadow-sm animate-in fade-in">
                    <AlertCircle className="h-6 w-6 text-red-500 mr-4 flex-shrink-0" />
                    <div>
                        <h3 className="text-sm font-bold text-red-400">Analysis Error</h3>
                        <p className="mt-1 text-sm text-red-300/80 leading-relaxed">{error}</p>
                    </div>
                </div>
            )}

            {mode === 'single' && data && !loading && (
                <div className={`space-y-8 transition-all duration-300 animate-in fade-in`}>
                    <CompanyOverview profile={data.company_data?.profile} />
                    <MetricGrid metrics={data.metrics} />
                    <HistoricalCharts historicalData={data.metrics?.historical_data} priceData={data.company_data?.historical_prices} />
                    <PrincipleEvaluations evaluation={data.evaluation} />
                    <AISection aiReport={data.ai_report} />
                    <AskFinolitics context={data} />
                </div>
            )}

            {mode === 'compare' && compareData && !loading && (
                <div className={`transition-all duration-300 animate-in fade-in`}>
                    <ComparisonView data={compareData} />
                </div>
            )}
        </div>
    );
}
