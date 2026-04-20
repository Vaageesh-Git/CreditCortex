import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BadgeCheck,
  Ban,
  BriefcaseBusiness,
  Building2,
  CircleAlert,
  Clock3,
  FileText,
  Gauge,
  Landmark,
  Loader2,
  ScanSearch,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  TrendingUp,
  UploadCloud,
  Wallet,
  Waypoints,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  RadialBar,
  RadialBarChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import heroImage from './assets/hero.png';
import './index.css';

const API_URL = 'http://localhost:8000/evaluate-loan';

const STATUS_META = {
  APPROVED: {
    label: 'Auto Approval',
    tone: 'emerald',
    icon: BadgeCheck,
    badge: 'Low Risk',
    bgClass: 'from-emerald-500/15 via-emerald-500/5 to-transparent',
    ringClass: 'ring-emerald-200',
    textClass: 'text-emerald-700',
    pillClass: 'bg-emerald-500/10 text-emerald-700 border-emerald-200',
    fill: '#0f9f6e',
  },
  REJECTED: {
    label: 'Auto Rejection',
    tone: 'rose',
    icon: Ban,
    badge: 'Critical Risk',
    bgClass: 'from-rose-500/15 via-rose-500/5 to-transparent',
    ringClass: 'ring-rose-200',
    textClass: 'text-rose-700',
    pillClass: 'bg-rose-500/10 text-rose-700 border-rose-200',
    fill: '#e23d5c',
  },
  PAUSED: {
    label: 'Escalated Review',
    tone: 'amber',
    icon: CircleAlert,
    badge: 'Manual Intervention',
    bgClass: 'from-amber-500/15 via-amber-500/5 to-transparent',
    ringClass: 'ring-amber-200',
    textClass: 'text-amber-700',
    pillClass: 'bg-amber-500/10 text-amber-700 border-amber-200',
    fill: '#d6a118',
  },
  PENDING_REVIEW: {
    label: 'Analyst Queue',
    tone: 'sky',
    icon: Clock3,
    badge: 'Underwriter Required',
    bgClass: 'from-sky-500/15 via-sky-500/5 to-transparent',
    ringClass: 'ring-sky-200',
    textClass: 'text-sky-700',
    pillClass: 'bg-sky-500/10 text-sky-700 border-sky-200',
    fill: '#0f77c6',
  },
};

const FIELD_LABELS = {
  annual_inc: 'Annual Income',
  dti: 'Debt-to-Income',
  foir: 'FOIR',
  installment: 'Monthly Installment',
  fico_range_low: 'FICO Low',
  fico_range_high: 'FICO High',
  credit_score_avg: 'Credit Score Avg',
  cibil_score: 'CIBIL Score',
  delinq_2yrs: 'Delinquencies (2Y)',
  pub_rec: 'Public Records',
  pub_rec_bankruptcies: 'Bankruptcies',
  revol_bal: 'Revolving Balance',
  revol_util: 'Revolving Utilization',
  credit_utilization: 'Credit Utilization',
  total_acc: 'Total Accounts',
  open_acc: 'Open Accounts',
  inq_last_6mths: 'Recent Inquiries',
  acc_now_delinq: 'Current Delinquencies',
  num_tl_90g_dpd_24m: '90+ DPD Trades',
  max_dpd: 'Max DPD (12M)',
  recent_enquiries: 'Recent Enquiries (6M)',
  cheque_bounces: 'Cheque Bounces (6M)',
  loan_amnt: 'Loan Amount',
  term: 'Term',
  int_rate: 'Interest Rate',
  credit_to_debit_ratio: 'Credit-to-Debit Ratio',
  high_dti_flag: 'High DTI Flag',
  high_util_flag: 'High Utilization Flag',
  home_ownership_MORTGAGE: 'Mortgage',
  home_ownership_NONE: 'No Home Ownership',
  home_ownership_OTHER: 'Home Ownership Other',
  home_ownership_OWN: 'Own Residence',
  home_ownership_RENT: 'Rent Residence',
  purpose_credit_card: 'Purpose: Credit Card',
  purpose_debt_consolidation: 'Purpose: Debt Consolidation',
  purpose_educational: 'Purpose: Educational',
  purpose_home_improvement: 'Purpose: Home Improvement',
  purpose_house: 'Purpose: House',
  purpose_major_purchase: 'Purpose: Major Purchase',
  purpose_medical: 'Purpose: Medical',
  purpose_moving: 'Purpose: Moving',
  purpose_other: 'Purpose: Other',
  purpose_renewable_energy: 'Purpose: Renewable Energy',
  purpose_small_business: 'Purpose: Small Business',
  purpose_vacation: 'Purpose: Vacation',
  purpose_wedding: 'Purpose: Wedding',
  grade_B: 'Grade B',
  grade_C: 'Grade C',
  grade_D: 'Grade D',
  grade_E: 'Grade E',
  grade_F: 'Grade F',
  grade_G: 'Grade G',
  final_decision: 'Final Decision',
  confidence_level: 'Confidence Level',
  policy_violation: 'Policy Violation',
  requires_manual_review: 'Manual Review',
  risk_score_predicted: 'Risk Score',
};

const CURRENCY_KEYS = new Set(['annual_inc', 'installment', 'revol_bal', 'loan_amnt']);
const PERCENT_KEYS = new Set([
  'dti',
  'foir',
  'revol_util',
  'credit_utilization',
  'int_rate',
  'risk_score_predicted',
]);
const INTEGER_KEYS = new Set([
  'fico_range_low',
  'fico_range_high',
  'credit_score_avg',
  'cibil_score',
  'delinq_2yrs',
  'pub_rec',
  'pub_rec_bankruptcies',
  'total_acc',
  'open_acc',
  'inq_last_6mths',
  'acc_now_delinq',
  'num_tl_90g_dpd_24m',
  'max_dpd',
  'recent_enquiries',
  'cheque_bounces',
]);

const PIPELINE_STAGES = [
  {
    title: 'Document Ingestion',
    description: 'Extract tables and narrative text from the uploaded borrower profile.',
    icon: UploadCloud,
  },
  {
    title: 'Risk Scoring',
    description: 'Run the XGBoost engine and compute explainability signals.',
    icon: Activity,
  },
  {
    title: 'Memo Generation',
    description: 'Draft the appraisal note using the compliance and policy context.',
    icon: FileText,
  },
  {
    title: 'Routing Decision',
    description: 'Assign the application to the correct approval or review queue.',
    icon: Waypoints,
  },
];

function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, value));
}

function averageDefined(values) {
  const validValues = values.filter((value) => value !== null && !Number.isNaN(value));
  if (!validValues.length) return null;
  return validValues.reduce((sum, value) => sum + value, 0) / validValues.length;
}

function toNumber(value) {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))) {
    return Number(value);
  }
  return null;
}

function hasRenderableValue(value) {
  return value !== null && value !== undefined && value !== '';
}

function normalizePercentValue(value) {
  const numericValue = toNumber(value);
  if (numericValue === null) return null;
  return Math.abs(numericValue) <= 1 ? numericValue * 100 : numericValue;
}

function extractRiskScore(...sources) {
  const patterns = [
    /Predicted Default Risk:\s*([0-9]+(?:\.[0-9]+)?)%/i,
    /(?:Low risk|High ML risk|High risk|Moderate risk)\s*\(([0-9]+(?:\.[0-9]+)?)%\)/i,
    /risk[^0-9]{0,20}([0-9]+(?:\.[0-9]+)?)%/i,
  ];

  for (const source of sources) {
    if (typeof source !== 'string' || !source.trim()) continue;

    for (const pattern of patterns) {
      const match = source.match(pattern);
      if (match?.[1]) {
        return Number(match[1]);
      }
    }
  }

  return null;
}

function prettifyKey(key) {
  return (FIELD_LABELS[key] || key.replace(/_/g, ' '))
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatMetricValue(key, value) {
  if (value === null || value === undefined || value === '') return 'Not Available';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';

  const numericValue = toNumber(value);
  if (numericValue === null) return String(value);

  if (CURRENCY_KEYS.has(key)) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(numericValue);
  }

  if (PERCENT_KEYS.has(key)) {
    return `${numericValue.toFixed(2)}%`;
  }

  if (INTEGER_KEYS.has(key)) {
    return numericValue.toFixed(0);
  }

  if (key === 'term') {
    return `${numericValue.toFixed(0)} months`;
  }

  if (key === 'credit_to_debit_ratio') {
    return numericValue.toFixed(2);
  }

  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: numericValue % 1 === 0 ? 0 : 2,
  }).format(numericValue);
}

function normalizeResults(payload) {
  if (!payload) return null;

  const routing = payload.routing || {
    status: payload.status || 'PAUSED',
    assigned_queue: payload.assigned_queue || 'DOCUMENT_COLLECTION_TEAM',
    reason: payload.reason || 'Structured financial data is missing from the uploaded document.',
  };

  const decision = payload.decision || {};
  const riskScore = normalizePercentValue(
    payload.metrics?.risk_score_predicted ??
      extractRiskScore(routing.reason, payload.credit_memo)
  );

  const percentageMetrics = {
    foir: normalizePercentValue(payload.percentage_metrics?.foir ?? payload.borrower_data?.foir),
    dti: normalizePercentValue(
      payload.percentage_metrics?.dti ?? payload.borrower_data?.dti ?? payload.borrower_data?.foir
    ),
    credit_utilization: normalizePercentValue(
      payload.percentage_metrics?.credit_utilization ??
        payload.borrower_data?.credit_utilization ??
        payload.borrower_data?.revol_util
    ),
  };

  const conductMetrics = {
    cheque_bounces: toNumber(
      payload.conduct_metrics?.cheque_bounces ??
        payload.borrower_data?.cheque_bounces ??
        payload.borrower_data?.cheque_bounce_count_6m
    ),
    max_dpd: toNumber(
      payload.conduct_metrics?.max_dpd ??
        payload.borrower_data?.max_dpd ??
        payload.borrower_data?.max_dpd_12m
    ),
    recent_enquiries: toNumber(
      payload.conduct_metrics?.recent_enquiries ??
        payload.borrower_data?.recent_enquiries ??
        payload.borrower_data?.recent_enquiries_6m ??
        payload.borrower_data?.inq_last_6mths
    ),
  };

  const borrowerData = {
    ...(payload.borrower_data || {}),
    dti: percentageMetrics.dti,
    foir: percentageMetrics.foir,
    credit_utilization: percentageMetrics.credit_utilization,
    revol_util:
      percentageMetrics.credit_utilization ??
      normalizePercentValue(payload.borrower_data?.revol_util),
    cheque_bounces: conductMetrics.cheque_bounces,
    max_dpd: conductMetrics.max_dpd,
    recent_enquiries: conductMetrics.recent_enquiries,
    final_decision: decision.final_decision,
    confidence_level: decision.confidence_level,
    policy_violation: decision.policy_violation,
    requires_manual_review: decision.requires_manual_review,
    risk_score_predicted: riskScore,
  };

  if (!hasRenderableValue(borrowerData.credit_score_avg) && hasRenderableValue(payload.borrower_data?.cibil_score)) {
    borrowerData.credit_score_avg = payload.borrower_data.cibil_score;
  }

  return {
    routing,
    decision,
    credit_memo: payload.credit_memo || 'Credit memo unavailable.',
    metrics: {
      risk_score_predicted: riskScore,
      shap_signals: payload.metrics?.shap_signals || {},
    },
    borrower_data: borrowerData,
    conduct_metrics: conductMetrics,
    percentage_metrics: percentageMetrics,
  };
}

function getStatusMeta(status) {
  return STATUS_META[status] || STATUS_META.PENDING_REVIEW;
}

function getShapChartData(results) {
  const shapSignals = results?.metrics?.shap_signals || {};

  return Object.entries(shapSignals)
    .map(([factor, rawImpact]) => {
      const impact = toNumber(rawImpact) || 0;
      return {
        factor,
        label: prettifyKey(factor),
        impact,
        absoluteImpact: Math.abs(impact),
        isRisk: impact > 0,
      };
    })
    .sort((left, right) => right.absoluteImpact - left.absoluteImpact);
}

function getSnapshotEntries(results) {
  const borrowerData = results?.borrower_data || {};

  const preferredKeys = [
    'final_decision',
    'confidence_level',
    'risk_score_predicted',
    'foir',
    'credit_utilization',
    'max_dpd',
    'recent_enquiries',
    'cheque_bounces',
    'policy_violation',
    'requires_manual_review',
    'credit_score_avg',
    'loan_amnt',
    'annual_inc',
  ];

  const preferredEntries = preferredKeys
    .filter((key) => hasRenderableValue(borrowerData[key]))
    .map((key) => [key, borrowerData[key]]);

  if (preferredEntries.length) {
    return preferredEntries.slice(0, 10);
  }

  return Object.entries(borrowerData)
    .filter(([, value]) => hasRenderableValue(value))
    .slice(0, 10);
}

function buildRadarData(borrowerData) {
  const creditScoreAvg =
    toNumber(borrowerData.credit_score_avg) ||
    toNumber(borrowerData.cibil_score) ||
    averageDefined([toNumber(borrowerData.fico_range_low), toNumber(borrowerData.fico_range_high)]);
  const foir = normalizePercentValue(borrowerData.foir ?? borrowerData.dti);
  const creditUtilization = normalizePercentValue(
    borrowerData.credit_utilization ?? borrowerData.revol_util
  );
  const maxDpd = toNumber(borrowerData.max_dpd ?? borrowerData.max_dpd_12m);
  const recentEnquiries = toNumber(
    borrowerData.recent_enquiries ?? borrowerData.recent_enquiries_6m ?? borrowerData.inq_last_6mths
  );
  const chequeBounces = toNumber(
    borrowerData.cheque_bounces ?? borrowerData.cheque_bounce_count_6m
  );

  return [
    creditScoreAvg !== null
      ? { subject: 'Bureau', score: clamp(((creditScoreAvg - 300) / 600) * 100) }
      : null,
    foir !== null ? { subject: 'FOIR', score: clamp(100 - foir) } : null,
    creditUtilization !== null
      ? { subject: 'Utilization', score: clamp(100 - creditUtilization) }
      : null,
    maxDpd !== null ? { subject: 'DPD', score: clamp(100 - (maxDpd / 90) * 100) } : null,
    recentEnquiries !== null
      ? { subject: 'Enquiries', score: clamp(100 - (recentEnquiries / 6) * 100) }
      : null,
    chequeBounces !== null
      ? { subject: 'Stability', score: clamp(100 - (chequeBounces / 4) * 100) }
      : null,
  ]
    .filter(Boolean)
    .map((item) => ({ ...item, score: Number(item.score.toFixed(1)) }));
}

function buildPressureData(borrowerData) {
  return [
    hasRenderableValue(borrowerData.foir ?? borrowerData.dti)
      ? { label: 'FOIR', value: normalizePercentValue(borrowerData.foir ?? borrowerData.dti) || 0 }
      : null,
    hasRenderableValue(borrowerData.credit_utilization ?? borrowerData.revol_util)
      ? {
          label: 'Credit Util',
          value: normalizePercentValue(
            borrowerData.credit_utilization ?? borrowerData.revol_util
          ) || 0,
        }
      : null,
    hasRenderableValue(borrowerData.risk_score_predicted)
      ? { label: 'PD Score', value: normalizePercentValue(borrowerData.risk_score_predicted) || 0 }
      : null,
  ].filter(Boolean);
}

function buildConductData(borrowerData) {
  return [
    hasRenderableValue(borrowerData.max_dpd ?? borrowerData.max_dpd_12m)
      ? { label: 'Max DPD', value: toNumber(borrowerData.max_dpd ?? borrowerData.max_dpd_12m) || 0 }
      : null,
    hasRenderableValue(
      borrowerData.recent_enquiries ??
        borrowerData.recent_enquiries_6m ??
        borrowerData.inq_last_6mths
    )
      ? {
          label: 'Enquiries',
          value:
            toNumber(
              borrowerData.recent_enquiries ??
                borrowerData.recent_enquiries_6m ??
                borrowerData.inq_last_6mths
            ) || 0,
        }
      : null,
    hasRenderableValue(borrowerData.cheque_bounces ?? borrowerData.cheque_bounce_count_6m)
      ? {
          label: 'Cheque Bounce',
          value: toNumber(borrowerData.cheque_bounces ?? borrowerData.cheque_bounce_count_6m) || 0,
        }
      : null,
  ].filter(Boolean);
}

function getFactorCollections(results) {
  const shapData = getShapChartData(results);
  if (shapData.length) {
    return {
      hasNumericImpacts: true,
      riskItems: shapData.filter((item) => item.isRisk),
      positiveItems: shapData.filter((item) => !item.isRisk),
    };
  }

  const decision = results?.decision || {};
  const riskItems = Array.isArray(decision.key_risk_factors)
    ? decision.key_risk_factors
        .filter(Boolean)
        .map((label, index) => ({ factor: `risk-${index}`, label, impact: null, isRisk: true }))
    : [];
  const positiveItems = Array.isArray(decision.key_positive_factors)
    ? decision.key_positive_factors
        .filter(Boolean)
        .map((label, index) => ({ factor: `positive-${index}`, label, impact: null, isRisk: false }))
    : [];

  return {
    hasNumericImpacts: false,
    riskItems,
    positiveItems,
  };
}

function decisionTone(decision) {
  switch (String(decision || '').toUpperCase()) {
    case 'APPROVE':
    case 'APPROVED':
      return 'emerald';
    case 'REJECT':
    case 'REJECTED':
      return 'rose';
    default:
      return 'amber';
  }
}

function confidenceTone(confidence) {
  switch (String(confidence || '').toUpperCase()) {
    case 'HIGH':
      return 'emerald';
    case 'LOW':
      return 'rose';
    default:
      return 'sky';
  }
}

function buildDecisionSummaryCards(results) {
  const decision = results?.decision || {};
  const riskItems = Array.isArray(decision.key_risk_factors) ? decision.key_risk_factors : [];
  const positiveItems = Array.isArray(decision.key_positive_factors) ? decision.key_positive_factors : [];
  const riskScore = normalizePercentValue(results?.metrics?.risk_score_predicted);

  return [
    hasRenderableValue(decision.final_decision)
      ? {
          label: 'Policy Decision',
          value: decision.final_decision,
          caption: 'Final verdict produced by the orchestrator decision JSON.',
          accent: decisionTone(decision.final_decision),
        }
      : null,
    hasRenderableValue(decision.confidence_level)
      ? {
          label: 'Confidence',
          value: decision.confidence_level,
          caption: 'Confidence level returned by the current credit policy evaluation.',
          accent: confidenceTone(decision.confidence_level),
        }
      : null,
    riskScore !== null
      ? {
          label: 'Risk Score',
          value: `${riskScore.toFixed(2)}%`,
          caption: 'Extracted from the current response text and aligned to the routing output.',
          accent: riskScore >= 25 ? 'rose' : riskScore <= 2 ? 'emerald' : 'amber',
        }
      : null,
    hasRenderableValue(decision.policy_violation)
      ? {
          label: 'Policy Violation',
          value: decision.policy_violation ? 'Yes' : 'No',
          caption: 'Indicates whether the AI flagged an explicit policy breach.',
          accent: decision.policy_violation ? 'rose' : 'emerald',
        }
      : null,
    hasRenderableValue(decision.requires_manual_review)
      ? {
          label: 'Manual Review',
          value: decision.requires_manual_review ? 'Required' : 'Not Required',
          caption: 'Shows whether the orchestrator requested human underwriting review.',
          accent: decision.requires_manual_review ? 'amber' : 'sky',
        }
      : null,
    riskItems.length
      ? {
          label: 'Risk Factors',
          value: `${riskItems.length}`,
          caption: 'Count of returned negative decision factors in the JSON response.',
          accent: 'rose',
        }
      : null,
    positiveItems.length
      ? {
          label: 'Positive Factors',
          value: `${positiveItems.length}`,
          caption: 'Count of returned positive decision factors in the JSON response.',
          accent: 'emerald',
        }
      : null,
  ].filter(Boolean);
}

function buildRiskMarkers(results) {
  const decision = results?.decision || {};
  const borrowerData = results?.borrower_data || {};
  const riskScore = normalizePercentValue(results?.metrics?.risk_score_predicted);
  const foir = normalizePercentValue(borrowerData.foir ?? borrowerData.dti);
  const utilization = normalizePercentValue(
    borrowerData.credit_utilization ?? borrowerData.revol_util
  );

  return [
    hasRenderableValue(decision.final_decision)
      ? {
          label: 'Final Decision',
          value: decision.final_decision,
          hint: 'Directly read from the structured decision JSON returned by the API.',
          tone: decisionTone(decision.final_decision),
        }
      : null,
    riskScore !== null
      ? {
          label: 'Probability of Default',
          value: `${riskScore.toFixed(2)}%`,
          hint: 'Routing thresholds now run with auto-approve below 2% and auto-reject from 25%.',
          tone: riskScore >= 25 ? 'rose' : riskScore <= 2 ? 'emerald' : 'amber',
        }
      : null,
    hasRenderableValue(decision.confidence_level)
      ? {
          label: 'Confidence',
          value: decision.confidence_level,
          hint: 'Confidence level produced by the current AI decision policy.',
          tone: confidenceTone(decision.confidence_level),
        }
      : null,
    foir !== null
      ? {
          label: 'FOIR',
          value: formatMetricValue('foir', foir),
          hint: 'Fixed Obligation to Income Ratio taken from the latest semantic extraction.',
          tone: foir > 60 ? 'rose' : foir >= 45 ? 'amber' : 'emerald',
        }
      : null,
    utilization !== null
      ? {
          label: 'Credit Utilization',
          value: formatMetricValue('credit_utilization', utilization),
          hint: 'Higher utilization increases short-term balance sheet pressure.',
          tone: utilization > 75 ? 'rose' : utilization >= 50 ? 'amber' : 'emerald',
        }
      : null,
  ].filter(Boolean);
}

function toneClasses(tone) {
  const classes = {
    rose: 'border-rose-200 bg-rose-50 text-rose-700',
    emerald: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    amber: 'border-amber-200 bg-amber-50 text-amber-700',
    sky: 'border-sky-200 bg-sky-50 text-sky-700',
  };

  return classes[tone] || classes.sky;
}

function StatTile({ label, value, caption, accent = 'sky' }) {
  return (
    <div className={`rounded-2xl border p-4 ${toneClasses(accent)} shadow-sm`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.22em] opacity-80">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
      <p className="mt-2 text-xs leading-5 text-slate-600">{caption}</p>
    </div>
  );
}

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files?.[0] || null);
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
      const response = await axios.post(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(normalizeResults(response.data));
    } catch (uploadError) {
      setError(uploadError.response?.data?.detail || 'Error processing the borrower profile.');
      setResults(null);
    } finally {
      setIsProcessing(false);
    }
  };

  const status = results?.routing?.status;
  const statusMeta = getStatusMeta(status);
  const StatusIcon = statusMeta.icon;
  const decision = results?.decision || {};
  const riskScore = normalizePercentValue(results?.metrics?.risk_score_predicted);
  const shapData = getShapChartData(results);
  const borrowerData = results?.borrower_data || {};
  const snapshotEntries = getSnapshotEntries(results);
  const radarData = buildRadarData(borrowerData);
  const decisionSummaryCards = buildDecisionSummaryCards(results);
  const pressureData = buildPressureData(borrowerData);
  const conductData = buildConductData(borrowerData);
  const riskMarkers = buildRiskMarkers(results);
  const factorCollections = getFactorCollections(results);
  const topRiskDrivers = factorCollections.riskItems.slice(0, 4);
  const topMitigants = factorCollections.positiveItems.slice(0, 3);
  const heroHighlights = [
    ['Policy Decision', decision.final_decision || statusMeta.label],
    ['Confidence', decision.confidence_level || 'Not Available'],
    ['FOIR', formatMetricValue('foir', borrowerData.foir ?? borrowerData.dti ?? null)],
    [
      'Credit Utilization',
      formatMetricValue(
        'credit_utilization',
        borrowerData.credit_utilization ?? borrowerData.revol_util ?? null
      ),
    ],
  ];
  const reportDate = new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date());

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(15,118,198,0.10),_transparent_24%),linear-gradient(180deg,#eef4f8_0%,#f7f5ef_52%,#eef3f6_100%)] text-slate-900">
      <header className="sticky top-0 z-40 border-b border-white/60 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1580px] items-center justify-between gap-4 px-6 py-4 lg:px-8">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-[0_18px_40px_-22px_rgba(15,23,42,0.85)]">
              <Landmark size={22} />
            </div>
            <div>
              <p className="dashboard-kicker">CreditCortex</p>
              <h1 className="dashboard-title text-[1.4rem] leading-none text-slate-950">
                NPA Prevention Command Center
              </h1>
            </div>
          </div>

          <div className="hidden items-center gap-3 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 md:flex">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </span>
            Credit decisioning service online
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1580px] px-6 py-6 lg:px-8 lg:py-8">
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <aside className="space-y-6 xl:col-span-4">
            <section className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_25px_60px_-35px_rgba(15,23,42,0.35)]">
              <div className="bg-[linear-gradient(135deg,#0f172a_0%,#123554_50%,#14532d_120%)] p-6 text-white">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="dashboard-kicker text-white/70">Officer Console</p>
                    <h2 className="dashboard-title text-[1.75rem] leading-tight">
                      Live credit appraisal intake
                    </h2>
                  </div>
                  <div className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white/80">
                    {reportDate}
                  </div>
                </div>
                <p className="mt-4 max-w-xl text-sm leading-6 text-slate-200">
                  Upload a real borrower PDF and CreditCortex will extract financials, score NPA risk,
                  generate the memo, and route the case to the right underwriting queue.
                </p>
              </div>

              <div className="space-y-5 p-6">
                <label
                  htmlFor="file-upload"
                  className="group block cursor-pointer rounded-[24px] border-2 border-dashed border-slate-300 bg-slate-50 p-6 transition hover:border-sky-300 hover:bg-sky-50"
                >
                  <input
                    id="file-upload"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <div className="flex items-center gap-4">
                    <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200 transition group-hover:scale-105">
                      <UploadCloud className="text-sky-600" size={28} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-slate-950">
                        {selectedFile ? selectedFile.name : 'Select borrower profile PDF'}
                      </p>
                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        Real extracted tables and narrative text only. No synthetic dashboard payloads.
                      </p>
                    </div>
                  </div>
                </label>

                <button
                  type="button"
                  onClick={handleUpload}
                  disabled={!selectedFile || isProcessing}
                  className="flex w-full items-center justify-center gap-3 rounded-2xl bg-slate-950 px-5 py-4 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="animate-spin" size={18} />
                      Running CreditCortex pipeline
                    </>
                  ) : (
                    <>
                      Execute appraisal workflow
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>

                {error && (
                  <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                    <div className="flex items-start gap-3">
                      <ShieldAlert className="mt-0.5 shrink-0" size={18} />
                      <p>{error}</p>
                    </div>
                  </div>
                )}

                <div className="space-y-3">
                  {PIPELINE_STAGES.map((stage, index) => {
                    const StageIcon = stage.icon;
                    const isActive = isProcessing;
                    const isComplete = Boolean(results) && !isProcessing;

                    return (
                      <div
                        key={stage.title}
                        className={`rounded-2xl border p-4 transition ${
                          isComplete
                            ? 'border-emerald-200 bg-emerald-50'
                            : isActive
                              ? 'border-sky-200 bg-sky-50'
                              : 'border-slate-200 bg-white'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`mt-0.5 rounded-xl p-2 ${
                              isComplete
                                ? 'bg-emerald-100 text-emerald-700'
                                : isActive
                                  ? 'bg-sky-100 text-sky-700'
                                  : 'bg-slate-100 text-slate-500'
                            }`}
                          >
                            <StageIcon size={16} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-semibold text-slate-950">
                                {index + 1}. {stage.title}
                              </p>
                              {isComplete && (
                                <span className="rounded-full border border-emerald-200 bg-white px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-700">
                                  Complete
                                </span>
                              )}
                              {isActive && !isComplete && (
                                <span className="rounded-full border border-sky-200 bg-white px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.18em] text-sky-700">
                                  Processing
                                </span>
                              )}
                            </div>
                            <p className="mt-1 text-xs leading-5 text-slate-500">{stage.description}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>

            <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-35px_rgba(15,23,42,0.25)]">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-slate-950 p-3 text-white">
                  <ScanSearch size={18} />
                </div>
                <div>
                  <p className="dashboard-kicker">Signal Monitor</p>
                  <h3 className="dashboard-title text-[1.2rem] leading-tight text-slate-950">
                    Underwriting checkpoints
                  </h3>
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {riskMarkers.length ? (
                  riskMarkers.map((marker) => (
                    <div
                      key={marker.label}
                      className={`rounded-2xl border p-4 ${toneClasses(marker.tone)}`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-slate-950">{marker.label}</p>
                        <span className="text-sm font-semibold text-slate-950">{marker.value}</span>
                      </div>
                      <p className="mt-2 text-xs leading-5 text-slate-600">{marker.hint}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm leading-6 text-slate-500">
                    Live monitoring cards will populate from the extracted application after a borrower
                    PDF is processed.
                  </div>
                )}
              </div>
            </section>

            <section className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_25px_60px_-35px_rgba(15,23,42,0.25)]">
              <div className="border-b border-slate-200 px-6 py-5">
                <p className="dashboard-kicker">Explainability Watch</p>
                <h3 className="dashboard-title text-[1.2rem] leading-tight text-slate-950">
                  Primary risk and cushion factors
                </h3>
              </div>

              <div className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-5">
                  <div className="flex items-center gap-2 text-rose-700">
                    <AlertTriangle size={16} />
                    <p className="text-xs font-bold uppercase tracking-[0.18em]">Risk Drivers</p>
                  </div>
                  <div className="mt-4 space-y-3">
                    {topRiskDrivers.length ? (
                      topRiskDrivers.map((item) => (
                        <div key={item.factor} className="rounded-2xl border border-rose-200 bg-white p-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="text-sm font-semibold text-slate-950">{item.label}</p>
                            {item.impact !== null ? (
                              <span className="text-sm font-semibold text-rose-700">
                                +{item.impact.toFixed(3)}
                              </span>
                            ) : null}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm leading-6 text-slate-500">
                        No structured risk factors are available in the latest response.
                      </p>
                    )}
                  </div>
                </div>

                <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-5">
                  <div className="flex items-center gap-2 text-emerald-700">
                    <Sparkles size={16} />
                    <p className="text-xs font-bold uppercase tracking-[0.18em]">Mitigants</p>
                  </div>
                  <div className="mt-4 space-y-3">
                    {topMitigants.length ? (
                      topMitigants.map((item) => (
                        <div key={item.factor} className="rounded-2xl border border-emerald-200 bg-white p-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="text-sm font-semibold text-slate-950">{item.label}</p>
                            {item.impact !== null ? (
                              <span className="text-sm font-semibold text-emerald-700">
                                {item.impact.toFixed(3)}
                              </span>
                            ) : null}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm leading-6 text-slate-500">
                        Positive factors will appear here when the API returns them.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </section>
          </aside>

          <section className="space-y-6 xl:col-span-8">
            {!results && !isProcessing && (
              <section className="overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-[0_30px_80px_-45px_rgba(15,23,42,0.32)]">
                <div className="grid items-stretch gap-0 lg:grid-cols-[1.2fr_0.8fr]">
                  <div className="bg-[linear-gradient(145deg,#0f172a_0%,#123554_52%,#0f766e_130%)] p-8 text-white lg:p-10">
                    <p className="dashboard-kicker text-white/70">Executive View</p>
                    <h2 className="dashboard-title max-w-xl text-[2.25rem] leading-tight text-white lg:text-[2.8rem]">
                      Turn raw borrower documents into an officer-grade NPA prevention dashboard.
                    </h2>
                    <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-200">
                      The interface will populate only after a real application is processed. Graphs,
                      highlights, and the memo all render directly from the live extracted borrower
                      profile and risk engine output.
                    </p>
                    <div className="mt-8 grid gap-4 md:grid-cols-3">
                      <StatTile
                        label="Workflow"
                        value="4-stage"
                        caption="Ingestion, scoring, memo generation, and routing."
                        accent="sky"
                      />
                      <StatTile
                        label="Decisioning"
                        value="Live"
                        caption="Queue recommendation comes from the current backend decision."
                        accent="emerald"
                      />
                      <StatTile
                        label="Data Source"
                        value="Actual PDF"
                        caption="No placeholder charts are shown before a real run."
                        accent="amber"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-center bg-[linear-gradient(180deg,#f8fafc_0%,#eef5f6_100%)] p-8">
                    <img
                      src={heroImage}
                      alt="CreditCortex dashboard illustration"
                      className="max-h-[420px] w-full max-w-[420px] object-contain drop-shadow-[0_35px_50px_rgba(15,23,42,0.22)]"
                    />
                  </div>
                </div>
              </section>
            )}

            {results && (
              <>
                <section
                  className={`overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-[0_30px_80px_-45px_rgba(15,23,42,0.32)]`}
                >
                  <div className={`bg-gradient-to-br ${statusMeta.bgClass} p-1`}>
                    <div className="grid gap-6 rounded-[30px] bg-[linear-gradient(135deg,#fefefe_0%,#f7fbff_60%,#f5f7f2_100%)] p-6 lg:grid-cols-[1.2fr_0.8fr] lg:p-8">
                      <div>
                        <div className="flex flex-wrap items-center gap-3">
                          <span className={`rounded-full border px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] ${statusMeta.pillClass}`}>
                            {statusMeta.badge}
                          </span>
                          <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">
                            Queue: {results.routing.assigned_queue}
                          </span>
                        </div>

                        <div className="mt-6 flex items-start gap-4">
                          <div className={`rounded-[24px] bg-white p-4 shadow-sm ring-1 ${statusMeta.ringClass}`}>
                            <StatusIcon className={statusMeta.textClass} size={30} />
                          </div>
                          <div>
                            <p className="dashboard-kicker">Routing Outcome</p>
                            <h2 className="dashboard-title text-[2rem] leading-none text-slate-950 lg:text-[2.4rem]">
                              {statusMeta.label}
                            </h2>
                            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
                              {results.routing.reason}
                            </p>
                          </div>
                        </div>

                        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                          {heroHighlights.map(([label, value]) => (
                            <div key={label} className="rounded-2xl border border-slate-200 bg-white/90 p-4 shadow-sm">
                              <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                                {label}
                              </p>
                              <p className="mt-2 text-lg font-semibold text-slate-950">{value}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-40px_rgba(15,23,42,0.5)]">
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <p className="dashboard-kicker">Probability of Default</p>
                            <h3 className="dashboard-title text-[1.4rem] leading-tight text-slate-950">
                              Credit risk posture
                            </h3>
                          </div>
                          <Gauge className={statusMeta.textClass} size={24} />
                        </div>

                        <div className="relative mt-5 h-[260px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadialBarChart
                              data={[{ name: 'Risk', value: riskScore || 0, fill: statusMeta.fill }]}
                              startAngle={210}
                              endAngle={-30}
                              innerRadius="70%"
                              outerRadius="100%"
                              barSize={18}
                            >
                              <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                              <RadialBar background dataKey="value" cornerRadius={18} />
                            </RadialBarChart>
                          </ResponsiveContainer>

                          <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <p className={`text-5xl font-semibold tracking-tight ${statusMeta.textClass}`}>
                              {riskScore !== null ? `${riskScore.toFixed(2)}%` : 'N/A'}
                            </p>
                            <p className="mt-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                              Risk Score
                            </p>
                            <p className="mt-4 max-w-[220px] text-center text-xs leading-5 text-slate-500">
                              Threshold logic from the current routing rules drives the final queue assignment.
                            </p>
                          </div>
                        </div>

                        <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
                          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
                            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-700">
                              Auto Approve
                            </p>
                            <p className="mt-2 text-xl font-semibold text-slate-950">&lt; 2%</p>
                          </div>
                          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
                            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-amber-700">
                              Human Review
                            </p>
                            <p className="mt-2 text-xl font-semibold text-slate-950">2% - 25%</p>
                          </div>
                          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4">
                            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-rose-700">
                              Auto Reject
                            </p>
                            <p className="mt-2 text-xl font-semibold text-slate-950">&ge; 25%</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>

                <section className="grid gap-6 xl:grid-cols-5">
                  <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] xl:col-span-3">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="dashboard-kicker">Explainability</p>
                        <h3 className="dashboard-title text-[1.35rem] leading-tight text-slate-950">
                          {factorCollections.hasNumericImpacts ? 'Top SHAP drivers' : 'Decision factors'}
                        </h3>
                      </div>
                      <div className="rounded-2xl bg-slate-950 p-3 text-white">
                        <Activity size={18} />
                      </div>
                    </div>

                    <div className="mt-6 h-[340px]">
                      {shapData.length ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={shapData.slice(0, 8)}
                            layout="vertical"
                            margin={{ top: 0, right: 16, left: 16, bottom: 0 }}
                          >
                            <CartesianGrid stroke="#e9eef4" horizontal={false} />
                            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} />
                            <YAxis
                              dataKey="label"
                              type="category"
                              width={132}
                              tick={{ fill: '#0f172a', fontSize: 12 }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip
                              cursor={{ fill: '#f8fafc' }}
                              formatter={(value) => Number(value).toFixed(4)}
                              contentStyle={{
                                borderRadius: '16px',
                                border: '1px solid #dbe4ee',
                                boxShadow: '0 20px 50px -32px rgba(15, 23, 42, 0.4)',
                              }}
                            />
                            <ReferenceLine x={0} stroke="#94a3b8" />
                            <Bar dataKey="impact" radius={[0, 8, 8, 0]}>
                              {shapData.slice(0, 8).map((entry) => (
                                <Cell key={entry.factor} fill={entry.isRisk ? '#e23d5c' : '#0f9f6e'} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      ) : topRiskDrivers.length || topMitigants.length ? (
                        <div className="grid h-full gap-4 md:grid-cols-2">
                          <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-5">
                            <p className="text-xs font-bold uppercase tracking-[0.18em] text-rose-700">
                              Risk Factors
                            </p>
                            <div className="mt-4 space-y-3">
                              {topRiskDrivers.length ? (
                                topRiskDrivers.map((item) => (
                                  <div
                                    key={item.factor}
                                    className="rounded-2xl border border-rose-200 bg-white p-3 text-sm font-semibold leading-6 text-slate-950"
                                  >
                                    {item.label}
                                  </div>
                                ))
                              ) : (
                                <p className="text-sm leading-6 text-slate-500">
                                  No negative factors were returned.
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-5">
                            <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-700">
                              Positive Factors
                            </p>
                            <div className="mt-4 space-y-3">
                              {topMitigants.length ? (
                                topMitigants.map((item) => (
                                  <div
                                    key={item.factor}
                                    className="rounded-2xl border border-emerald-200 bg-white p-3 text-sm font-semibold leading-6 text-slate-950"
                                  >
                                    {item.label}
                                  </div>
                                ))
                              ) : (
                                <p className="text-sm leading-6 text-slate-500">
                                  No positive factors were returned.
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex h-full items-center justify-center rounded-[24px] border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
                          Decision factors will appear here when the response includes them.
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] xl:col-span-2">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="dashboard-kicker">Portfolio Lens</p>
                        <h3 className="dashboard-title text-[1.35rem] leading-tight text-slate-950">
                          Borrower health view
                        </h3>
                      </div>
                      <div className="rounded-2xl bg-slate-950 p-3 text-white">
                        <BriefcaseBusiness size={18} />
                      </div>
                    </div>

                    <div className="mt-6 h-[340px]">
                      {radarData.length ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={radarData}>
                            <PolarGrid stroke="#d7e2ea" />
                            <PolarAngleAxis
                              dataKey="subject"
                              tick={{ fill: '#334155', fontSize: 12, fontWeight: 600 }}
                            />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                            <Radar
                              name="Borrower"
                              dataKey="score"
                              stroke="#0f77c6"
                              fill="#0f77c6"
                              fillOpacity={0.2}
                              strokeWidth={2.5}
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="flex h-full items-center justify-center rounded-[24px] border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
                          Derived borrower health scores will populate from the actual extracted metrics.
                        </div>
                      )}
                    </div>

                    <p className="mt-3 text-xs leading-6 text-slate-500">
                      FOIR, bureau quality, utilization, DPD history, enquiry pressure, and cheque
                      behavior are derived directly from the latest backend response.
                    </p>
                  </div>
                </section>

                <section className="grid gap-6 xl:grid-cols-5">
                  <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] xl:col-span-3">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="dashboard-kicker">Decision Overview</p>
                        <h3 className="dashboard-title text-[1.35rem] leading-tight text-slate-950">
                          Policy and routing summary
                        </h3>
                      </div>
                      <div className="rounded-2xl bg-slate-950 p-3 text-white">
                        <Wallet size={18} />
                      </div>
                    </div>

                    <div className="mt-6 grid gap-4 md:grid-cols-2">
                      {decisionSummaryCards.length ? (
                        decisionSummaryCards.map((card) => (
                          <StatTile
                            key={card.label}
                            label={card.label}
                            value={card.value}
                            caption={card.caption}
                            accent={card.accent}
                          />
                        ))
                      ) : (
                        <div className="md:col-span-2 flex min-h-[320px] items-center justify-center rounded-[24px] border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
                          Structured decision metadata is not available for this application.
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] xl:col-span-2">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="dashboard-kicker">Pressure Gauge</p>
                        <h3 className="dashboard-title text-[1.35rem] leading-tight text-slate-950">
                          Core percentage metrics
                        </h3>
                      </div>
                      <div className="rounded-2xl bg-slate-950 p-3 text-white">
                        <Gauge size={18} />
                      </div>
                    </div>

                    <div className="mt-6 h-[320px]">
                      {pressureData.length ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={pressureData}
                            layout="vertical"
                            margin={{ top: 8, right: 8, left: 8, bottom: 0 }}
                          >
                            <CartesianGrid stroke="#e9eef4" horizontal={false} />
                            <XAxis
                              type="number"
                              domain={[0, 100]}
                              tick={{ fill: '#475569', fontSize: 12 }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis
                              dataKey="label"
                              type="category"
                              width={96}
                              tick={{ fill: '#0f172a', fontSize: 12 }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip
                              formatter={(value) => `${Number(value).toFixed(2)}%`}
                              contentStyle={{
                                borderRadius: '16px',
                                border: '1px solid #dbe4ee',
                                boxShadow: '0 20px 50px -32px rgba(15, 23, 42, 0.4)',
                              }}
                            />
                            <Bar dataKey="value" radius={[0, 10, 10, 0]}>
                              {pressureData.map((entry) => (
                                <Cell
                                  key={entry.label}
                                  fill={entry.value > 40 ? '#e23d5c' : entry.value > 25 ? '#d6a118' : '#0f77c6'}
                                />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="flex h-full items-center justify-center rounded-[24px] border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
                          Percentage-based borrower metrics will render here after extraction.
                        </div>
                      )}
                    </div>
                  </div>
                </section>

                <section className="grid gap-6 xl:grid-cols-5">
                  <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] xl:col-span-3">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="dashboard-kicker">Borrower Snapshot</p>
                        <h3 className="dashboard-title text-[1.35rem] leading-tight text-slate-950">
                          Extracted application facts
                        </h3>
                      </div>
                      <div className="rounded-2xl bg-slate-950 p-3 text-white">
                        <Building2 size={18} />
                      </div>
                    </div>

                    <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                      {snapshotEntries.length ? (
                        snapshotEntries.map(([key, value]) => (
                          <div
                            key={key}
                            className="rounded-[24px] border border-slate-200 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbfd_100%)] p-4 shadow-sm"
                          >
                            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                              {prettifyKey(key)}
                            </p>
                            <p className="mt-3 text-lg font-semibold leading-snug text-slate-950">
                              {formatMetricValue(key, value)}
                            </p>
                          </div>
                        ))
                      ) : (
                        <div className="col-span-full rounded-[24px] border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
                          No structured borrower fields were returned for this application.
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] xl:col-span-2">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="dashboard-kicker">Conduct Signals</p>
                        <h3 className="dashboard-title text-[1.35rem] leading-tight text-slate-950">
                          Behavior and exception counts
                        </h3>
                      </div>
                      <div className="rounded-2xl bg-slate-950 p-3 text-white">
                        <TrendingDown size={18} />
                      </div>
                    </div>

                    <div className="mt-6 h-[320px]">
                      {conductData.length ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={conductData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                            <CartesianGrid stroke="#e9eef4" vertical={false} />
                            <XAxis
                              dataKey="label"
                              tick={{ fill: '#475569', fontSize: 11 }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis
                              tick={{ fill: '#475569', fontSize: 12 }}
                              allowDecimals={false}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip
                              formatter={(value) => Number(value).toFixed(0)}
                              contentStyle={{
                                borderRadius: '16px',
                                border: '1px solid #dbe4ee',
                                boxShadow: '0 20px 50px -32px rgba(15, 23, 42, 0.4)',
                              }}
                            />
                            <Bar dataKey="value" radius={[10, 10, 0, 0]} fill="#14532d" />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="flex h-full items-center justify-center rounded-[24px] border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
                          No conduct counters were present in the returned borrower profile.
                        </div>
                      )}
                    </div>
                  </div>
                </section>

                <section className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)] lg:p-8">
                  <div className="flex flex-wrap items-center gap-4 border-b border-slate-200 pb-5">
                    <div className="rounded-2xl bg-slate-950 p-3 text-white">
                      <FileText size={20} />
                    </div>
                    <div>
                      <p className="dashboard-kicker">Narrative Memo</p>
                      <h3 className="dashboard-title text-[1.45rem] leading-tight text-slate-950">
                        Credit appraisal note
                      </h3>
                    </div>
                    <span className="ml-auto rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-sky-700">
                      Generated from current case data
                    </span>
                  </div>

                  <div className="memo-prose mt-6">
                    <ReactMarkdown>{results.credit_memo}</ReactMarkdown>
                  </div>
                </section>
              </>
            )}

            {isProcessing && (
              <section className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-[0_25px_60px_-38px_rgba(15,23,42,0.25)]">
                <div className="flex items-center gap-4">
                  <div className="rounded-2xl bg-slate-950 p-4 text-white">
                    <Loader2 className="animate-spin" size={24} />
                  </div>
                  <div>
                    <p className="dashboard-kicker">Pipeline Running</p>
                    <h3 className="dashboard-title text-[1.5rem] leading-tight text-slate-950">
                      Processing the borrower application
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      CreditCortex is extracting structured data, scoring the case, generating the
                      memo, and preparing the routing recommendation.
                    </p>
                  </div>
                </div>
              </section>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
