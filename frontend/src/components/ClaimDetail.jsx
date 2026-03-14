import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { api } from '../api/client';
import FraudIndicator from './FraudIndicator';
import { FeatureImportanceChart } from './ChartComponent';

export default function ClaimDetail() {
  const { claimId } = useParams();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [status, setStatus] = useState('');

  useEffect(() => {
    if (!claimId) return;
    setLoading(true);
    api
      .getClaim(claimId)
      .then((res) => {
        setClaim(res.data);
        setStatus(res.data.status || '');
      })
      .catch(() => setClaim(null))
      .finally(() => setLoading(false));
  }, [claimId]);

  const handleStatusUpdate = async () => {
    if (!claimId || status === claim?.status) return;
    setUpdating(true);
    try {
      const res = await api.updateClaimStatus(claimId, status);
      setClaim((c) => (c ? { ...c, ...res.data } : c));
    } catch (e) {
      console.error(e);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }
  if (!claim) {
    return <div className="text-center py-12 text-gray-500">Claim not found</div>;
  }

  const pred = claim.prediction;
  const fi = pred?.feature_importance || (typeof pred?.feature_importance_json === 'string'
    ? (() => { try { return JSON.parse(pred.feature_importance_json); } catch { return {}; } })()
    : {});

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Claim {claim.claim_id}</h1>
        <div className="flex items-center gap-2">
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="rounded-md border dark:bg-gray-700 dark:border-gray-600 px-3 py-2"
          >
            {['pending', 'approved', 'rejected', 'fraud'].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button
            onClick={handleStatusUpdate}
            disabled={updating || status === claim.status}
            className="px-4 py-2 bg-primary text-white rounded-md disabled:opacity-50"
          >
            {updating ? <Loader2 className="w-4 h-4 animate-spin inline" /> : 'Update'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6">
            <h2 className="font-semibold mb-4">Claim Details</h2>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <dt className="text-gray-500">Claimant</dt>
              <dd>{claim.claimant_name}</dd>
              <dt className="text-gray-500">Age</dt>
              <dd>{claim.claimant_age}</dd>
              <dt className="text-gray-500">Amount</dt>
              <dd>${Number(claim.claim_amount).toLocaleString()}</dd>
              <dt className="text-gray-500">Type</dt>
              <dd className="capitalize">{claim.claim_type}</dd>
              <dt className="text-gray-500">Policy Duration</dt>
              <dd>{claim.policy_duration_months} months</dd>
              <dt className="text-gray-500">Previous Claims</dt>
              <dd>{claim.previous_claims_count}</dd>
              <dt className="text-gray-500">Submission Date</dt>
              <dd>{claim.submission_date || '-'}</dd>
              <dt className="text-gray-500">Status</dt>
              <dd className="capitalize">{claim.status}</dd>
            </dl>
            <div className="mt-4">
              <dt className="text-gray-500 text-sm">Description</dt>
              <dd className="mt-1">{claim.claim_description}</dd>
            </div>
          </div>
          {pred && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6">
              <h2 className="font-semibold mb-4">Feature Importance</h2>
              <FeatureImportanceChart data={fi} />
            </div>
          )}
        </div>
        <div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6 sticky top-4">
            <h2 className="font-semibold mb-4">Fraud Risk</h2>
            {pred ? (
              <>
                <FraudIndicator
                  probability={pred.fraud_probability}
                  riskLevel={pred.risk_level}
                  factors={pred.explanation || pred}
                  size={200}
                />
                <div className="mt-4 text-sm text-gray-500 space-y-1">
                  {pred.predicted_at && <p>Predicted: {new Date(pred.predicted_at).toLocaleString()}</p>}
                  {pred.model_version && <p>Model: v{pred.model_version}</p>}
                </div>
              </>
            ) : (
              <p className="text-gray-500">No prediction yet. Submit for analysis from the Submit Claim form.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
