import React from 'react'
import { Settings, Clock, Globe, Users, Zap } from 'lucide-react'

export default function AdminSettings() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">System Settings</h1>
        <p className="text-slate-400 mt-1">Global configuration for the AI Social Media Manager</p>
      </div>

      <div className="glass-card p-6 space-y-5">
        <h2 className="font-semibold text-white flex items-center gap-2"><Clock size={18} /> Scheduling</h2>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Daily Generation Time (IST)</label>
            <input type="time" defaultValue="09:00" className="input-field w-auto" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Post on Alternate Days</p>
              <p className="text-xs text-slate-500">Prevents oversaturation on social platforms</p>
            </div>
            <div className="w-12 h-6 bg-violet-600 rounded-full relative cursor-pointer">
              <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-6" />
            </div>
          </div>
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Topic Cooldown (days)</label>
            <input type="number" defaultValue={30} min={7} max={90} className="input-field w-auto" />
          </div>
        </div>
      </div>

      <div className="glass-card p-6 space-y-5">
        <h2 className="font-semibold text-white flex items-center gap-2"><Zap size={18} /> Content Generation</h2>
        <div className="space-y-4">
          {[
            { label: 'Posts per day', key: 'posts', default: 5 },
            { label: 'Reel scripts per day', key: 'reels', default: 5 },
            { label: 'Videos per day', key: 'videos', default: 5 },
          ].map(item => (
            <div key={item.key}>
              <label className="text-sm text-slate-400 mb-2 block">{item.label}</label>
              <input type="number" defaultValue={item.default} min={1} max={20} className="input-field w-auto" />
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card p-6 space-y-5">
        <h2 className="font-semibold text-white flex items-center gap-2"><Globe size={18} /> Client Info</h2>
        <div className="space-y-3 text-sm">
          {[
            { label: 'Client Name', value: 'Dr. Anshu Gupta' },
            { label: 'Specialty', value: 'Cosmetic & Aesthetic Dentist, Implantologist, Pediatric Dentist' },
            { label: 'Location', value: 'Chandigarh, India' },
            { label: 'Website', value: 'https://www.chandigarhdentist.com' },
            { label: 'Experience', value: '27+ Years' },
          ].map(item => (
            <div key={item.label} className="flex justify-between items-start gap-4 py-2 border-b border-white/8 last:border-0">
              <span className="text-slate-400">{item.label}</span>
              <span className="text-white text-right">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      <button className="btn-primary">
        <Settings size={16} /> Save Settings
      </button>
    </div>
  )
}
