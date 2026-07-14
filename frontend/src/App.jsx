import { useEffect } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import { useAuth } from './auth/AuthContext.jsx';
import Login from './pages/Login.jsx';
import Signals from './pages/Signals.jsx';
import Portfolio from './pages/Portfolio.jsx';
import Trades from './pages/Trades.jsx';
import Performance from './pages/Performance.jsx';
import Broker from './pages/Broker.jsx';

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center">Loading…</div>;
  return user ? children : <Navigate to="/login" replace />;
}

// Kite redirects to /broker/callback?request_token=... after login. Capture the
// token immediately (even before auth) so it survives the login redirect, then
// land on the Broker page to complete the connection.
function CaptureKiteToken() {
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('request_token');
    if (token) {
      sessionStorage.setItem('pp_kite_request_token', token);
      navigate('/broker', { replace: true });
    }
  }, [location, navigate]);
  return null;
}

export default function App() {
  return (
    <>
      <CaptureKiteToken />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <Protected>
              <Layout />
            </Protected>
          }
        >
          <Route index element={<Navigate to="/signals" replace />} />
          <Route path="signals" element={<Signals />} />
          <Route path="portfolio" element={<Portfolio />} />
          <Route path="trades" element={<Trades />} />
          <Route path="performance" element={<Performance />} />
          <Route path="broker" element={<Broker />} />
          <Route path="broker/callback" element={<Broker />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
