import { useMemo } from 'react';

const RISK_STYLES = {
  low: { color: 'stroke-success', bg: 'text-success', label: 'Low Risk' },
  medium: { color: 'stroke-yellow-500', bg: 'text-yellow-600 dark:text-yellow-400', label: 'Medium Risk' },
  high: { color: 'stroke-orange-500', bg: 'text-orange-600 dark:text-orange-400', label: 'High Risk' },
  critical: { color: 'stroke-danger', bg: 'text-danger', label: 'Critical Risk' },
};

export default function FraudIndicator({ probability, riskLevel, factors = [], size = 180 }) {
  const p = Math.min(100, Math.max(0, Number(probability) || 0));
  const style = RISK_STYLES[riskLevel] || RISK_STYLES.low;
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDash = (p / 100) * circumference;

  const topFactors = useMemo(() => {
    if (!factors || !Array.isArray(factors)) return [];
    return (Array.isArray(factors.factors_increasing_risk)
      ? factors.factors_increasing_risk
      : Object.entries(factors).slice(0, 3)
    ).slice(0, 3);
  }, [factors]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="12"
            className="text-gray-200 dark:text-gray-700"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - strokeDash}
            className={`${style.color} transition-all duration-500`}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${style.bg}`}>{p.toFixed(1)}%</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">{style.label}</span>
        </div>
      </div>
      {topFactors.length > 0 && (
        <div className="mt-4 text-left w-full max-w-xs">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Top suspicious factors:</p>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            {topFactors.map((f, i) => (
              <li key={i}>
                • {typeof f === 'object' ? f.factor || f.name : f}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
