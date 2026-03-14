import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { api } from '../api/client';

const RISK_CLASS = {
  low: 'risk-low',
  medium: 'risk-medium',
  high: 'risk-high',
  critical: 'risk-critical',
};

export default function ClaimsList() {
  const [claims, setClaims] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const res = await api.getClaims({
        page,
        per_page: 10,
        search: search || undefined,
        claim_type: filterType || undefined,
        status: filterStatus || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setClaims(res.data.claims || []);
      setTotal(res.data.total || 0);
      setPages(res.data.pages || 1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims();
  }, [page, filterType, filterStatus, sortBy, sortOrder]);

  useEffect(() => {
    const t = setTimeout(() => fetchClaims(), 300);
    return () => clearTimeout(t);
  }, [search]);

  const formatDate = (d) => {
    if (!d) return '-';
    const s = typeof d === 'string' ? d : d?.isoformat?.() || '';
    return s.split('T')[0];
  };
  const formatAmount = (a) => (a != null ? `$${Number(a).toLocaleString()}` : '-');

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <h2 className="text-xl font-semibold">Claims</h2>
        <div className="flex flex-wrap gap-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search name or ID"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-2 rounded-md border dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
            className="rounded-md border dark:bg-gray-700 dark:border-gray-600 px-3 py-2"
          >
            <option value="">All Types</option>
            {['auto', 'health', 'property', 'liability'].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={(e) => { setFilterStatus(e.target.value); setPage(1); }}
            className="rounded-md border dark:bg-gray-700 dark:border-gray-600 px-3 py-2"
          >
            <option value="">All Status</option>
            {['pending', 'approved', 'rejected', 'fraud'].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-md border dark:bg-gray-700 dark:border-gray-600 px-3 py-2"
          >
            <option value="date">Date</option>
            <option value="amount">Amount</option>
            <option value="risk_level">Risk Level</option>
          </select>
          <button
            onClick={() => setSortOrder((o) => (o === 'desc' ? 'asc' : 'desc'))}
            className="px-3 py-2 rounded-md border dark:border-gray-600"
          >
            {sortOrder === 'desc' ? '↓ Desc' : '↑ Asc'}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card overflow-x-auto">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : claims.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No claims found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="text-left px-4 py-3">Claim ID</th>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Amount</th>
                <th className="text-left px-4 py-3">Type</th>
                <th className="text-left px-4 py-3">Risk</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Date</th>
                <th className="text-left px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((c) => (
                <tr key={c.claim_id} className="border-t dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-4 py-3 font-mono text-sm">{c.claim_id}</td>
                  <td className="px-4 py-3">{c.claimant_name}</td>
                  <td className="px-4 py-3">{formatAmount(c.claim_amount)}</td>
                  <td className="px-4 py-3 capitalize">{c.claim_type}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${RISK_CLASS[c.risk_level] || 'risk-low'}`}>
                      {c.fraud_probability != null ? `${c.fraud_probability.toFixed(0)}%` : '-'} {c.risk_level || ''}
                    </span>
                  </td>
                  <td className="px-4 py-3 capitalize">{c.status}</td>
                  <td className="px-4 py-3">{formatDate(c.submission_date || c.created_at)}</td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/claims/${c.claim_id}`}
                      className="inline-flex items-center gap-1 text-primary hover:underline"
                    >
                      <Eye className="w-4 h-4" /> View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t dark:border-gray-600">
            <p className="text-sm text-gray-500">
              Page {page} of {pages} ({total} total)
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-2 rounded border disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(pages, p + 1))}
                disabled={page >= pages}
                className="p-2 rounded border disabled:opacity-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
