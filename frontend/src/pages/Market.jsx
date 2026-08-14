import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client.js';

const fmt = (n) =>
  n == null ? '—' : Number(n).toLocaleString('en-IN', { maximumFractionDigits: 2 });

function SourceBadge({ source }) {
  const live = source === 'zerodha';
  return (
    <span className={`src-badge ${live ? 'src-live' : 'src-demo'}`}>
      {live ? '● LIVE · Zerodha' : '● DEMO DATA (connect Zerodha for real rates)'}
    </span>
  );
}

function MoversTable({ title, rows, positive }) {
  return (
    <div className="card movers-card">
      <h3 className={positive ? 'buy' : 'sell'}>{title}</h3>
      <table className="data">
        <thead>
          <tr><th>Symbol</th><th>LTP</th><th>Chg%</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.symbol}>
              <td className="sym">{r.symbol}</td>
              <td>{fmt(r.last_price)}</td>
              <td className={r.change_pct >= 0 ? 'buy' : 'sell'}>
                {r.change_pct >= 0 ? '+' : ''}{fmt(r.change_pct)}%
              </td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr><td colSpan="3" className="muted">No data yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default function Market() {
  const [indices, setIndices] = useState(null);
  const [movers, setMovers] = useState(null);
  const [news, setNews] = useState(null);
  const [error, setError] = useState('');

  const loadQuotes = useCallback(() => {
    api.indices().then(setIndices).catch((e) => setError(e.message));
    api.movers().then(setMovers).catch((e) => setError(e.message));
  }, []);

  const loadNews = useCallback(() => {
    api.news().then(setNews).catch(() => {});
  }, []);

  useEffect(() => {
    loadQuotes();
    loadNews();
    const qt = setInterval(loadQuotes, 30_000);
    const nt = setInterval(loadNews, 300_000);
    return () => { clearInterval(qt); clearInterval(nt); };
  }, [loadQuotes, loadNews]);

  return (
    <section>
      <div className="page-head">
        <h2>Market Watch</h2>
        {indices && <SourceBadge source={indices.data_source} />}
      </div>
      {error && <div className="error">{error}</div>}

      <div className="ticker-strip">
        {(indices?.rates || []).map((r) => (
          <div className="idx-card" key={r.index}>
            <span className="idx-name">{r.index}</span>
            <span className="idx-price">{r.error ? '—' : fmt(r.last_price)}</span>
          </div>
        ))}
        {!indices && <div className="muted">Loading indices…</div>}
      </div>

      <div className="movers-grid">
        <MoversTable title="Top Gainers" rows={movers?.gainers || []} positive />
        <MoversTable title="Top Losers" rows={movers?.losers || []} positive={false} />
      </div>

      <div className="card news-card">
        <h3>Market News</h3>
        {!news && <div className="muted">Loading headlines…</div>}
        {news && news.items.length === 0 && (
          <div className="muted">No headlines available right now.</div>
        )}
        <ul className="news-list">
          {(news?.items || []).map((n, i) => (
            <li key={i}>
              <a href={n.link} target="_blank" rel="noreferrer">{n.title}</a>
              <span className="news-meta">{n.source}{n.published ? ` · ${n.published}` : ''}</span>
            </li>
          ))}
        </ul>
        {news && <p className="fineprint">{news.note}</p>}
      </div>
    </section>
  );
}
