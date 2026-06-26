import React, { useState } from 'react'
import { Bell, Mail, MessageCircle, User, Save } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

export default function ClientSettings() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState({
    email: true,
    whatsapp: true,
    dashboard: true,
  })

  const handleSave = () => {
    toast.success('Settings saved!')
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-1">Manage your notification preferences</p>
      </div>

      {/* Profile */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="font-semibold text-white flex items-center gap-2"><User size={18} /> Profile</h2>
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Full Name</label>
            <input type="text" defaultValue={user?.full_name} className="input-field" />
          </div>
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Email</label>
            <input type="email" defaultValue={user?.email} className="input-field" />
          </div>
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Phone / WhatsApp</label>
            <input type="tel" defaultValue={user?.phone} className="input-field" placeholder="+91..." />
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="font-semibold text-white flex items-center gap-2"><Bell size={18} /> Notifications</h2>
        <p className="text-sm text-slate-400">Choose how you want to be notified when new content is ready for approval.</p>

        {[
          { key: 'email', icon: Mail, label: 'Email Notifications', desc: 'Receive daily content ready emails' },
          { key: 'whatsapp', icon: MessageCircle, label: 'WhatsApp Notifications', desc: 'Get WhatsApp alerts for new content' },
          { key: 'dashboard', icon: Bell, label: 'Dashboard Alerts', desc: 'Show notification badges in dashboard' },
        ].map(({ key, icon: Icon, label, desc }) => (
          <div key={key} className="flex items-center justify-between py-3 border-b border-white/8 last:border-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-violet-500/15 rounded-xl flex items-center justify-center">
                <Icon size={18} className="text-violet-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">{label}</p>
                <p className="text-xs text-slate-500">{desc}</p>
              </div>
            </div>
            <button
              onClick={() => setNotifications(n => ({ ...n, [key]: !n[key] }))}
              className={`w-12 h-6 rounded-full transition-all relative ${notifications[key] ? 'bg-violet-600' : 'bg-slate-700'}`}
            >
              <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${notifications[key] ? 'left-6' : 'left-0.5'}`} />
            </button>
          </div>
        ))}
      </div>

      <button onClick={handleSave} className="btn-primary">
        <Save size={16} /> Save Settings
      </button>
    </div>
  )
}
