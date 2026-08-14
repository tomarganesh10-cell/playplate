import { useEffect, useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext.jsx';
import { api } from '../api/client.js';

const NAV = [
  { to: '/market', label: 'Market Watch' },
  { to: '/signals', label: 'Live Signals' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/trades', label: 'Trade History' },
  { to: '/performance', label: 'Performance' },
  { to: '/broker', label: 'Broker' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
  }, []);

  return (
    <div className="app">
      <aside className="sidebar">
        <h1 className="brand">Trading<br />Playplate</h1>
        <nav>
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} className={({ isActive }) => (isActive ? 'active' : '')}>
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="user">{user?.email}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </aside>
      <main className="content">
        <div className="topbar">
          {health && (
            <span className={`mode-badge mode-${health.trading_mode}`}>
              {health.trading_mode.toUpperCase()} MODE
              {health.live_trading_armed ? ' · LIVE ARMED' : ''}
              {' · '}market {health.market_session}
              {health.circuit_breaker_tripped ? ' · ⛔ BREAKER TRIPPED' : ''}
            </span>
          )}
        </div>
        <div className="disclaimer">
          ⚠️ Automated analysis only — not investment advice. No profit is guaranteed; trading
          involves risk of loss. Paper trading is enabled by default.
        </div>
        <Outlet />
      </main>
    </div>
  );
}
