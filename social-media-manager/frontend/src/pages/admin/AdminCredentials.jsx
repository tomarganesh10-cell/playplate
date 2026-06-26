import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { credentialsApi } from '../../api/client'
import toast from 'react-hot-toast'
import { Key, Check, AlertCircle, Eye, EyeOff, Save, Trash2 } from 'lucide-react'

function CredentialRow({ cred, onSave, onDelete }) {
  const [value, setValue] = useState('')
  const [showInput, setShowInput] = useState(false)
  const [showValue, setShowValue] = useState(false)

  const icons = {
    openai: '🤖', anthropic: '🧠', gemini: '✨', meta: '📘', linkedin: '💼',
    youtube: '▶️', google_drive: '📁', google_sheets: '📊', whatsapp: '💬',
    sendgrid: '📧', kling: '🎬', runway: '🎥', pika: '🎦', hailuo: '🎞️',
    stability: '🖼️', google_veo: '📽️',
  }

  return (
    <div className={`flex items-center gap-4 p-4 rounded-xl border transition-all
      ${cred.is_configured
        ? 'bg-green-500/5 border-green-500/20'
        : 'bg-white/3 border-white/8 hover:border-white/15'
      }`}
    >
      <span className="text-2xl">{icons[cred.service] || '🔑'}</span>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-white text-sm">{cred.label}</p>
        <p className="text-xs text-slate-500 font-mono">{cred.key_name}</p>
        {cred.last_verified && (
          <p className="text-xs text-green-400 mt-0.5">
            Last verified: {new Date(cred.last_verified).toLocaleDateString()}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2">
        {cred.is_configured ? (
          <span className="badge bg-green-500/20 text-green-300 border border-green-500/30 flex items-center gap-1">
            <Check size={11} /> Configured
          </span>
        ) : (
          <span className="badge bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
            <AlertCircle size={11} /> Not Set
          </span>
        )}

        {showInput ? (
          <div className="flex items-center gap-2">
            <div className="relative">
              <input
                type={showValue ? 'text' : 'password'}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                className="input-field w-64 pr-10 text-sm py-2"
                placeholder={`Enter ${cred.label}...`}
              />
              <button
                onClick={() => setShowValue(!showValue)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                {showValue ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            <button
              onClick={() => { onSave(cred.service, value); setShowInput(false); setValue('') }}
              disabled={!value}
              className="btn-primary py-2 disabled:opacity-40"
            >
              <Save size={15} /> Save
            </button>
            <button onClick={() => setShowInput(false)} className="btn-secondary py-2">Cancel</button>
          </div>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={() => setShowInput(true)}
              className="btn-secondary py-2 text-xs"
            >
              <Key size={14} /> {cred.is_configured ? 'Update' : 'Set Key'}
            </button>
            {cred.is_configured && (
              <button
                onClick={() => onDelete(cred.service)}
                className="btn-secondary py-2 text-xs border-red-500/30 text-red-400 hover:text-red-300"
              >
                <Trash2 size={14} />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

const SERVICE_GROUPS = {
  'AI Models': ['openai', 'anthropic', 'gemini'],
  'Social Platforms': ['meta', 'linkedin', 'youtube'],
  'Google Services': ['google_drive', 'google_sheets'],
  'Video AI': ['kling', 'runway', 'pika', 'hailuo', 'google_veo'],
  'Image AI': ['stability'],
  'Communication': ['whatsapp', 'sendgrid'],
}

export default function AdminCredentials() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['credentials'],
    queryFn: credentialsApi.list,
  })

  const saveMutation = useMutation({
    mutationFn: ({ service, value }) => credentialsApi.update(service, value),
    onSuccess: () => {
      toast.success('Credential saved securely!')
      queryClient.invalidateQueries({ queryKey: ['credentials'] })
    },
    onError: () => toast.error('Failed to save credential'),
  })

  const deleteMutation = useMutation({
    mutationFn: (service) => credentialsApi.delete(service),
    onSuccess: () => {
      toast.success('Credential removed')
      queryClient.invalidateQueries({ queryKey: ['credentials'] })
    },
  })

  const credentials = data?.data || []
  const credMap = Object.fromEntries(credentials.map(c => [c.service, c]))

  const configured = credentials.filter(c => c.is_configured).length
  const total = credentials.length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">API Credentials</h1>
          <p className="text-slate-400 mt-1">Manage all API keys and integration credentials</p>
        </div>
        <div className="glass-card px-5 py-3">
          <p className="text-sm text-slate-400">Configured</p>
          <p className="text-2xl font-bold text-white">{configured}<span className="text-slate-500 text-lg">/{total}</span></p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="glass-card p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-slate-400">Setup Progress</span>
          <span className="text-sm font-semibold text-white">{Math.round((configured / total) * 100)}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-violet-600 to-cyan-600 h-2 rounded-full transition-all"
            style={{ width: `${(configured / total) * 100}%` }}
          />
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {Object.entries(SERVICE_GROUPS).map(([groupName, services]) => {
        const groupCreds = services.map(s => credMap[s]).filter(Boolean)
        if (!groupCreds.length) return null
        return (
          <div key={groupName} className="glass-card p-6">
            <h2 className="font-semibold text-white mb-4 text-sm uppercase tracking-wider text-slate-400">
              {groupName}
            </h2>
            <div className="space-y-3">
              {groupCreds.map(cred => (
                <CredentialRow
                  key={cred.service}
                  cred={cred}
                  onSave={(service, value) => saveMutation.mutate({ service, value })}
                  onDelete={(service) => deleteMutation.mutate(service)}
                />
              ))}
            </div>
          </div>
        )
      })}

      <div className="glass-card p-5 border-amber-500/20 bg-amber-500/5">
        <div className="flex gap-3">
          <AlertCircle size={20} className="text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-amber-300 text-sm">Security Note</p>
            <p className="text-xs text-amber-400/70 mt-1">
              API keys are encrypted before storage. Keys are never exposed in the UI after saving.
              Only enter credentials on a secure network. Contact your system admin to rotate keys.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
