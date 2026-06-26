import React from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { LayoutDashboard, Key, Database, Settings, LogOut, Shield, DollarSign } from 'lucide-react'

const navItems = [
  { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin/credentials', label: 'API Credentials', icon: Key },
  { to: '/admin/knowledge-base', label: 'Knowledge Base', icon: Database },
  { to: '/admin/pricing', label: 'Video Pricing', icon: DollarSign },
  { to: '/admin/settings', label: 'Settings', icon: Settings },
]

export default function AdminLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      <aside className="flex flex-col w-64 bg-slate-900/90 backdrop-blur-xl border-r border-white/8">
        <div className="p-6 border-b border-white/8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-orange-600 rounded-xl flex items-center justify-center">
              <Shield size={20} className="text-white" />
            </div>
            <div>
              <p className="font-bold text-white text-sm">Admin Panel</p>
              <p className="text-xs text-slate-500">Playplate SMM</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-b border-white/8">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center text-white font-bold text-xs">
              SA
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{user?.full_name}</p>
              <p className="text-xs text-red-400">Super Admin</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/8">
          <NavLink to="/client" className="sidebar-link text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 mb-1">
            <LayoutDashboard size={18} /> Client View
          </NavLink>
          <button onClick={() => { logout(); navigate('/login') }} className="sidebar-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10">
            <LogOut size={18} /> Sign Out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}
