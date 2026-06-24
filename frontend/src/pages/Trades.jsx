import { useEffect, useState } from 'react';
import { api } from '../api/client.js';

export default function Trades() {
  const [trades, setTrades] = useState([]);
  const [error, setError] = useState('');

  const load = () => api.trades('all').then(setTrades).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const close = async (id) => {
    if (!window.confirm('Close this trade at market?')) return;
    try {
      await api.closeTrade(id);
      await load();
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <section>
      <h2>Trade History</h2>
      {error && <div className="error">{error}</div>}
      <table className="data">
        <thead>
          <tr>
            <th>ID</th><th>Symbol</th><th>Side</th><th>Mode</th><th>Qty</th>
            <th>Entry</th><th>Exit</th><th>PnL</th><th>Status</th><th>Opened</th><th></th>
          </tr>
        </thead>
        <tbody>
          {trades.map((t) => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>{t.symbol}</td>
              <td className={t.side === 'BUY' ? 'buy' : 'sell'}>{t.side}</td>
              <td>{t.mode}</td>
              <td>{t.quantity}</td>
              <td>{t.entry_price}</td>
              <td>{t.exit_price ?? '—'}</td>
              <td className={t.pnl >= 0 ? 'buy' : 'sell'}>{t.pnl}</td>
              <td>{t.status}</td>
              <td>{new Date(t.opened_at).toLocaleString()}</td>
              <td>{t.status === 'open' && <button className="small" onClick={() => close(t.id)}>Close</button>}</td>
            </tr>
          ))}
          {trades.length === 0 && <tr><td colSpan="11" className="muted">No trades yet.</td></tr>}
        </tbody>
      </table>
    </section>
  );
}
