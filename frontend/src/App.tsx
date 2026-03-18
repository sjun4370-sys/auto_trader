import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout, Drawer } from 'antd'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import BackgroundDecoration from './components/BackgroundDecoration'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Trade from './pages/Trade'
import Positions from './pages/Positions'
import Strategies from './pages/Strategies'
import Statistics from './pages/Statistics'
import AIAssistant from './pages/AIAssistant'
import Accounts from './pages/Accounts'

const { Content } = Layout

// 响应式断点
const BREAKPOINT = 768

// 监听 localStorage 变化的 key
const TOKEN_KEY = 'token'

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [isMobile, setIsMobile] = useState(false)
  const [drawerVisible, setDrawerVisible] = useState(false)

  // 监听 localStorage 变化（用于跨标签页同步）
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === TOKEN_KEY) {
        setToken(e.newValue)
      }
    }

    // 监听自定义事件（用于同标签页内的 token 变化）
    const handleTokenChange = () => {
      setToken(localStorage.getItem(TOKEN_KEY))
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('token-change', handleTokenChange)
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('token-change', handleTokenChange)
    }
  }, [])

  // 监听屏幕宽度变化
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < BREAKPOINT)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // 移动端菜单点击后关闭抽屉
  const handleMenuClick = () => {
    if (isMobile) {
      setDrawerVisible(false)
    }
  }

  if (!token) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    )
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#000000' }}>
      {/* 背景装饰 */}
      <BackgroundDecoration />
      <Header
        isMobile={isMobile}
        onMenuClick={() => setDrawerVisible(true)}
      />
      <Layout>
        {/* PC端显示左侧菜单，移动端使用抽屉 */}
        {isMobile ? (
          <Drawer
            placement="left"
            onClose={() => setDrawerVisible(false)}
            open={drawerVisible}
            width={200}
            bodyStyle={{ padding: 0 }}
          >
            <Sidebar onMenuClick={handleMenuClick} />
          </Drawer>
        ) : (
          <Sidebar />
        )}

        <Layout style={{ padding: isMobile ? '12px' : '24px', background: '#000' }}>
          <Content
            style={{
              padding: 0,
              margin: 0,
              minHeight: 280,
              background: '#000',
              color: '#fff'
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
              <Route path="/accounts" element={<Accounts />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default App
