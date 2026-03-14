import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Trade from './pages/Trade'
import Positions from './pages/Positions'
import Strategies from './pages/Strategies'
import Statistics from './pages/Statistics'
import AIAssistant from './pages/AIAssistant'

const { Content } = Layout

function App() {
  const token = localStorage.getItem('token');

  return token ? (
    <Layout style={{ minHeight: '100vh' }}>
      <Header />
      <Layout>
        <Sidebar />
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/market" element={<Market />} />
              <Route path="/trade" element={<Trade />} />
              <Route path="/positions" element={<Positions />} />
              <Route path="/strategies" element={<Strategies />} />
              <Route path="/statistics" element={<Statistics />} />
              <Route path="/ai" element={<AIAssistant />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  ) : (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  )
}

export default App
