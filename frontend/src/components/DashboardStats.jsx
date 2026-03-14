import { FileText, AlertTriangle, TrendingUp, Shield } from 'lucide-react';

const statCards = [
  {
    key: 'total_claims',
    label: 'Total Claims',
    icon: FileText,
    color: 'bg-primary/10 text-primary dark:bg-primary/20',
  },
  {
    key: 'average_fraud_probability',
    label: 'Avg Fraud %',
    icon: TrendingUp,
    color: 'bg-accent/10 text-accent dark:bg-accent/20',
  },
  {
    key: 'high_risk_count',
    label: 'High Risk',
    icon: AlertTriangle,
    color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  },
  {
    key: 'fraud_rate',
    label: 'Fraud Rate %',
    icon: Shield,
    color: 'bg-success/10 text-success dark:bg-green-900/30 dark:text-green-400',
  },
];

export default function DashboardStats({ stats }) {
  if (!stats) return null;

  const formatValue = (key, val) => {
    if (val == null) return '0';
    if (key === 'average_fraud_probability' || key === 'fraud_rate')
      return typeof val === 'number' ? val.toFixed(1) : val;
    return Number(val).toLocaleString();
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map(({ key, label, icon: Icon, color }) => (
        <div
          key={key}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-5 hover:shadow-card-hover transition"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-2xl font-bold mt-1">
                {formatValue(key, stats[key])}
                {(key === 'average_fraud_probability' || key === 'fraud_rate') && '%'}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${color}`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
