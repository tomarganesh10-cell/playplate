import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../../api/client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { TrendingUp, Eye, Heart, MessageCircle, Share2, Users } from 'lucide-react'

const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
const PERIOD_OPTIONS = [7, 14, 30, 60, 90]

export default function AnalyticsDashboard() {
  const [period, setPeriod] = useState(30)

  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['analytics-overview', period],
    queryFn: () => analyticsApi.overview(period),
  })

  const { data: topData } = useQuery({
    queryKey: ['top-content', 5, 'likes'],
    queryFn: () => analyticsApi.topContent(5, 'likes'),
  })

  const analytics = overviewData?.data || {}
  const topContent = topData?.data || []

  const platformData = Object.entries(analytics.platforms || {}).map(([name, stats]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    likes: stats.likes || 0,
    views: stats.views || 0,
    comments: stats.comments || 0,
    shares: stats.shares || 0,
    reach: stats.reach || 0,
  }))

  const pieData = platformData.map((p, i) => ({
    name: p.name,
    value: p.reach,
    color: COLORS[i % COLORS.length],
  })).filter(p => p.value > 0)

  const stats = [
    { label: 'Total Reach', value: analytics.total_reach?.toLocaleString() || '0', icon: Users, color: 'text-violet-400' },
    { label: 'Total Views', value: analytics.total_views?.toLocaleString() || '0', icon: Eye, color: 'text-cyan-400' },
    { label: 'Total Likes', value: analytics.total_likes?.toLocaleString() || '0', icon: Heart, color: 'text-rose-400' },
    { label: 'Total Comments', value: analytics.total_comments?.toLocaleString() || '0', icon: MessageCircle, color: 'text-green-400' },
    { label: 'Total Shares', value: analytics.total_shares?.toLocaleString() || '0', icon: Share2, color: 'text-amber-400' },
    { label: 'Posts Published', value: analytics.published_posts?.toLocaleString() || '0', icon: TrendingUp, color: 'text-blue-400' },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-slate-400 mt-1">Performance across all platforms</p>
        </div>
        <div className="flex gap-2">
          {PERIOD_OPTIONS.map(d => (
            <button
              key={d}
              onClick={() => setPeriod(d)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all
                ${period === d
                  ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30'
                  : 'bg-white/8 text-slate-400 hover:text-white hover:bg-white/12'
                }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map(s => (
          <div key={s.label} className="glass-card p-5">
            <div className="flex items-center gap-3">
              <s.icon size={22} className={s.color} />
              <div>
                <p className="text-slate-400 text-xs">{s.label}</p>
                <p className="text-2xl font-bold text-white">{s.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="glass-card p-6">
          <h3 className="font-semibold text-white mb-4">Platform Comparison</h3>
          {platformData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={platformData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="likes" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="views" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="comments" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500">
              No data yet — publish some content to see analytics
            </div>
          )}
        </div>

        {/* Pie Chart - Reach */}
        <div className="glass-card p-6">
          <h3 className="font-semibold text-white mb-4">Reach by Platform</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                <Legend wrapperStyle={{ color: '#94a3b8', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500">
              No reach data yet
            </div>
          )}
        </div>
      </div>

      {/* Top Content */}
      {topContent.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-semibold text-white mb-4">Top Performing Content</h3>
          <div className="space-y-3">
            {topContent.map((item, i) => (
              <div key={item.id} className="flex items-center gap-4 p-3 rounded-xl bg-white/4 hover:bg-white/8 transition-colors">
                <span className="w-7 h-7 flex items-center justify-center text-sm font-bold text-slate-400">
                  #{i + 1}
                </span>
                {item.image_url && (
                  <img src={item.image_url} alt="" className="w-12 h-12 rounded-lg object-cover" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{item.title}</p>
                  <p className="text-xs text-slate-500 capitalize">{item.platform?.replace('_', ' ')}</p>
                </div>
                <div className="flex gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><Heart size={12} className="text-rose-400" /> {item.likes}</span>
                  <span className="flex items-center gap-1"><Eye size={12} className="text-cyan-400" /> {item.views}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
