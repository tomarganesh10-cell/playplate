import { useEffect, useState } from 'react';
import { api } from '../api/client.js';

const TOKEN_KEY = 'pp_kite_request_token';

export default function Broker() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);
  const [diag, setDiag] = useState(null);
  const [diagBusy, setDiagBusy] = useState(false);
  const pendingToken = sessionStorage.getItem(TOKEN_KEY);

  const runDiagnostics = async () => {
    setDiagBusy(true);
    setError('');
    try {
      setDiag(await api.brokerDiagnostics());
    } catch (e) {
      setError(e.message);
    } finally {
      setDiagBusy(false);
    }
  };

  const load = () => api.brokerStatus().then(setStatus).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const startLogin = async () => {
    setError('');
    try {
      const r = await api.brokerLoginUrl();
      window.location.href = r.login_url; // Kite redirects back with ?request_token=...
    } catch (e) {
      setError(e.message);
    }
  };

  const completeConnection = async () => {
    setBusy(true);
    setError('');
    try {
      const r = await api.brokerSession(pendingToken);
      sessionStorage.removeItem(TOKEN_KEY);
      setMsg(`Zerodha connected ✓ (issued ${new Date(r.issued_at).toLocaleTimeString()})`);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section>
      <h2>Broker Connection (Zerodha)</h2>
      {error && <div className="error">{error}</div>}
      {msg && <div className="card summary">{msg}</div>}

      {status && (
        <div className="stat-grid">
          <div className="card stat">
            <span className="stat-label">Trading mode</span>
            <span className="stat-value">{status.trading_mode}</span>
          </div>
          <div className="card stat">
            <span className="stat-label">Kite session</span>
            <span className={`stat-value ${status.session_present ? 'buy' : 'sell'}`}>
              {status.session_present ? 'CONNECTED' : 'NOT CONNECTED'}
            </span>
          </div>
          <div className="card stat">
            <span className="stat-label">Live trading armed</span>
            <span className={`stat-value ${status.live_trading_armed ? 'sell' : 'buy'}`}>
              {status.live_trading_armed ? 'YES' : 'NO (safe)'}
            </span>
          </div>
        </div>
      )}

      {pendingToken ? (
        <div className="card">
          <p>
            Kite login detected — a request token is ready. Complete the connection to
            store today&apos;s session (encrypted).
          </p>
          <button onClick={completeConnection} disabled={busy}>
            {busy ? 'Connecting…' : 'Complete Zerodha connection'}
          </button>
        </div>
      ) : (
        <div className="card">
          <p>
            Kite access tokens expire daily. Log in once every trading morning; after
            login Kite redirects back here and the connection completes.
          </p>
          <button onClick={startLogin}>Login with Kite</button>
          <p className="fineprint">
            Requires the Kite app&apos;s Redirect URL to be set to
            {' '}<code>https://trading.playplate.in/broker/callback</code>.
            Only admins can connect the broker.
          </p>
        </div>
      )}

      <div className="card">
        <h3>Data access check</h3>
        <p className="fineprint">
          Logging in and receiving market data are entitled separately by Zerodha.
          Run this to see exactly which Kite capabilities your app can use.
        </p>
        <button onClick={runDiagnostics} disabled={diagBusy}>
          {diagBusy ? 'Checking…' : 'Run data access check'}
        </button>
        {diag && (
          <>
            <table className="data">
              <thead><tr><th>Capability</th><th>Status</th></tr></thead>
              <tbody>
                {Object.entries(diag.checks).map(([name, r]) => (
                  <tr key={name}>
                    <td>{name}</td>
                    <td className={r.ok ? 'buy' : 'sell'}>{r.ok ? 'OK' : r.error}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="notice">{diag.hint}</p>
          </>
        )}
      </div>
    </section>
  );
}
