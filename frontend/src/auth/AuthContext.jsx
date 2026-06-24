import { createContext, useContext, useEffect, useState } from 'react';
import { api, tokens } from '../api/client.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tokens.access) { setLoading(false); return; }
    api.me().then(setUser).catch(() => tokens.clear()).finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const t = await api.login(email, password);
    tokens.set(t);
    setUser(await api.me());
  };

  const logout = () => { tokens.clear(); setUser(null); };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
