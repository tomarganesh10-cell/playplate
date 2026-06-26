import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { kbApi } from '../../api/client'
import toast from 'react-hot-toast'
import { Database, RefreshCw, Search, Tag } from 'lucide-react'

export default function AdminKnowledgeBase() {
  const [selectedCategory, setSelectedCategory] = useState('')
  const queryClient = useQueryClient()

  const { data: entries, isLoading } = useQuery({
    queryKey: ['kb-entries', selectedCategory],
    queryFn: () => kbApi.list(selectedCategory || undefined),
  })

  const { data: categoriesData } = useQuery({
    queryKey: ['kb-categories'],
    queryFn: kbApi.categories,
  })

  const crawlMutation = useMutation({
    mutationFn: kbApi.crawl,
    onSuccess: () => { toast.success('Crawl started!'); queryClient.invalidateQueries({ queryKey: ['kb-entries'] }) },
  })

  const seedMutation = useMutation({
    mutationFn: kbApi.seed,
    onSuccess: () => { toast.success('Knowledge base seeded!'); queryClient.invalidateQueries({ queryKey: ['kb-entries'] }) },
  })

  const items = entries?.data || []
  const categories = categoriesData?.data || {}

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Knowledge Base</h1>
          <p className="text-slate-400 mt-1">Dental knowledge extracted from chandigarhdentist.com</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => seedMutation.mutate()} disabled={seedMutation.isPending} className="btn-secondary">
            <Database size={16} /> Seed KB
          </button>
          <button onClick={() => crawlMutation.mutate()} disabled={crawlMutation.isPending} className="btn-primary">
            <RefreshCw size={16} /> Re-crawl Site
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory('')}
          className={`badge py-1.5 px-4 border transition-all ${!selectedCategory ? 'bg-violet-500/20 text-violet-300 border-violet-500/30' : 'bg-white/5 text-slate-400 border-white/10 hover:border-white/20'}`}
        >
          All ({Object.values(categories).reduce((a, b) => a + b, 0)})
        </button>
        {Object.entries(categories).map(([cat, count]) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`badge py-1.5 px-4 border transition-all ${selectedCategory === cat ? 'bg-violet-500/20 text-violet-300 border-violet-500/30' : 'bg-white/5 text-slate-400 border-white/10 hover:border-white/20'}`}
          >
            {cat.replace(/_/g, ' ')} ({count})
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map(item => (
          <div key={item.id} className="glass-card p-5">
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3 className="font-semibold text-white text-sm">{item.title}</h3>
              <span className="badge bg-violet-500/15 text-violet-300 border border-violet-500/20 text-[11px] whitespace-nowrap">
                {item.category?.replace(/_/g, ' ')}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">{item.content}</p>
            {item.tags && item.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {item.tags.map((tag, i) => (
                  <span key={i} className="flex items-center gap-1 px-2 py-0.5 bg-slate-700/50 text-slate-400 text-[11px] rounded-full">
                    <Tag size={9} /> {tag}
                  </span>
                ))}
              </div>
            )}
            {item.last_crawled && (
              <p className="text-[11px] text-slate-600 mt-2">Crawled: {new Date(item.last_crawled).toLocaleDateString()}</p>
            )}
          </div>
        ))}
      </div>

      {items.length === 0 && !isLoading && (
        <div className="text-center py-16">
          <Database size={48} className="text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No knowledge base entries yet.</p>
          <button onClick={() => seedMutation.mutate()} className="btn-primary mt-4 mx-auto">
            <Database size={16} /> Seed Knowledge Base
          </button>
        </div>
      )}
    </div>
  )
}
