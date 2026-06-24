import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import { useAuth } from './auth/AuthContext.jsx';
import Login from './pages/Login.jsx';
import Signals from './pages/Signals.jsx';
import Portfolio from './pages/Portfolio.jsx';
import Trades from './pages/Trades.jsx';
import Performance from './pages/Performance.jsx';

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center">Loading…</div>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
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
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
