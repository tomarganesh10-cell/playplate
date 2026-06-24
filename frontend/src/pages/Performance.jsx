import { useEffect, useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { api } from '../api/client.js';

export default function Performance() {
  const [perf, setPerf] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.performance(30).then(setPerf).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!perf) return <div className="muted">Loading…</div>;

  const metrics = [
    { label: 'Total Trades', value: perf.total_trades },
    { label: 'Win Rate', value: `${(perf.win_rate * 100).toFixed(1)}%` },
    { label: 'Net PnL', value: `₹${perf.total_pnl.toLocaleString()}`, pnl: perf.total_pnl },
    { label: 'Profit Factor', value: perf.profit_factor },
    { label: 'Sharpe Ratio', value: perf.sharpe_ratio },
    { label: 'Max Drawdown', value: `${perf.max_drawdown_pct}%` },
    { label: 'Avg Win', value: `₹${perf.avg_win}` },
    { label: 'Avg Loss', value: `₹${perf.avg_loss}` },
  ];

  const chartData = [
    { name: 'Avg Win', value: perf.avg_win },
    { name: 'Avg Loss', value: perf.avg_loss },
    { name: 'Net PnL', value: perf.total_pnl },
  ];

  return (
    <section>
      <h2>Performance Analytics (30d)</h2>
      <div className="stat-grid">
        {metrics.map((m) => (
          <div className="card stat" key={m.label}>
            <span className="stat-label">{m.label}</span>
            <span className={`stat-value ${m.pnl != null ? (m.pnl >= 0 ? 'buy' : 'sell') : ''}`}>
              {m.value}
            </span>
          </div>
        ))}
      </div>
      <div className="card" style={{ height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3142" />
            <XAxis dataKey="name" stroke="#8a94a6" />
            <YAxis stroke="#8a94a6" />
            <Tooltip />
            <Bar dataKey="value" fill="#4c8bf5" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="fineprint">
        Past performance does not guarantee future results. Metrics are computed from recorded
        trades (including paper trades).
      </p>
    </section>
  );
}
