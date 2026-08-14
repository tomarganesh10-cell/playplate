// Minimal fetch wrapper with JWT handling and auto-refresh.
const BASE = import.meta.env.VITE_API_BASE_URL || '/api';

const TOKEN_KEY = 'pp_access';
const REFRESH_KEY = 'pp_refresh';

export const tokens = {
  get access() { return localStorage.getItem(TOKEN_KEY); },
  get refresh() { return localStorage.getItem(REFRESH_KEY); },
  set({ access_token, refresh_token }) {
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(REFRESH_KEY, refresh_token);
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

async function request(path, { method = 'GET', body, auth = true, retry = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth && retry && tokens.refresh) {
    const refreshed = await tryRefresh();
    if (refreshed) return request(path, { method, body, auth, retry: false });
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

async function tryRefresh() {
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokens.refresh }),
    });
    if (!res.ok) return false;
    tokens.set(await res.json());
    return true;
  } catch {
    return false;
  }
}

export const api = {
  login: (email, password) =>
    request('/auth/login', { method: 'POST', body: { email, password }, auth: false }),
  me: () => request('/auth/me'),
  signals: (status = 'active') => request(`/signals/?status=${status}`),
  scan: (timeframe = '15m') => request(`/signals/scan?timeframe=${timeframe}`, { method: 'POST' }),
  portfolio: () => request('/portfolio/'),
  trades: (status = 'all') => request(`/trades/?status=${status}`),
  placeOrder: (order) => request('/trades/order', { method: 'POST', body: order }),
  closeTrade: (id) => request(`/trades/${id}/close`, { method: 'POST' }),
  performance: (days = 30) => request(`/performance/?days=${days}`),
  health: () => request('/health/ready', { auth: false }),
  brokerStatus: () => request('/broker/status'),
  brokerDiagnostics: () => request('/broker/diagnostics'),
  brokerLoginUrl: () => request('/broker/login-url'),
  brokerSession: (request_token) =>
    request('/broker/session', { method: 'POST', body: { request_token } }),
  indices: () => request('/market/indices'),
  movers: () => request('/market/movers'),
  news: () => request('/market/news'),
};
