import React from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { contentApi, kbApi } from '../../api/client'
import { Zap, Database, RefreshCw, Activity, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdminDashboard() {
  const { data: stats } = useQuery({ queryKey: ['content-stats'], queryFn: contentApi.stats })
  const { data: kbCategories } = useQuery({ queryKey: ['kb-categories'], queryFn: kbApi.categories })

  const generateMutation = useMutation({
    mutationFn: contentApi.triggerGeneration,
    onSuccess: () => toast.success('Daily generation started!'),
    onError: () => toast.error('Generation failed'),
  })

  const crawlMutation = useMutation({
    mutationFn: kbApi.crawl,
    onSuccess: () => toast.success('Website crawl started!'),
    onError: () => toast.error('Crawl failed'),
  })

  const contentStats = stats?.data || {}
  const categories = kbCategories?.data || {}

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
        <p className="text-slate-400 mt-1">System overview and controls for Dr. Anshu Gupta's SMM</p>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Content', value: contentStats.total || 0, icon: Activity, color: 'bg-violet-600' },
          { label: 'Published', value: contentStats.published || 0, icon: CheckCircle, color: 'bg-green-600' },
          { label: 'Pending', value: contentStats.pending_approval || 0, icon: AlertCircle, color: 'bg-amber-600' },
          { label: 'KB Entries', value: Object.values(categories).reduce((a, b) => a + b, 0), icon: Database, color: 'bg-blue-600' },
        ].map(stat => (
          <div key={stat.label} className="stat-card">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl ${stat.color}`}>
                <stat.icon size={20} className="text-white" />
              </div>
              <div>
                <p className="text-slate-400 text-xs">{stat.label}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="glass-card p-6">
        <h2 className="font-semibold text-white mb-4">System Controls</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-5 rounded-xl bg-gradient-to-br from-violet-600/15 to-violet-500/5 border border-violet-500/20">
            <div className="flex items-center gap-3 mb-3">
              <Zap size={22} className="text-violet-400" />
              <h3 className="font-semibold text-white">Generate Daily Content</h3>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              Manually trigger the AI content generation workflow. This runs automatically at 9:00 AM IST.
            </p>
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="btn-primary w-full justify-center"
            >
              {generateMutation.isPending ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Generating...</>
              ) : (
                <><Zap size={16} /> Generate Now</>
              )}
            </button>
          </div>

          <div className="p-5 rounded-xl bg-gradient-to-br from-cyan-600/15 to-cyan-500/5 border border-cyan-500/20">
            <div className="flex items-center gap-3 mb-3">
              <RefreshCw size={22} className="text-cyan-400" />
              <h3 className="font-semibold text-white">Crawl Website</h3>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              Re-crawl chandigarhdentist.com to refresh the knowledge base with latest content.
            </p>
            <button
              onClick={() => crawlMutation.mutate()}
              disabled={crawlMutation.isPending}
              className="btn-secondary w-full justify-center border-cyan-500/30 text-cyan-300"
            >
              {crawlMutation.isPending ? (
                <><div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" /> Crawling...</>
              ) : (
                <><RefreshCw size={16} /> Crawl Now</>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Knowledge Base Summary */}
      <div className="glass-card p-6">
        <h2 className="font-semibold text-white mb-4">Knowledge Base Categories</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(categories).map(([category, count]) => (
            <div key={category} className="p-3 rounded-xl bg-white/4 border border-white/8">
              <p className="text-xs text-slate-400 capitalize">{category.replace(/_/g, ' ')}</p>
              <p className="text-lg font-bold text-white mt-1">{count}</p>
              <p className="text-xs text-slate-500">entries</p>
            </div>
          ))}
        </div>
      </div>

      {/* System Info */}
      <div className="glass-card p-6">
        <h2 className="font-semibold text-white mb-4">System Information</h2>
        <div className="space-y-3 text-sm">
          {[
            { label: 'Client', value: 'Dr. Anshu Gupta — Chandigarh Dentist' },
            { label: 'Domain', value: 'social.playplate.in' },
            { label: 'Daily Generation', value: '9:00 AM IST (automated)' },
            { label: 'Posting Schedule', value: 'Alternate days' },
            { label: 'Topic Cooldown', value: '30 days (no repeat)' },
            { label: 'Platforms', value: 'Instagram, Facebook, LinkedIn, YouTube, Google Business' },
          ].map(item => (
            <div key={item.label} className="flex items-start justify-between gap-4 py-2 border-b border-white/8 last:border-0">
              <span className="text-slate-400">{item.label}</span>
              <span className="text-white font-medium text-right">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
