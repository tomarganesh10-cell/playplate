import { useEffect, useState } from 'react';
import { api } from '../api/client.js';

export default function Portfolio() {
  const [p, setP] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.portfolio().then(setP).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!p) return <div className="muted">Loading…</div>;

  const cards = [
    { label: 'Capital', value: `₹${p.capital.toLocaleString()}` },
    { label: 'Cash', value: `₹${p.cash.toLocaleString()}` },
    { label: 'Invested', value: `₹${p.invested.toLocaleString()}` },
    { label: 'Exposure', value: `₹${p.exposure.toLocaleString()}` },
    { label: 'Realised PnL (today)', value: `₹${p.realised_pnl_today.toLocaleString()}`, pnl: p.realised_pnl_today },
    { label: 'Unrealised PnL', value: `₹${p.unrealised_pnl.toLocaleString()}`, pnl: p.unrealised_pnl },
  ];

  return (
    <section>
      <h2>Portfolio</h2>
      <div className="stat-grid">
        {cards.map((c) => (
          <div className="card stat" key={c.label}>
            <span className="stat-label">{c.label}</span>
            <span className={`stat-value ${c.pnl != null ? (c.pnl >= 0 ? 'buy' : 'sell') : ''}`}>
              {c.value}
            </span>
          </div>
        ))}
      </div>
      <h3>Open Positions</h3>
      <table className="data">
        <thead>
          <tr><th>Symbol</th><th>Qty</th><th>Avg</th><th>Last</th><th>Unrealised PnL</th></tr>
        </thead>
        <tbody>
          {p.open_positions.map((pos) => (
            <tr key={pos.symbol}>
              <td>{pos.symbol}</td>
              <td>{pos.quantity}</td>
              <td>{pos.avg_price}</td>
              <td>{pos.last_price}</td>
              <td className={pos.unrealised_pnl >= 0 ? 'buy' : 'sell'}>{pos.unrealised_pnl}</td>
            </tr>
          ))}
          {p.open_positions.length === 0 && (
            <tr><td colSpan="5" className="muted">No open positions.</td></tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
