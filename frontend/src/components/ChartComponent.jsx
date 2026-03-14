import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const COLORS = ['#1e3a8a', '#b8860b', '#059669', '#dc2626', '#6b7280'];

export function ClaimsOverTimeChart({ data }) {
  if (!data?.length) return <EmptyChart />;
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
        <XAxis dataKey="month" stroke="currentColor" className="text-xs" />
        <YAxis stroke="currentColor" className="text-xs" />
        <Tooltip
          contentStyle={{ backgroundColor: 'var(--tw-bg-opacity)', borderRadius: '0.5rem' }}
          labelStyle={{ color: 'inherit' }}
        />
        <Legend />
        <Line type="monotone" dataKey="count" name="Claims" stroke="#1e3a8a" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function FraudByTypeChart({ data }) {
  if (!data?.length) return <EmptyChart />;
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 60 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
        <XAxis type="number" stroke="currentColor" />
        <YAxis type="category" dataKey="claim_type" stroke="currentColor" width={50} />
        <Tooltip />
        <Bar dataKey="count" fill="#b8860b" name="Claims" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function StatusDonutChart({ data }) {
  if (!data?.length) return <EmptyChart />;
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="count"
          nameKey="status"
          label={({ status, count }) => `${status}: ${count}`}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function FeatureImportanceChart({ data }) {
  if (!data || typeof data !== 'object') return <EmptyChart />;
  const arr = Object.entries(data)
    .slice(0, 10)
    .map(([name, value]) => ({ name: name.replace(/_/g, ' '), value: Math.round(Number(value) * 10000) / 100 }));
  if (!arr.length) return <EmptyChart />;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={arr} layout="vertical" margin={{ left: 80 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
        <XAxis type="number" domain={[0, 100]} stroke="currentColor" />
        <YAxis type="category" dataKey="name" stroke="currentColor" width={70} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v) => `${v}%`} />
        <Bar dataKey="value" fill="#1e3a8a" name="Importance %" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function EmptyChart() {
  return (
    <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm">
      No data available
    </div>
  );
}
