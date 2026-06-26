import React, { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  LayoutDashboard, CheckSquare, Calendar, Image, BarChart3,
  Settings, LogOut, Bell, Menu, X, Sparkles, ChevronDown
} from 'lucide-react'

const navItems = [
  { to: '/client', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/client/approval', label: 'Approval Queue', icon: CheckSquare, badge: '!' },
  { to: '/client/calendar', label: 'Content Calendar', icon: Calendar },
  { to: '/client/posts', label: 'Posts Library', icon: Image },
  { to: '/client/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/client/settings', label: 'Settings', icon: Settings },
]

export default function ClientLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const Sidebar = () => (
    <aside className="flex flex-col h-full bg-slate-900/90 backdrop-blur-xl border-r border-white/8 w-64">
      {/* Logo */}
      <div className="p-6 border-b border-white/8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-xl">🦷</span>
          </div>
          <div>
            <p className="font-bold text-white text-sm">Playplate SMM</p>
            <p className="text-xs text-slate-500">AI Social Media</p>
          </div>
        </div>
      </div>

      {/* Doctor Profile */}
      <div className="p-4 border-b border-white/8">
        <div className="flex items-center gap-3 p-3 rounded-xl bg-violet-500/10 border border-violet-500/20">
          <div className="w-9 h-9 bg-gradient-to-br from-violet-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
            AG
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-white truncate">{user?.full_name}</p>
            <p className="text-xs text-violet-400">Client Dashboard</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            onClick={() => setSidebarOpen(false)}
          >
            <item.icon size={18} />
            <span className="flex-1">{item.label}</span>
            {item.badge && (
              <span className="bg-violet-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/8">
        <button onClick={handleLogout} className="sidebar-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10">
          <LogOut size={18} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  )

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex flex-col flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-black/60" onClick={() => setSidebarOpen(false)} />
          <div className="relative flex flex-col w-64 z-10">
            <Sidebar />
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center gap-4 px-6 py-4 border-b border-white/8 bg-slate-900/50 backdrop-blur-xl flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-slate-400 hover:text-white"
          >
            <Menu size={22} />
          </button>

          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-violet-400" />
            <span className="text-sm text-slate-400">AI Content Manager</span>
          </div>

          <div className="ml-auto flex items-center gap-3">
            <button className="relative text-slate-400 hover:text-white p-2 rounded-lg hover:bg-white/8 transition-colors">
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-violet-500 rounded-full"></span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
