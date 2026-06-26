import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { contentApi, analyticsApi } from '../../api/client'
import { Link } from 'react-router-dom'
import {
  TrendingUp, Eye, Heart, MessageCircle, Share2, CheckCircle,
  Clock, AlertCircle, Zap, ArrowRight, Calendar, Video, Image
} from 'lucide-react'
import { format } from 'date-fns'

function StatCard({ label, value, icon: Icon, color, subtext }) {
  return (
    <div className="stat-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-1">{value ?? '—'}</p>
          {subtext && <p className="text-xs text-slate-500 mt-1">{subtext}</p>}
        </div>
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon size={22} className="text-white" />
        </div>
      </div>
    </div>
  )
}

function ContentCard({ item }) {
  const statusColors = {
    pending_approval: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    approved: 'bg-green-500/20 text-green-300 border-green-500/30',
    published: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    rejected: 'bg-red-500/20 text-red-300 border-red-500/30',
    scheduled: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    draft: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  }

  const platformIcons = {
    instagram_post: '📸',
    facebook_post: '👥',
    linkedin_post: '💼',
    instagram_reel: '🎬',
    youtube_short: '▶️',
  }

  return (
    <div className="glass-card p-4 hover:border-violet-500/30 transition-all cursor-pointer">
      <div className="flex items-start gap-3">
        <span className="text-2xl">{platformIcons[item.content_type] || '📄'}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-sm font-semibold text-white truncate">{item.title}</p>
          </div>
          <p className="text-xs text-slate-400 line-clamp-2">{item.caption}</p>
          <div className="flex items-center gap-2 mt-2">
            <span className={`badge border ${statusColors[item.status] || 'bg-slate-500/20 text-slate-300'}`}>
              {item.status?.replace('_', ' ')}
            </span>
            <span className="text-xs text-slate-500">
              {item.created_at ? format(new Date(item.created_at), 'MMM d') : ''}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ClientDashboard() {
  const { data: stats } = useQuery({ queryKey: ['content-stats'], queryFn: contentApi.stats })
  const { data: analyticsData } = useQuery({
    queryKey: ['analytics-overview', 30],
    queryFn: () => analyticsApi.overview(30),
  })
  const { data: pendingData } = useQuery({
    queryKey: ['pending-approval'],
    queryFn: contentApi.pendingApproval,
    refetchInterval: 60000,
  })

  const pending = pendingData?.data || []
  const analytics = analyticsData?.data || {}
  const contentStats = stats?.data || {}

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          Good morning, Dr. Anshu! 🌟
        </h1>
        <p className="text-slate-400 mt-1">Your AI social media manager is running. Here's your overview.</p>
      </div>

      {/* Alert: Pending Approvals */}
      {pending.length > 0 && (
        <div className="bg-gradient-to-r from-amber-500/15 to-orange-500/15 border border-amber-500/30 rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center">
              <AlertCircle size={20} className="text-amber-400" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-amber-300">{pending.length} items awaiting your approval</p>
              <p className="text-sm text-amber-400/70">Your AI has generated fresh content — review takes less than 5 minutes!</p>
            </div>
            <Link to="/client/approval" className="btn-primary bg-amber-500 hover:bg-amber-400 shadow-amber-500/30">
              Review Now <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Pending Approval"
          value={contentStats.pending_approval || 0}
          icon={Clock}
          color="bg-amber-500"
          subtext="Awaiting review"
        />
        <StatCard
          label="Published"
          value={contentStats.published || 0}
          icon={CheckCircle}
          color="bg-green-500"
          subtext="Live on platforms"
        />
        <StatCard
          label="Total Reach"
          value={analytics.total_reach?.toLocaleString() || '0'}
          icon={Eye}
          color="bg-blue-500"
          subtext="Last 30 days"
        />
        <StatCard
          label="Engagement"
          value={((analytics.total_likes || 0) + (analytics.total_comments || 0)).toLocaleString()}
          icon={Heart}
          color="bg-rose-500"
          subtext="Likes + Comments"
        />
      </div>

      {/* Platform Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {['instagram', 'facebook', 'linkedin'].map(platform => {
          const pStats = analytics.platforms?.[platform] || {}
          const icons = { instagram: '📸', facebook: '👥', linkedin: '💼' }
          return (
            <div key={platform} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xl">{icons[platform]}</span>
                <span className="font-semibold text-white capitalize">{platform}</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-slate-400 text-xs">Likes</p>
                  <p className="text-lg font-bold text-white">{pStats.likes?.toLocaleString() || 0}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">Views</p>
                  <p className="text-lg font-bold text-white">{pStats.views?.toLocaleString() || 0}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">Comments</p>
                  <p className="text-lg font-bold text-white">{pStats.comments?.toLocaleString() || 0}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">Shares</p>
                  <p className="text-lg font-bold text-white">{pStats.shares?.toLocaleString() || 0}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Content */}
      {pending.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Pending Approval</h2>
            <Link to="/client/approval" className="text-sm text-violet-400 hover:text-violet-300 flex items-center gap-1">
              View all <ArrowRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pending.slice(0, 6).map(item => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { to: '/client/approval', icon: '✅', label: 'Approve Content', color: 'from-green-600/20 to-green-500/10 border-green-500/20' },
            { to: '/client/calendar', icon: '📅', label: 'View Calendar', color: 'from-blue-600/20 to-blue-500/10 border-blue-500/20' },
            { to: '/client/posts', icon: '🖼️', label: 'Posts Library', color: 'from-violet-600/20 to-violet-500/10 border-violet-500/20' },
            { to: '/client/analytics', icon: '📊', label: 'Analytics', color: 'from-cyan-600/20 to-cyan-500/10 border-cyan-500/20' },
          ].map(action => (
            <Link
              key={action.to}
              to={action.to}
              className={`glass-card p-5 bg-gradient-to-br ${action.color} hover:scale-[1.02] transition-transform text-center`}
            >
              <div className="text-3xl mb-2">{action.icon}</div>
              <p className="text-sm font-medium text-slate-200">{action.label}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
