import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import DashboardStats from '../components/DashboardStats';
import ClaimForm from '../components/ClaimForm';
import {
  ClaimsOverTimeChart,
  FraudByTypeChart,
  StatusDonutChart,
} from '../components/ChartComponent';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const res = await api.getStatistics();
      setStats(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const byMonth = stats?.by_month || [];
  const byType = stats?.by_type || [];
  const statusDonut = stats?.by_status || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link to="/claims" className="text-primary hover:underline">
          View all claims →
        </Link>
      </div>

      {loading ? (
        <div className="animate-pulse h-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      ) : (
        <DashboardStats stats={stats} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6">
          <h2 className="font-semibold mb-4">Claims Over Time</h2>
          <ClaimsOverTimeChart data={byMonth} />
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6">
          <h2 className="font-semibold mb-4">Claims by Type</h2>
          <FraudByTypeChart data={byType} />
        </div>
      </div>

      {statusDonut.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6 max-w-md">
          <h2 className="font-semibold mb-4">Status Distribution</h2>
          <StatusDonutChart data={statusDonut} />
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold mb-4">Submit New Claim</h2>
        <ClaimForm onSuccess={fetchStats} />
      </div>
    </div>
  );
}
