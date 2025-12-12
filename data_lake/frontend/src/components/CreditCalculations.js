import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CreditCalculations = () => {
  const [customerId, setCustomerId] = useState('CUST_MSM_00001');
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const resp = await axios.get(`/api/analytics?customer_id=${customerId}`);
      setAnalytics(resp.data);
    } catch (e) {
      console.error('Failed to load analytics', e);
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !analytics) return <div className="p-6">Loading calculations...</div>;

  const overall = analytics.overall || {};
  const tx = analytics.transactions || {};
  const gst = analytics.gst || {};
  const ondc = analytics.ondc || {};
  const mf = analytics.mutual_funds || {};
  const ins = analytics.insurance || {};
  const ocen = analytics.ocen || {};
  const credit = analytics.credit || {};

  // Cashflow derivation examples
  const cashflowScore = overall.scores?.cashflow_stability || 0;
  const totalTxn = tx.total_transactions || 0;
  const totalAmt = tx.total_amount || 0;
  const avgTxn = tx.average_transaction || (totalTxn ? totalAmt / totalTxn : 0);

  // Business derivation examples
  const businessScore = overall.scores?.business_health || 0;
  const gstBusinesses = gst.total_businesses || 0;
  const gstTurnover = gst.total_revenue || gst.annual_turnover || 0;
  const providerDiversity = ondc.provider_diversity || ondc.unique_providers || Object.keys(ondc.by_provider || {}).length;

  // Debt capacity derivation examples
  const debtScore = overall.scores?.debt_capacity || 0;
  const creditUtil = credit.credit_utilization || (credit.calculation && credit.calculation.credit_utilization) || (credit.credit_utilization === 0 ? 0 : null);
  const ocenApproval = ocen.approval_rate || 0;

  const methodology = overall.score_methodology || {};

  return (
    <div className="space-y-6 p-6">
      <h2 className="text-2xl font-bold">Credit Calculations — {customerId}</h2>

      <section className="bg-white rounded-lg p-4 shadow">
        <h3 className="font-semibold">Composite Score</h3>
        <p className="text-sm text-gray-600">Formula: {methodology.composite_formula || '0.45*cashflow + 0.35*business + 0.20*debt'}</p>
        <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 border rounded">
            <p className="text-xs text-gray-500">Cashflow Stability</p>
            <p className="text-xl font-bold">{cashflowScore}</p>
            <p className="text-sm text-gray-600 mt-2">Derived from transactions:</p>
            <ul className="text-sm text-gray-700 ml-4 list-disc">
              <li>Total transactions: {totalTxn}</li>
              <li>Total amount: ₹{Math.round(totalAmt).toLocaleString()}</li>
              <li>Average txn: ₹{Math.round(avgTxn).toLocaleString()}</li>
            </ul>
          </div>

          <div className="p-3 border rounded">
            <p className="text-xs text-gray-500">Business Health</p>
            <p className="text-xl font-bold">{businessScore}</p>
            <p className="text-sm text-gray-600 mt-2">Contributors:</p>
            <ul className="text-sm text-gray-700 ml-4 list-disc">
              <li>GST businesses: {gstBusinesses}</li>
              <li>GST turnover: ₹{Math.round(gstTurnover).toLocaleString()}</li>
              <li>ONDC provider diversity: {providerDiversity}</li>
              <li>Mutual fund portfolios: {mf.total_portfolios || 0}</li>
            </ul>
          </div>

          <div className="p-3 border rounded">
            <p className="text-xs text-gray-500">Debt Capacity</p>
            <p className="text-xl font-bold">{debtScore}</p>
            <p className="text-sm text-gray-600 mt-2">Contributors:</p>
            <ul className="text-sm text-gray-700 ml-4 list-disc">
              <li>Credit utilization: {String(creditUtil ?? 'N/A')}</li>
              <li>OCEN approval rate: {ocenApproval}%</li>
              <li>Open loans: {credit.open_loans || credit.calculation?.reports_counted || 'N/A'}</li>
            </ul>
          </div>
        </div>

        <div className="mt-4 p-3 bg-gray-50 rounded">
          <p className="text-sm">Weighted calculation:</p>
          <pre className="text-sm bg-white p-2 rounded mt-2">{methodology.explanation || `${cashflowScore}*0.45 + ${businessScore}*0.35 + ${debtScore}*0.20 = ${overall.calculated_credit_score || overall.scores?.overall_risk_score}`}</pre>
        </div>
      </section>

      <section className="bg-white rounded-lg p-4 shadow">
        <h3 className="font-semibold">Detailed Component Calculations</h3>

        <div className="mt-3 space-y-3">
          <div className="p-3 border rounded">
            <h4 className="font-medium">Cashflow Stability — Breakdown</h4>
            <p className="text-sm text-gray-600">Source: Transactions summary</p>
            <pre className="text-sm mt-2 bg-white p-2 rounded">{JSON.stringify(tx.calculation || tx, null, 2)}</pre>
          </div>

          <div className="p-3 border rounded">
            <h4 className="font-medium">Business Health — Breakdown</h4>
            <p className="text-sm text-gray-600">Sources: GST / ONDC / Mutual Funds</p>
            <pre className="text-sm mt-2 bg-white p-2 rounded">{JSON.stringify({ gst: gst.calculation || gst, ondc: ondc.calculation || ondc, mutual_funds: mf.calculation || mf }, null, 2)}</pre>
          </div>

          <div className="p-3 border rounded">
            <h4 className="font-medium">Debt Capacity — Breakdown</h4>
            <p className="text-sm text-gray-600">Sources: Credit / OCEN / Insurance</p>
            <pre className="text-sm mt-2 bg-white p-2 rounded">{JSON.stringify({ credit: credit.calculation || credit, ocen: ocen.calculation || ocen, insurance: ins.calculation || ins }, null, 2)}</pre>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CreditCalculations;
