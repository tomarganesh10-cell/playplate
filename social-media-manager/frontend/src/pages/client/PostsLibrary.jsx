import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { contentApi } from '../../api/client'
import { Search, Filter, Eye, Heart, MessageCircle, Share2 } from 'lucide-react'
import { format } from 'date-fns'

const STATUS_COLORS = {
  published: 'bg-green-500/20 text-green-300 border-green-500/30',
  approved: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  scheduled: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  pending_approval: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  rejected: 'bg-red-500/20 text-red-300 border-red-500/30',
  draft: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
}

const PLATFORM_ICONS = {
  instagram_post: '📸',
  facebook_post: '👥',
  linkedin_post: '💼',
  instagram_reel: '🎬',
  youtube_short: '▶️',
}

export default function PostsLibrary() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [platformFilter, setPlatformFilter] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['content', statusFilter, platformFilter, page],
    queryFn: () => contentApi.list({
      status: statusFilter || undefined,
      content_type: platformFilter || undefined,
      page,
      limit: 12,
    }),
  })

  const items = data?.data?.items || []
  const totalPages = data?.data?.pages || 1
  const total = data?.data?.total || 0

  const filtered = search
    ? items.filter(i => i.title?.toLowerCase().includes(search.toLowerCase()) ||
        i.caption?.toLowerCase().includes(search.toLowerCase()))
    : items

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Posts Library</h1>
        <p className="text-slate-400 mt-1">{total} total items in your library</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search posts..."
            className="input-field pl-9"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="input-field w-auto"
        >
          <option value="">All Statuses</option>
          <option value="published">Published</option>
          <option value="approved">Approved</option>
          <option value="scheduled">Scheduled</option>
          <option value="pending_approval">Pending Approval</option>
          <option value="rejected">Rejected</option>
          <option value="draft">Draft</option>
        </select>

        <select
          value={platformFilter}
          onChange={(e) => { setPlatformFilter(e.target.value); setPage(1) }}
          className="input-field w-auto"
        >
          <option value="">All Platforms</option>
          <option value="instagram_post">Instagram</option>
          <option value="facebook_post">Facebook</option>
          <option value="linkedin_post">LinkedIn</option>
          <option value="instagram_reel">Instagram Reel</option>
          <option value="youtube_short">YouTube Short</option>
        </select>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {filtered.map(item => (
          <div key={item.id} className="glass-card overflow-hidden hover:border-violet-500/30 transition-all">
            {/* Image */}
            {item.image_url ? (
              <img src={item.image_url} alt={item.title} className="w-full h-44 object-cover" />
            ) : (
              <div className="w-full h-44 bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center">
                <span className="text-4xl">{PLATFORM_ICONS[item.content_type] || '📄'}</span>
              </div>
            )}

            <div className="p-4 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold text-white text-sm leading-tight line-clamp-2">{item.title}</h3>
                <span className="text-lg flex-shrink-0">{PLATFORM_ICONS[item.content_type] || '📄'}</span>
              </div>

              <p className="text-xs text-slate-400 line-clamp-2">{item.caption}</p>

              <div className="flex items-center justify-between">
                <span className={`badge border text-[11px] ${STATUS_COLORS[item.status] || ''}`}>
                  {item.status?.replace(/_/g, ' ')}
                </span>
                <span className="text-xs text-slate-500">
                  {item.created_at ? format(new Date(item.created_at), 'MMM d, yyyy') : ''}
                </span>
              </div>

              {/* Stats (if published) */}
              {item.status === 'published' && (
                <div className="flex gap-3 pt-2 border-t border-white/8 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><Heart size={12} className="text-rose-400" /> {item.likes}</span>
                  <span className="flex items-center gap-1"><Eye size={12} className="text-cyan-400" /> {item.views}</span>
                  <span className="flex items-center gap-1"><MessageCircle size={12} className="text-green-400" /> {item.comments}</span>
                  <span className="flex items-center gap-1"><Share2 size={12} className="text-amber-400" /> {item.shares}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-slate-400 text-sm">Page {page} of {totalPages}</span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn-secondary disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
