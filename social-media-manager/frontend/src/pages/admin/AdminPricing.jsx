import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { DollarSign, TrendingUp, Video, Image, Star, ExternalLink, Calculator } from 'lucide-react'

const GENERATOR_ICONS = {
  kling:      { emoji: '🎬', color: 'from-orange-500 to-red-500' },
  runway:     { emoji: '✈️', color: 'from-blue-500 to-cyan-500' },
  pika:       { emoji: '⚡', color: 'from-yellow-500 to-orange-500' },
  hailuo:     { emoji: '🌊', color: 'from-teal-500 to-green-500' },
  google_veo: { emoji: '🔍', color: 'from-blue-600 to-indigo-600' },
  dalle3:     { emoji: '🖼️', color: 'from-purple-500 to-violet-600' },
}

const QUALITY_COLORS = {
  standard: 'bg-slate-500/20 text-slate-300',
  pro:      'bg-blue-500/20 text-blue-300',
  hd:       'bg-violet-500/20 text-violet-300',
  'gen4 turbo': 'bg-cyan-500/20 text-cyan-300',
  veo3:     'bg-green-500/20 text-green-300',
}

function GeneratorCard({ generatorKey, data }) {
  const [showPlans, setShowPlans] = useState(false)
  const icon = GENERATOR_ICONS[generatorKey] || { emoji: '🎥', color: 'from-slate-500 to-slate-600' }
  const lowestPriceUSD = Math.min(...Object.values(data.plans || {}).map(p => p.price_usd || 999))
  const lowestPriceINR = Math.min(...Object.values(data.plans || {}).map(p => p.price_inr || 9999))

  const recoPlan = data.monthly_subscriptions?.[data.recommended_plan]

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className={`bg-gradient-to-r ${icon.color} p-5 flex items-center gap-4`}>
        <span className="text-4xl">{icon.emoji}</span>
        <div className="flex-1">
          <h3 className="text-xl font-bold text-white">{data.name}</h3>
          <p className="text-white/70 text-sm mt-0.5">
            From <span className="font-bold text-white">${lowestPriceUSD}</span> /video
            &nbsp;·&nbsp; ₹{lowestPriceINR}/video
          </p>
        </div>
        <a href={data.website} target="_blank" rel="noopener noreferrer"
           className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors">
          <ExternalLink size={16} className="text-white" />
        </a>
      </div>

      <div className="p-5 space-y-5">
        {/* Per-Video Pricing */}
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Per Video Pricing
          </p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(data.plans || {}).map(([key, plan]) => (
              <div key={key} className="bg-white/4 rounded-xl p-3 border border-white/8">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`badge text-[11px] ${QUALITY_COLORS[plan.quality?.toLowerCase()] || 'bg-slate-500/20 text-slate-300'}`}>
                    {plan.quality}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  {plan.duration || plan.size} · {plan.resolution || '—'}
                </p>
                <p className="text-white font-bold mt-1">
                  ${plan.price_usd}
                  <span className="text-slate-400 font-normal text-xs ml-1">/ ₹{plan.price_inr}</span>
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Monthly Plan */}
        {recoPlan && (
          <div className="bg-gradient-to-r from-violet-500/15 to-cyan-500/10 border border-violet-500/25 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Star size={14} className="text-amber-400 fill-amber-400" />
              <span className="text-xs font-semibold text-amber-300 uppercase tracking-wider">Recommended Plan</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <p className="text-white font-bold text-lg">
                  {typeof recoPlan.price_usd === 'number' ? `$${recoPlan.price_usd}` : recoPlan.price_usd}
                  <span className="text-slate-400 font-normal text-sm">/month</span>
                </p>
                <p className="text-slate-400 text-xs mt-0.5">
                  {typeof recoPlan.price_inr === 'number' ? `₹${recoPlan.price_inr}/month` : recoPlan.note || ''}
                </p>
              </div>
              {recoPlan.videos_approx && (
                <div className="text-right">
                  <p className="text-cyan-400 font-bold">
                    ~{recoPlan.videos_approx === 'unlimited' ? '∞' : recoPlan.videos_approx}
                  </p>
                  <p className="text-xs text-slate-500">videos/month</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Toggle all subscription plans */}
        <button
          onClick={() => setShowPlans(!showPlans)}
          className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
        >
          {showPlans ? '▲ Hide' : '▼ Show'} all subscription plans
        </button>

        {showPlans && (
          <div className="space-y-2">
            {Object.entries(data.monthly_subscriptions || {}).map(([key, plan]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-white/3 rounded-lg border border-white/6">
                <div>
                  <p className="text-sm font-medium text-white capitalize">{key}</p>
                  {plan.credits && (
                    <p className="text-xs text-slate-500">
                      {plan.credits === 'unlimited' ? '∞ unlimited' : `${plan.credits} credits`}
                    </p>
                  )}
                  {plan.note && <p className="text-xs text-slate-500">{plan.note}</p>}
                </div>
                <div className="text-right">
                  <p className="text-white font-semibold">
                    {typeof plan.price_usd === 'number' ? `$${plan.price_usd}` : plan.price_usd}
                    {typeof plan.price_usd === 'number' && <span className="text-xs text-slate-400">/mo</span>}
                  </p>
                  {typeof plan.price_inr === 'number' && (
                    <p className="text-xs text-slate-500">₹{plan.price_inr}/mo</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function CostCalculator({ generators }) {
  const [gen, setGen] = useState('kling')
  const [duration, setDuration] = useState(10)
  const [videosPerMonth, setVideosPerMonth] = useState(150)

  const { data } = useQuery({
    queryKey: ['cost-estimate', gen, duration, videosPerMonth],
    queryFn: () => api.get('/pricing/estimate', {
      params: { generator: gen, duration_seconds: duration, videos_per_month: videosPerMonth }
    }),
  })

  const estimate = data?.data || {}

  return (
    <div className="glass-card p-6">
      <h3 className="font-semibold text-white flex items-center gap-2 mb-5">
        <Calculator size={18} className="text-violet-400" />
        Cost Calculator
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Video Generator</label>
          <select value={gen} onChange={e => setGen(e.target.value)} className="input-field">
            {Object.keys(generators).map(k => (
              <option key={k} value={k}>{generators[k]?.name || k}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Video Duration (seconds)</label>
          <select value={duration} onChange={e => setDuration(Number(e.target.value))} className="input-field">
            {[5, 6, 8, 10, 15, 16, 30, 60].map(d => (
              <option key={d} value={d}>{d}s</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Videos Per Month</label>
          <input
            type="number"
            value={videosPerMonth}
            onChange={e => setVideosPerMonth(Number(e.target.value))}
            min={1} max={1000}
            className="input-field"
          />
        </div>
      </div>

      {estimate.monthly_total_usd !== undefined && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Per Video', usd: estimate.per_video_usd, inr: estimate.per_video_inr },
            { label: 'Monthly', usd: estimate.monthly_total_usd, inr: estimate.monthly_total_inr },
            { label: 'Annual', usd: estimate.annual_total_usd, inr: estimate.annual_total_inr },
          ].map(item => (
            <div key={item.label} className="bg-white/5 rounded-xl p-4 border border-white/8 text-center">
              <p className="text-xs text-slate-400 mb-1">{item.label}</p>
              <p className="text-xl font-bold text-white">${item.usd}</p>
              <p className="text-sm text-violet-400">₹{item.inr}</p>
            </div>
          ))}
          <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-center">
            <p className="text-xs text-slate-400 mb-1">Tip</p>
            <p className="text-xs text-green-300 leading-relaxed">{estimate.tip}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default function AdminPricing() {
  const { data, isLoading } = useQuery({
    queryKey: ['video-pricing'],
    queryFn: () => api.get('/pricing/video-generators'),
  })

  const pricing = data?.data || {}
  const generators = pricing.generators || {}
  const monthly = pricing.monthly_estimate || {}
  const reco = pricing.recommendation || {}

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Video Generator Pricing</h1>
        <p className="text-slate-400 mt-1">Compare costs across all AI video and image generation platforms</p>
      </div>

      {/* Monthly Bundle Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(reco).map(([tier, plan]) => {
          const colors = { starter: 'border-green-500/30 bg-green-500/5', growth: 'border-violet-500/30 bg-violet-500/5', premium: 'border-amber-500/30 bg-amber-500/5' }
          const labels = { starter: '🌱 Starter', growth: '🚀 Growth', premium: '💎 Premium' }
          return (
            <div key={tier} className={`glass-card p-5 border ${colors[tier] || ''}`}>
              <p className="font-semibold text-white text-sm mb-3">{labels[tier] || tier}</p>
              <div className="space-y-1 mb-4">
                {plan.generators?.map(g => (
                  <p key={g} className="text-xs text-slate-400">• {g.replace(/_/g, ' ')}</p>
                ))}
              </div>
              <div>
                <p className="text-2xl font-bold text-white">${plan.monthly_usd}<span className="text-sm text-slate-400">/mo</span></p>
                <p className="text-violet-400 text-sm">₹{plan.monthly_inr}/month</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Dr. Anshu Monthly Estimate */}
      {monthly.estimated_costs && (
        <div className="glass-card p-6">
          <h3 className="font-semibold text-white mb-1">Estimated Monthly Cost for Dr. Anshu Gupta</h3>
          <p className="text-slate-400 text-sm mb-4">
            Based on {monthly.videos_per_month} videos/month + {monthly.images_per_month} images/month
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(monthly.estimated_costs).map(([tier, costs]) => (
              <div key={tier} className="bg-white/4 rounded-xl p-4 border border-white/8">
                <p className="text-xs font-semibold text-slate-400 uppercase mb-3 capitalize">{tier}</p>
                {Object.entries(costs).filter(([k]) => k !== 'total_usd' && k !== 'total_inr').map(([k, v]) => (
                  <div key={k} className="flex justify-between text-sm py-1">
                    <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}</span>
                    <span className="text-white">${v}</span>
                  </div>
                ))}
                <div className="border-t border-white/10 mt-2 pt-2 flex justify-between">
                  <span className="font-semibold text-white">Total</span>
                  <div className="text-right">
                    <span className="font-bold text-white">${costs.total_usd}</span>
                    <p className="text-xs text-violet-400">₹{costs.total_inr}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-3">{monthly.note}</p>
        </div>
      )}

      {/* Cost Calculator */}
      {Object.keys(generators).length > 0 && (
        <CostCalculator generators={generators} />
      )}

      {/* Generator Cards */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(generators).map(([key, data]) => (
          <GeneratorCard key={key} generatorKey={key} data={data} />
        ))}
      </div>

      {/* Disclaimer */}
      <div className="glass-card p-4 border-amber-500/20 bg-amber-500/5">
        <p className="text-xs text-amber-400/80">
          ⚠️ <strong className="text-amber-300">Disclaimer:</strong> Prices are approximate and subject to change.
          Exchange rate: 1 USD ≈ ₹83. Always verify current pricing on each platform's official website before subscribing.
          Prices last updated: June 2025.
        </p>
      </div>
    </div>
  )
}
