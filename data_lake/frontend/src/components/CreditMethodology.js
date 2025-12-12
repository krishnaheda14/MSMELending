import React from 'react';
import { BookOpen, TrendingUp, DollarSign, Shield, ShoppingCart, LineChart, AlertTriangle } from 'lucide-react';

const CreditMethodology = () => {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl p-6">
        <h2 className="text-3xl font-bold mb-2">Credit Assessment Methodology</h2>
        <p className="text-purple-100">
          Comprehensive framework for evaluating MSME creditworthiness using alternative data sources
        </p>
      </div>

      {/* Credit Score Components */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <LineChart className="w-6 h-6 mr-2 text-blue-600" />
          Credit Score Components
        </h3>
        
        <div className="space-y-6">
          {/* Cashflow Stability - 45% */}
          <div className="border-l-4 border-blue-500 pl-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xl font-semibold text-gray-800">Cashflow Stability (45% weight)</h4>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">Highest Priority</span>
            </div>
            <p className="text-gray-700 mb-3">
              Measures the consistency and predictability of cash inflows and outflows over time.
            </p>
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="font-semibold text-gray-800 mb-2">Key Metrics:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                <li><strong>Transaction Volume Consistency:</strong> Monthly variance in transaction count (lower variance = higher score)</li>
                <li><strong>Income/Expense Ratio:</strong> Average monthly income divided by average monthly expenses (ideal: &gt;1.2)</li>
                <li><strong>Monthly Variance:</strong> Standard deviation of monthly cashflows (lower = more stable)</li>
                <li><strong>Positive Balance Days:</strong> Percentage of days with positive account balance</li>
              </ul>
              <p className="text-sm text-gray-600 mt-3 italic">
                <strong>Realistic Benchmark:</strong> Score ≥75 indicates very stable cashflows; 60-74 is moderately stable; &lt;60 suggests volatility requiring deeper review.
              </p>
            </div>
          </div>

          {/* Business Health - 35% */}
          <div className="border-l-4 border-green-500 pl-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xl font-semibold text-gray-800">Business Health (35% weight)</h4>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">High Priority</span>
            </div>
            <p className="text-gray-700 mb-3">
              Evaluates the operational strength, compliance, and growth trajectory of the business.
            </p>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="font-semibold text-gray-800 mb-2">Key Metrics:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                <li><strong>GST Compliance Score:</strong> Timely filing rate × average turnover per return (higher = better)</li>
                <li><strong>ONDC Order Diversity:</strong> Number of unique providers × average order value (multi-channel capability)</li>
                <li><strong>State/Geographic Diversification:</strong> Number of states with active GST presence or ONDC deliveries</li>
                <li><strong>Revenue Trends:</strong> Year-over-year growth in GST turnover or transaction volume</li>
                <li><strong>Mutual Fund Investments:</strong> Presence of MF portfolios indicates financial discipline and surplus capital</li>
              </ul>
              <p className="text-sm text-gray-600 mt-3 italic">
                <strong>Realistic Benchmark:</strong> Score ≥80 indicates strong business fundamentals; 65-79 is acceptable; &lt;65 requires mitigation plans.
              </p>
            </div>
          </div>

          {/* Debt Capacity - 20% */}
          <div className="border-l-4 border-orange-500 pl-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xl font-semibold text-gray-800">Debt Capacity (20% weight)</h4>
              <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold">Moderate Priority</span>
            </div>
            <p className="text-gray-700 mb-3">
              Assesses the borrower's ability to service additional debt without over-leveraging.
            </p>
            <div className="bg-orange-50 rounded-lg p-4">
              <p className="font-semibold text-gray-800 mb-2">Key Metrics:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                <li><strong>Credit Utilization:</strong> Existing loan balances ÷ total available credit (ideal: &lt;50%)</li>
                <li><strong>OCEN Approval Rate:</strong> (Approved amount ÷ Requested amount) × 100 — low approval rate (&lt;30%) is a red flag</li>
                <li><strong>Insurance Coverage Ratio:</strong> Total sum assured ÷ annual business revenue (higher = better risk management)</li>
                <li><strong>Loan-to-Income Ratio:</strong> Total monthly loan EMIs ÷ average monthly income (ideal: &lt;40%)</li>
                <li><strong>Debt Service Coverage Ratio (DSCR):</strong> Net operating income ÷ total debt obligations (must be &gt;1.25)</li>
              </ul>
              <p className="text-sm text-gray-600 mt-3 italic">
                <strong>Realistic Benchmark:</strong> Score ≥70 indicates healthy debt capacity; 50-69 is acceptable with conditions; &lt;50 suggests over-leverage.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Composite Score Formula */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <TrendingUp className="w-6 h-6 mr-2 text-purple-600" />
          Composite Credit Score Calculation
        </h3>
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border-2 border-purple-200">
          <p className="text-lg font-mono font-semibold text-gray-800 mb-4">
            Credit Score = (0.45 × Cashflow Stability) + (0.35 × Business Health) + (0.20 × Debt Capacity)
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-sm text-gray-600">Cashflow Weight</p>
              <p className="text-3xl font-bold text-blue-700">45%</p>
              <p className="text-xs text-gray-500 mt-1">Most critical factor</p>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-sm text-gray-600">Business Weight</p>
              <p className="text-3xl font-bold text-green-700">35%</p>
              <p className="text-xs text-gray-500 mt-1">Strong indicator</p>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-sm text-gray-600">Debt Weight</p>
              <p className="text-3xl font-bold text-orange-700">20%</p>
              <p className="text-xs text-gray-500 mt-1">Contextual factor</p>
            </div>
          </div>
          <div className="mt-6 border-t border-gray-300 pt-4">
            <p className="font-semibold text-gray-800 mb-2">Score Interpretation:</p>
            <div className="space-y-2">
              <div className="flex items-center">
                <div className="w-24 text-sm font-semibold text-gray-700">75 – 100:</div>
                <div className="flex-1 bg-green-100 rounded px-3 py-1 text-green-800 font-semibold">✓ APPROVE — Strong creditworthiness</div>
              </div>
              <div className="flex items-center">
                <div className="w-24 text-sm font-semibold text-gray-700">60 – 74:</div>
                <div className="flex-1 bg-yellow-100 rounded px-3 py-1 text-yellow-800 font-semibold">⚠ REVIEW — Acceptable with conditions or collateral</div>
              </div>
              <div className="flex items-center">
                <div className="w-24 text-sm font-semibold text-gray-700">Below 60:</div>
                <div className="flex-1 bg-red-100 rounded px-3 py-1 text-red-800 font-semibold">✗ CAUTION — High risk; require additional guarantees or decline</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alternative Data Sources */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <BookOpen className="w-6 h-6 mr-2 text-indigo-600" />
          Alternative Data Sources Explained
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* ONDC */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-3">
              <ShoppingCart className="w-8 h-8 text-pink-600 mr-3" />
              <h4 className="text-lg font-semibold text-gray-800">ONDC (Open Network for Digital Commerce)</h4>
            </div>
            <p className="text-gray-700 text-sm mb-2">
              Order data from India's unified digital commerce network.
            </p>
            <p className="font-semibold text-sm text-gray-800 mb-1">Credit Insights:</p>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              <li><strong>High order volumes</strong> indicate active customer engagement and revenue generation</li>
              <li><strong>Provider diversity</strong> (multi-channel sales) suggests business resilience</li>
              <li><strong>Consistent average order value</strong> shows stable demand</li>
              <li><strong>Geographic reach</strong> (multiple states) reduces concentration risk</li>
            </ul>
            <p className="text-xs text-gray-600 mt-2 italic">
              Red flag: Very low order volumes (&lt;100/month) or single-provider dependency
            </p>
          </div>

          {/* OCEN */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-3">
              <DollarSign className="w-8 h-8 text-purple-600 mr-3" />
              <h4 className="text-lg font-semibold text-gray-800">OCEN (Open Credit Enablement Network)</h4>
            </div>
            <p className="text-gray-700 text-sm mb-2">
              Digital loan application history across multiple lenders.
            </p>
            <p className="font-semibold text-sm text-gray-800 mb-1">Credit Insights:</p>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              <li><strong>Approval rate &lt;30%</strong> is a major red flag (indicates high-risk profile or poor documentation)</li>
              <li><strong>Multiple rejections</strong> suggest credit hunger or weak fundamentals</li>
              <li><strong>Approved amounts &gt; requested</strong> indicate lender confidence</li>
              <li><strong>Timely repayment status</strong> (if available) validates reliability</li>
            </ul>
            <p className="text-xs text-gray-600 mt-2 italic">
              Red flag: Approval rate &lt;20% or excessive application frequency (&gt;10 apps/month)
            </p>
          </div>

          {/* Mutual Funds */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-3">
              <LineChart className="w-8 h-8 text-green-600 mr-3" />
              <h4 className="text-lg font-semibold text-gray-800">Mutual Fund Investments</h4>
            </div>
            <p className="text-gray-700 text-sm mb-2">
              Portfolio holdings and returns from registered mutual funds.
            </p>
            <p className="font-semibold text-sm text-gray-800 mb-1">Credit Insights:</p>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              <li><strong>Presence of MF portfolios</strong> demonstrates financial discipline and surplus capital</li>
              <li><strong>Positive returns</strong> suggest sound investment decisions</li>
              <li><strong>Diversified schemes</strong> (equity, debt, hybrid) indicate risk awareness</li>
              <li><strong>Long-term holdings</strong> show financial stability and planning</li>
            </ul>
            <p className="text-xs text-gray-600 mt-2 italic">
              Positive signal: MF investments ≥ 10% of annual business revenue
            </p>
          </div>

          {/* Insurance */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-3">
              <Shield className="w-8 h-8 text-blue-600 mr-3" />
              <h4 className="text-lg font-semibold text-gray-800">Insurance Coverage</h4>
            </div>
            <p className="text-gray-700 text-sm mb-2">
              Life, health, property, and business insurance policies.
            </p>
            <p className="font-semibold text-sm text-gray-800 mb-1">Credit Insights:</p>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              <li><strong>Adequate coverage</strong> (sum assured ≥ 2× annual revenue) protects against business disruptions</li>
              <li><strong>Active policies</strong> show proactive risk management</li>
              <li><strong>Premium payment regularity</strong> validates cash discipline</li>
              <li><strong>Diverse policy types</strong> (life + property + liability) indicate comprehensive protection</li>
            </ul>
            <p className="text-xs text-gray-600 mt-2 italic">
              Red flag: No active insurance or lapsed policies due to non-payment
            </p>
          </div>
        </div>
      </div>

      {/* Risk Flags */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <AlertTriangle className="w-6 h-6 mr-2 text-red-600" />
          Critical Risk Flags
        </h3>
        <div className="space-y-3">
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="font-semibold text-red-800 mb-1">🚩 OCEN Approval Rate &lt; 30%</p>
            <p className="text-sm text-red-700">Indicates multiple lenders have rejected or reduced loan requests — requires deep dive into credit history and financials.</p>
          </div>
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="font-semibold text-red-800 mb-1">🚩 Cashflow Volatility (Variance &gt; 50%)</p>
            <p className="text-sm text-red-700">Unstable income/expense patterns suggest seasonal business or operational challenges — verify with GST returns and ONDC trends.</p>
          </div>
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="font-semibold text-red-800 mb-1">🚩 Single-Provider Dependency (ONDC)</p>
            <p className="text-sm text-red-700">&gt;80% of orders from one provider indicates platform lock-in — business is vulnerable to policy changes or platform shutdowns.</p>
          </div>
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="font-semibold text-red-800 mb-1">🚩 Zero GST Compliance or Missing Returns</p>
            <p className="text-sm text-red-700">Non-filing or irregular GST returns signal poor record-keeping or tax evasion — immediate disqualification unless resolved.</p>
          </div>
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="font-semibold text-red-800 mb-1">🚩 Credit Utilization &gt; 75%</p>
            <p className="text-sm text-red-700">High existing debt relative to limits suggests over-leverage — new loan may push borrower into distress.</p>
          </div>
        </div>
      </div>

      {/* Footer Note */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
        <p className="text-sm text-gray-700">
          <strong>Methodology Note:</strong> This credit assessment framework combines traditional financial metrics with alternative data sources (ONDC, OCEN, Mutual Funds, Insurance) to provide a holistic view of MSME creditworthiness. The composite score is designed to balance cashflow stability (most critical), business health (operational strength), and debt capacity (leverage assessment). All thresholds and weights are calibrated based on MSME lending best practices in the Indian market.
        </p>
      </div>
    </div>
  );
};

export default CreditMethodology;
