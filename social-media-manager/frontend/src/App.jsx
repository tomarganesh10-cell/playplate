import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

import Login from './pages/Login'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminCredentials from './pages/admin/AdminCredentials'
import AdminKnowledgeBase from './pages/admin/AdminKnowledgeBase'
import AdminSettings from './pages/admin/AdminSettings'

import ClientLayout from './pages/client/ClientLayout'
import ClientDashboard from './pages/client/ClientDashboard'
import ApprovalQueue from './pages/client/ApprovalQueue'
import ContentCalendar from './pages/client/ContentCalendar'
import PostsLibrary from './pages/client/PostsLibrary'
import AnalyticsDashboard from './pages/client/AnalyticsDashboard'
import ClientSettings from './pages/client/ClientSettings'

function PrivateRoute({ children, adminOnly = false }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && user.role !== 'super_admin') return <Navigate to="/client" replace />
  return children
}

function RootRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'super_admin') return <Navigate to="/admin" replace />
  return <Navigate to="/client" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<RootRedirect />} />

        {/* Admin Routes */}
        <Route path="/admin" element={<PrivateRoute adminOnly><AdminLayout /></PrivateRoute>}>
          <Route index element={<AdminDashboard />} />
          <Route path="credentials" element={<AdminCredentials />} />
          <Route path="knowledge-base" element={<AdminKnowledgeBase />} />
          <Route path="settings" element={<AdminSettings />} />
        </Route>

        {/* Client Routes */}
        <Route path="/client" element={<PrivateRoute><ClientLayout /></PrivateRoute>}>
          <Route index element={<ClientDashboard />} />
          <Route path="approval" element={<ApprovalQueue />} />
          <Route path="calendar" element={<ContentCalendar />} />
          <Route path="posts" element={<PostsLibrary />} />
          <Route path="analytics" element={<AnalyticsDashboard />} />
          <Route path="settings" element={<ClientSettings />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
