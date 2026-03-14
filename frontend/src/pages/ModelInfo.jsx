import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { FeatureImportanceChart } from '../components/ChartComponent';
import { Loader2 } from 'lucide-react';

export default function ModelInfo() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getModelInfo()
      .then((res) => setInfo(res.data))
      .catch(() => setInfo(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!info) {
    return (
      <div className="text-center py-12 text-gray-500">
        Model info not available. Run setup to train the model.
      </div>
    );
  }

  const metrics = [
    { key: 'accuracy', label: 'Accuracy' },
    { key: 'precision', label: 'Precision' },
    { key: 'recall', label: 'Recall' },
    { key: 'f1_score', label: 'F1-Score' },
    { key: 'roc_auc', label: 'ROC-AUC' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Model Information</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {metrics.map(({ key, label }) => (
          <div key={key} className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
            <p className="text-xl font-bold mt-1">
              {info[key] != null ? (typeof info[key] === 'number' ? (info[key] * 100).toFixed(2) + '%' : info[key]) : '-'}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-card p-6">
        <h2 className="font-semibold mb-4">Feature Importance (Top 10)</h2>
        <FeatureImportanceChart data={info.feature_importance} />
      </div>

      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
        {info.version && <span>Version: {info.version}</span>}
      </div>
    </div>
  );
}
