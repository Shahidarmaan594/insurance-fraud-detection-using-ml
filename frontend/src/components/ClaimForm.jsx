import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { api } from '../api/client';
import FraudIndicator from './FraudIndicator';

const CLAIM_TYPES = ['auto', 'health', 'property', 'liability'];
const INITIAL = {
  claimant_name: '',
  claimant_age: '',
  claim_amount: '',
  claim_type: 'auto',
  policy_duration_months: '',
  previous_claims_count: 0,
  claim_description: '',
};

export default function ClaimForm({ onSuccess }) {
  const [form, setForm] = useState(INITIAL);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [claimId, setClaimId] = useState(null);

  const validate = () => {
    const e = {};
    if (!form.claimant_name?.trim()) e.claimant_name = 'Required';
    const age = parseInt(form.claimant_age, 10);
    if (isNaN(age) || age < 18 || age > 80) e.claimant_age = 'Age must be 18-80';
    const amt = parseFloat(form.claim_amount);
    if (isNaN(amt) || amt < 0 || amt > 500000) e.claim_amount = 'Amount must be 0-500000';
    const dur = parseInt(form.policy_duration_months, 10);
    if (isNaN(dur) || dur < 1 || dur > 480) e.policy_duration_months = 'Duration must be 1-480 months';
    if (!form.claim_description?.trim()) e.claim_description = 'Required';
    if (form.claim_description?.length > 1000) e.claim_description = 'Max 1000 characters';
    const prev = parseInt(form.previous_claims_count, 10);
    if (isNaN(prev) || prev < 0 || prev > 10) e.previous_claims_count = 'Must be 0-10';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
    if (errors[name]) setErrors((e) => ({ ...e, [name]: null }));
  };

  const isFormValid = () => {
    return (
      form.claimant_name?.trim() &&
      form.claimant_age && form.claim_amount && form.policy_duration_months &&
      form.claim_description?.trim() &&
      form.claim_description.length <= 1000 &&
      parseInt(form.claimant_age, 10) >= 18 &&
      parseInt(form.claimant_age, 10) <= 80 &&
      parseFloat(form.claim_amount) >= 0 &&
      parseFloat(form.claim_amount) <= 500000 &&
      parseInt(form.policy_duration_months, 10) >= 1 &&
      parseInt(form.policy_duration_months, 10) <= 480 &&
      parseInt(form.previous_claims_count || 0, 10) >= 0 &&
      parseInt(form.previous_claims_count || 0, 10) <= 10
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate() || loading) return;

    setLoading(true);
    setErrors({});
    setPrediction(null);
    setClaimId(null);

    try {
      const payload = {
        claimant_name: form.claimant_name,
        claimant_age: parseInt(form.claimant_age, 10),
        claim_amount: parseFloat(form.claim_amount),
        claim_type: form.claim_type,
        policy_duration_months: parseInt(form.policy_duration_months, 10),
        previous_claims_count: parseInt(form.previous_claims_count || 0, 10),
        claim_description: form.claim_description,
      };

      const createRes = await api.createClaim(payload);
      const id = createRes.data.claim_id;
      setClaimId(id);

      const predRes = await api.predictFraud({ ...payload, claim_id: id });
      setPrediction(predRes.data);
      onSuccess?.();
    } catch (err) {
      const msg = err.response?.data?.error || err.message;
      const errs = err.response?.data?.errors;
      setErrors(errs || { submit: msg });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setForm(INITIAL);
    setErrors({});
    setPrediction(null);
    setClaimId(null);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6">
      <h2 className="text-xl font-semibold mb-4">Submit New Claim</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Claimant Name</label>
            <input
              type="text"
              name="claimant_name"
              value={form.claimant_name}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
              placeholder="Full name"
            />
            {errors.claimant_name && <p className="text-danger text-sm mt-1">{errors.claimant_name}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Age (18-80)</label>
            <input
              type="number"
              name="claimant_age"
              value={form.claimant_age}
              onChange={handleChange}
              min={18}
              max={80}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
            />
            {errors.claimant_age && <p className="text-danger text-sm mt-1">{errors.claimant_age}</p>}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Claim Amount (0-500000)</label>
            <input
              type="number"
              name="claim_amount"
              value={form.claim_amount}
              onChange={handleChange}
              min={0}
              max={500000}
              step={0.01}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
            />
            {errors.claim_amount && <p className="text-danger text-sm mt-1">{errors.claim_amount}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Claim Type</label>
            <select
              name="claim_type"
              value={form.claim_type}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
            >
              {CLAIM_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Policy Duration (months)</label>
            <input
              type="number"
              name="policy_duration_months"
              value={form.policy_duration_months}
              onChange={handleChange}
              min={1}
              max={480}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
            />
            {errors.policy_duration_months && <p className="text-danger text-sm mt-1">{errors.policy_duration_months}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Previous Claims (0-10)</label>
            <input
              type="number"
              name="previous_claims_count"
              value={form.previous_claims_count}
              onChange={handleChange}
              min={0}
              max={10}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
            />
            {errors.previous_claims_count && <p className="text-danger text-sm mt-1">{errors.previous_claims_count}</p>}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Claim Description (max 1000 chars)</label>
          <textarea
            name="claim_description"
            value={form.claim_description}
            onChange={handleChange}
            rows={4}
            maxLength={1000}
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2"
            placeholder="Describe the incident..."
          />
          <p className="text-xs text-gray-500 mt-1">{form.claim_description?.length || 0}/1000</p>
          {errors.claim_description && <p className="text-danger text-sm mt-1">{errors.claim_description}</p>}
        </div>
        {errors.submit && <p className="text-danger text-sm">{errors.submit}</p>}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!isFormValid() || loading}
            className="px-4 py-2 bg-primary hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md flex items-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            Submit Claim
          </button>
          {prediction && (
            <button type="button" onClick={resetForm} className="px-4 py-2 border rounded-md">
              Submit Another
            </button>
          )}
        </div>
      </form>
      {prediction && (
        <div className="mt-6 pt-6 border-t dark:border-gray-600">
          <h3 className="font-medium mb-4">Fraud Prediction</h3>
          <div className="flex flex-col md:flex-row gap-6 items-center">
            <FraudIndicator
              probability={prediction.probability}
              riskLevel={prediction.risk_level}
              factors={prediction.explanation}
            />
            {claimId && (
              <p className="text-sm text-gray-500">Claim ID: {claimId}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
