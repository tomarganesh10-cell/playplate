import { useEffect, useState } from 'react';
import { api } from '../api/client.js';

export default function Signals() {
  const [signals, setSignals] = useState([]);
  const [summary, setSummary] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = () => api.signals('active').then(setSignals).catch((e) => setError(e.message));

  useEffect(() => { load(); }, []);

  const runScan = async () => {
    setBusy(true);
    setError('');
    try {
      const res = await api.scan('15m');
      setSummary(res.summary);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const trade = async (s) => {
    if (!window.confirm(`Submit ${s.side} ${s.symbol} order? (subject to risk checks & mode)`)) return;
    try {
      const r = await api.placeOrder({
        symbol: s.symbol, side: s.side, quantity: 1,
        stop_loss: s.stop_loss, target: s.target, signal_id: s.id,
      });
      alert(r.message);
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <section>
      <div className="page-head">
        <h2>Live Signals</h2>
        <button onClick={runScan} disabled={busy}>{busy ? 'Scanning…' : 'Run scan'}</button>
      </div>
      {error && <div className="error">{error}</div>}
      {summary && <div className="card summary">{summary}</div>}
      <table className="data">
        <thead>
          <tr>
            <th>#</th><th>Symbol</th><th>Side</th><th>Entry</th><th>Stop</th>
            <th>Target</th><th>R:R</th><th>Score</th><th>Conf.</th><th></th>
          </tr>
        </thead>
        <tbody>
          {signals.map((s) => (
            <tr key={s.id}>
              <td>{s.rank}</td>
              <td>{s.symbol}</td>
              <td className={s.side === 'BUY' ? 'buy' : 'sell'}>{s.side}</td>
              <td>{s.entry}</td>
              <td>{s.stop_loss}</td>
              <td>{s.target}</td>
              <td>{s.risk_reward}</td>
              <td>{s.score}</td>
              <td>{(s.confidence * 100).toFixed(0)}%</td>
              <td><button className="small" onClick={() => trade(s)}>Trade</button></td>
            </tr>
          ))}
          {signals.length === 0 && (
            <tr><td colSpan="10" className="muted">No active signals. Run a scan.</td></tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
