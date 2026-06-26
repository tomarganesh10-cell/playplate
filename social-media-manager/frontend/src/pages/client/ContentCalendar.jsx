import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../../api/client'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { format, getDaysInMonth, startOfMonth, getDay } from 'date-fns'

const PLATFORM_COLORS = {
  instagram_post: 'bg-pink-500',
  facebook_post: 'bg-blue-600',
  linkedin_post: 'bg-blue-800',
  instagram_reel: 'bg-purple-600',
  youtube_short: 'bg-red-600',
}

export default function ContentCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date())

  const { data } = useQuery({
    queryKey: ['calendar', currentDate.getFullYear(), currentDate.getMonth() + 1],
    queryFn: () => analyticsApi.calendar(currentDate.getFullYear(), currentDate.getMonth() + 1),
  })

  const calendarData = data?.data?.days || {}
  const daysInMonth = getDaysInMonth(currentDate)
  const firstDayOfWeek = getDay(startOfMonth(currentDate))
  const today = new Date()

  const prevMonth = () => setCurrentDate(d => new Date(d.getFullYear(), d.getMonth() - 1, 1))
  const nextMonth = () => setCurrentDate(d => new Date(d.getFullYear(), d.getMonth() + 1, 1))

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Content Calendar</h1>
          <p className="text-slate-400 mt-1">Scheduled and published content</p>
        </div>
      </div>

      <div className="glass-card p-6">
        {/* Calendar Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            {format(currentDate, 'MMMM yyyy')}
          </h2>
          <div className="flex gap-2">
            <button onClick={prevMonth} className="btn-secondary py-2 px-3">
              <ChevronLeft size={18} />
            </button>
            <button onClick={nextMonth} className="btn-secondary py-2 px-3">
              <ChevronRight size={18} />
            </button>
          </div>
        </div>

        {/* Day Names */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {dayNames.map(d => (
            <div key={d} className="text-center text-xs font-semibold text-slate-500 py-2">{d}</div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {/* Empty cells before first day */}
          {Array.from({ length: firstDayOfWeek }).map((_, i) => (
            <div key={`empty-${i}`} className="min-h-[80px]" />
          ))}

          {/* Days */}
          {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
            const dayPosts = calendarData[day] || []
            const isToday = today.getDate() === day &&
              today.getMonth() === currentDate.getMonth() &&
              today.getFullYear() === currentDate.getFullYear()

            return (
              <div
                key={day}
                className={`min-h-[80px] rounded-xl p-2 border transition-colors
                  ${isToday
                    ? 'border-violet-500/50 bg-violet-500/10'
                    : 'border-white/5 bg-white/3 hover:bg-white/6'
                  }`}
              >
                <span className={`text-sm font-semibold ${isToday ? 'text-violet-300' : 'text-slate-400'}`}>
                  {day}
                </span>
                <div className="mt-1 space-y-1">
                  {dayPosts.slice(0, 3).map((post, i) => (
                    <div
                      key={i}
                      className={`${PLATFORM_COLORS[post.platform] || 'bg-slate-600'} rounded px-1.5 py-0.5 text-[10px] text-white truncate`}
                    >
                      {post.time} {post.title?.slice(0, 15)}
                    </div>
                  ))}
                  {dayPosts.length > 3 && (
                    <div className="text-[10px] text-slate-500 pl-1">+{dayPosts.length - 3} more</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="glass-card p-4">
        <p className="text-sm font-medium text-slate-300 mb-3">Platforms</p>
        <div className="flex flex-wrap gap-3">
          {Object.entries(PLATFORM_COLORS).map(([platform, color]) => (
            <div key={platform} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded ${color}`} />
              <span className="text-xs text-slate-400">{platform.replace(/_/g, ' ')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
