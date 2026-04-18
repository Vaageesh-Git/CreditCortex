import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
  UploadCloud, ShieldAlert, CheckCircle, Clock, FileText,
  Activity, AlertTriangle, TrendingUp, TrendingDown, Info, Loader2, Flag, Wallet, Building
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine, CartesianGrid
} from 'recharts';
import './index.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setResults(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await axios.post(
        'http://localhost:8000/evaluate-loan',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error processing application.");
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusUI = (status) => {
    switch (status) {
      case 'APPROVED':
        return { color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', icon: <CheckCircle size={28} /> };
      case 'REJECTED':
        return { color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200', icon: <ShieldAlert size={28} /> };
      case 'PAUSED':
      case 'PENDING_REVIEW':
        return { color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', icon: <Clock size={28} /> };
      default:
        return { color: 'text-slate-700', bg: 'bg-slate-50', border: 'border-slate-200', icon: <Info size={28} /> };
    }
  };

  const getShapChartData = () => {
    if (!results?.metrics?.shap_signals) return [];
    return Object.entries(results.metrics.shap_signals)
      .map(([key, value]) => ({
        factor: key,
        impact: parseFloat(value),
        isRisk: parseFloat(value) > 0
      }))
      .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));
  };

  // Extract meaningful metrics (ignoring imputed zeros) for the UI Snapshot
  const getMeaningfulMetrics = () => {
    if (!results?.borrower_data) return [];
    return Object.entries(results.borrower_data)
      .filter(([_, val]) => val !== 0 && val !== null && val !== "")
      .slice(0, 8); // Take top 8 extracted values
  };

  const chartData = getShapChartData();
  const criticalRisks = chartData.filter(d => d.impact > 0.3);
  const activeMetrics = getMeaningfulMetrics();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-blue-100">

      {/* NAVBAR */}
      <header className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Activity className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">Credit<span className="text-blue-600">Cortex</span></h1>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Underwriting Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <span className="text-sm font-medium text-slate-600">System Online</span>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto p-6 lg:p-8 space-y-6">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">

          {/* LEFT SIDEBAR: INGESTION & ALERTS */}
          <div className="xl:col-span-4 space-y-6">

            {/* UPLOAD WIDGET */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-600"></div>
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                <UploadCloud className="text-blue-600" size={20}/>
                Document Ingestion
              </h2>

              <input type="file" accept=".pdf" onChange={handleFileChange} className="hidden" id="file-upload" />
              <label
                htmlFor="file-upload"
                className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-xl p-8 cursor-pointer hover:bg-slate-50 transition-colors group"
              >
                <div className="bg-blue-50 p-4 rounded-full mb-3 group-hover:scale-105 transition-transform">
                  <UploadCloud size={32} className="text-blue-600" />
                </div>
                <p className="text-sm font-bold text-slate-700 truncate w-full text-center px-4">
                  {selectedFile ? selectedFile.name : "Select Borrower PDF"}
                </p>
                <p className="text-xs text-slate-400 mt-2 font-medium">Auto-extracts tables & unstructured text</p>
              </label>

              <button
                onClick={handleUpload}
                disabled={!selectedFile || isProcessing}
                className="w-full mt-5 py-3.5 rounded-xl bg-slate-900 text-white font-bold hover:bg-blue-600 disabled:bg-slate-200 disabled:text-slate-400 transition-colors flex justify-center items-center gap-2 shadow-sm"
              >
                {isProcessing ? (
                  <><Loader2 className="animate-spin" size={18} /> Executing AI Pipeline...</>
                ) : (
                  "Run CreditCortex Matrix"
                )}
              </button>

              {error && (
                <div className="mt-4 p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm flex items-start gap-2">
                  <ShieldAlert className="shrink-0 mt-0.5" size={16} />
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* CRITICAL FLAGS */}
            {criticalRisks.length > 0 && (
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-rose-100 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-rose-500"></div>
                <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2 uppercase tracking-wide text-sm">
                  <Flag className="text-rose-500" size={18} /> High-Risk Factors
                </h3>
                <div className="space-y-3">
                  {criticalRisks.map((r, i) => (
                    <div key={i} className="flex justify-between items-center p-3 bg-rose-50 rounded-lg border border-rose-100">
                      <span className="text-sm font-medium text-rose-900 truncate pr-2">{r.factor}</span>
                      <span className="text-xs font-bold text-rose-700 bg-rose-200 px-2.5 py-1 rounded-md">
                        +{r.impact.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* RIGHT MAIN DASHBOARD */}
          <div className="xl:col-span-8 space-y-6">

            {!results && !isProcessing && (
              <div className="h-full min-h-[600px] flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl bg-white/50">
                <Building size={64} className="mb-4 text-slate-200" />
                <h3 className="text-xl font-bold text-slate-400">Awaiting Data</h3>
                <p className="mt-2 text-sm font-medium">Upload a profile to synthesize the appraisal matrix.</p>
              </div>
            )}

            {results && (
              <>
                {/* HERO ROW: DECISION & SCORE */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* HITL Routing Decision */}
                  <div className={`md:col-span-2 p-6 rounded-2xl border flex flex-col justify-center shadow-sm ${getStatusUI(results.routing.status).bg} ${getStatusUI(results.routing.status).border}`}>
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-full bg-white shadow-sm ${getStatusUI(results.routing.status).color}`}>
                        {getStatusUI(results.routing.status).icon}
                      </div>
                      <div>
                        <h3 className={`text-xs font-bold uppercase tracking-widest mb-1 ${getStatusUI(results.routing.status).color}`}>System Action</h3>
                        <h2 className="text-3xl font-black text-slate-900 tracking-tight">{results.routing.status}</h2>
                        <div className="mt-3 flex items-center gap-2">
                          <span className="text-sm font-semibold text-slate-700">Routed to:</span>
                          <span className="bg-white/80 px-3 py-1 rounded-md shadow-sm border border-slate-200 font-mono text-xs font-bold text-slate-800">
                            {results.routing.assigned_queue}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* ML Risk Score */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-center items-center text-center">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Default Probability</h3>
                    <div className="flex items-center justify-center gap-2">
                      <h1 className={`text-5xl font-black tracking-tighter ${results.metrics.risk_score_predicted > 30 ? 'text-rose-600' : 'text-emerald-600'}`}>
                        {results.metrics.risk_score_predicted}%
                      </h1>
                    </div>
                    <p className="text-xs font-medium text-slate-500 mt-2 flex items-center gap-1">
                      {results.metrics.risk_score_predicted > 30 ? <TrendingUp size={14} className="text-rose-500"/> : <TrendingDown size={14} className="text-emerald-500"/>}
                      Calculated via XGBoost
                    </p>
                  </div>
                </div>

                {/* MIDDLE ROW: LIVE EXTRACTED DATA & SHAP */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Extracted Data Snapshot */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                     <h3 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wide flex items-center gap-2">
                      <Wallet className="text-blue-500" size={18} /> Borrower Snapshot
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      {activeMetrics.length > 0 ? activeMetrics.map(([key, val], idx) => (
                        <div key={idx} className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider truncate" title={key}>{key.replace(/_/g, ' ')}</p>
                          <p className="text-sm font-bold text-slate-800 truncate">{val}</p>
                        </div>
                      )) : (
                        <p className="col-span-2 text-sm text-slate-500 italic">No valid structured metrics extracted.</p>
                      )}
                    </div>
                  </div>

                  {/* SHAP Chart */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h3 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wide flex items-center gap-2">
                      <Activity className="text-blue-500" size={18} /> Risk Drivers (SHAP)
                    </h3>
                    <div className="h-[200px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData.slice(0, 5)} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                          <XAxis type="number" hide />
                          <YAxis dataKey="factor" type="category" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11}} width={100} />
                          <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                          <ReferenceLine x={0} stroke="#cbd5e1" />
                          <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                            {chartData.slice(0, 5).map((d, i) => (
                              <Cell key={i} fill={d.isRisk ? "#ef4444" : "#10b981"} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* BOTTOM ROW: THE AI MEMO */}
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-4 mb-6">
                    <FileText className="text-blue-600" size={24} />
                    <h3 className="text-xl font-bold text-slate-900">Credit Appraisal Memo</h3>
                    <span className="ml-auto text-xs font-semibold bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-200">Auto-Generated via RAG</span>
                  </div>
                  
                  <div className="prose prose-slate prose-h3:text-lg prose-h4:text-base max-w-none">
                    <ReactMarkdown>{results.credit_memo}</ReactMarkdown>
                  </div>
                </div>
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;