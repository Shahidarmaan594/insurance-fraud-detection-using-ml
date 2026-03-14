import { useState } from 'react';
import { Link } from 'react-router-dom';
import ClaimsList from '../components/ClaimsList';
import ClaimForm from '../components/ClaimForm';

export default function ClaimsPage() {
  const [showForm, setShowForm] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Claims</h1>
        <button
          onClick={() => setShowForm((f) => !f)}
          className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-md"
        >
          {showForm ? 'Hide Form' : 'New Claim'}
        </button>
      </div>

      {showForm && (
        <ClaimForm onSuccess={() => setRefreshKey((k) => k + 1)} />
      )}

      <ClaimsList key={refreshKey} />
    </div>
  );
}
