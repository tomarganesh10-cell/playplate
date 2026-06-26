import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentApi } from '../../api/client'
import toast from 'react-hot-toast'
import { Check, X, Edit3, RefreshCw, Instagram, Linkedin, Facebook, Video, Hash } from 'lucide-react'

const PLATFORM_LABELS = {
  instagram_post: { label: 'Instagram', icon: '📸', color: 'from-pink-500 to-purple-600' },
  facebook_post: { label: 'Facebook', icon: '👥', color: 'from-blue-600 to-blue-700' },
  linkedin_post: { label: 'LinkedIn', icon: '💼', color: 'from-blue-700 to-cyan-700' },
  instagram_reel: { label: 'Instagram Reel', icon: '🎬', color: 'from-purple-600 to-pink-600' },
  youtube_short: { label: 'YouTube Short', icon: '▶️', color: 'from-red-600 to-red-700' },
}

function ContentApprovalCard({ item, onAction }) {
  const [editing, setEditing] = useState(false)
  const [editedCaption, setEditedCaption] = useState(item.caption || '')
  const [regenInstructions, setRegenInstructions] = useState('')
  const [showRegen, setShowRegen] = useState(false)

  const platform = PLATFORM_LABELS[item.content_type] || { label: item.content_type, icon: '📄', color: 'from-slate-600 to-slate-700' }

  return (
    <div className="glass-card overflow-hidden">
      {/* Platform Header */}
      <div className={`bg-gradient-to-r ${platform.color} p-4 flex items-center gap-3`}>
        <span className="text-2xl">{platform.icon}</span>
        <div>
          <p className="font-semibold text-white">{platform.label}</p>
          <p className="text-xs text-white/70">{item.category?.replace(/_/g, ' ')}</p>
        </div>
        <div className="ml-auto">
          <span className="badge bg-white/20 text-white border border-white/30">Pending Review</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        <div>
          <h3 className="font-semibold text-white text-base">{item.title}</h3>
          {item.image_url && (
            <img src={item.image_url} alt={item.title} className="w-full h-48 object-cover rounded-xl mt-3" />
          )}
        </div>

        {/* Caption */}
        <div>
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Caption</label>
          {editing ? (
            <textarea
              value={editedCaption}
              onChange={(e) => setEditedCaption(e.target.value)}
              className="input-field mt-2 min-h-[120px] resize-none text-sm"
              placeholder="Edit caption..."
            />
          ) : (
            <p className="text-slate-300 text-sm mt-2 leading-relaxed line-clamp-4">{item.caption}</p>
          )}
        </div>

        {/* Hashtags */}
        {item.hashtags && item.hashtags.length > 0 && (
          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Hash size={12} /> Hashtags ({item.hashtags.length})
            </label>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {item.hashtags.slice(0, 10).map((tag, i) => (
                <span key={i} className="px-2 py-1 bg-violet-500/15 text-violet-300 text-xs rounded-full border border-violet-500/20">
                  {tag}
                </span>
              ))}
              {item.hashtags.length > 10 && (
                <span className="px-2 py-1 bg-slate-500/15 text-slate-400 text-xs rounded-full">
                  +{item.hashtags.length - 10} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* CTA */}
        {item.cta && (
          <div className="bg-violet-500/10 border border-violet-500/20 rounded-xl p-3">
            <p className="text-xs text-violet-400 font-medium">CTA</p>
            <p className="text-sm text-violet-200 mt-1">{item.cta}</p>
          </div>
        )}

        {/* Regenerate Instructions */}
        {showRegen && (
          <div>
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Regeneration Instructions</label>
            <textarea
              value={regenInstructions}
              onChange={(e) => setRegenInstructions(e.target.value)}
              className="input-field mt-2 min-h-[80px] resize-none text-sm"
              placeholder="Tell the AI what to change (e.g., 'Focus more on kids dentistry', 'Make it more professional')"
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-white/8">
          {/* Approve */}
          {editing ? (
            <button
              onClick={() => {
                onAction(item.id, { action: 'approve', edited_caption: editedCaption })
                setEditing(false)
              }}
              className="btn-primary bg-gradient-to-r from-green-600 to-green-500 shadow-green-500/25 flex-1"
            >
              <Check size={15} /> Save & Approve
            </button>
          ) : (
            <button
              onClick={() => onAction(item.id, { action: 'approve' })}
              className="btn-primary bg-gradient-to-r from-green-600 to-green-500 shadow-green-500/25 flex-1"
            >
              <Check size={15} /> Approve
            </button>
          )}

          {/* Edit */}
          <button
            onClick={() => { setEditing(!editing); setShowRegen(false) }}
            className="btn-secondary flex-1"
          >
            <Edit3 size={15} /> {editing ? 'Cancel Edit' : 'Edit'}
          </button>

          {/* Regenerate */}
          {showRegen ? (
            <button
              onClick={() => {
                onAction(item.id, { action: 'regenerate', regenerate_instructions: regenInstructions })
                setShowRegen(false)
              }}
              className="btn-secondary border-cyan-500/30 text-cyan-300 flex-1"
            >
              <RefreshCw size={15} /> Send for Regen
            </button>
          ) : (
            <button
              onClick={() => { setShowRegen(true); setEditing(false) }}
              className="btn-secondary"
            >
              <RefreshCw size={15} />
            </button>
          )}

          {/* Reject */}
          <button
            onClick={() => onAction(item.id, { action: 'reject', notes: 'Rejected by doctor' })}
            className="btn-secondary border-red-500/30 text-red-400 hover:text-red-300"
          >
            <X size={15} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default function ApprovalQueue() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['pending-approval'],
    queryFn: contentApi.pendingApproval,
    refetchInterval: 30000,
  })

  const approvalMutation = useMutation({
    mutationFn: ({ id, action }) => contentApi.approve(id, action),
    onSuccess: (_, { action }) => {
      const messages = {
        approve: '✅ Content approved and queued for posting!',
        reject: '❌ Content rejected',
        edit: '✏️ Edit saved',
        regenerate: '🔄 Sent for regeneration',
      }
      toast.success(messages[action.action] || 'Action completed')
      queryClient.invalidateQueries({ queryKey: ['pending-approval'] })
      queryClient.invalidateQueries({ queryKey: ['content-stats'] })
    },
    onError: () => toast.error('Action failed, please try again'),
  })

  const handleAction = (id, action) => {
    approvalMutation.mutate({ id, action })
  }

  const approveAll = () => {
    const items = data?.data || []
    items.forEach(item => {
      approvalMutation.mutate({ id: item.id, action: { action: 'approve' } })
    })
  }

  const pending = data?.data || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Approval Queue</h1>
          <p className="text-slate-400 mt-1">
            {pending.length > 0
              ? `${pending.length} items waiting for your review`
              : 'All caught up! No pending items.'}
          </p>
        </div>
        {pending.length > 0 && (
          <button onClick={approveAll} className="btn-primary bg-gradient-to-r from-green-600 to-green-500 shadow-green-500/25">
            <Check size={16} /> Approve All ({pending.length})
          </button>
        )}
      </div>

      {/* Filters summary */}
      {pending.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {['instagram_post', 'facebook_post', 'linkedin_post', 'instagram_reel', 'youtube_short'].map(type => {
            const count = pending.filter(p => p.content_type === type).length
            if (!count) return null
            const p = PLATFORM_LABELS[type]
            return (
              <span key={type} className="badge bg-white/8 text-slate-300 border border-white/10 py-1.5 px-3">
                {p?.icon} {p?.label} ({count})
              </span>
            )
          })}
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!isLoading && pending.length === 0 && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-xl font-semibold text-white">All Caught Up!</h2>
          <p className="text-slate-400 mt-2">No content pending approval. Check back tomorrow morning!</p>
          <p className="text-slate-500 text-sm mt-1">Daily generation runs at 9:00 AM IST</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {pending.map(item => (
          <ContentApprovalCard
            key={item.id}
            item={item}
            onAction={handleAction}
          />
        ))}
      </div>
    </div>
  )
}
