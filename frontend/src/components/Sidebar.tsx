import { useState, useEffect, useRef } from 'react'
import { Layout, Menu } from 'antd'
import type { MenuProps } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  LineChartOutlined,
  SwapOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  RobotOutlined,
  BankOutlined,
  WalletOutlined,
} from '@ant-design/icons'

const { Sider } = Layout

interface SidebarProps {
  onMenuClick?: () => void
}

// 菜单项配置
const menuItemsList = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/market', icon: <LineChartOutlined />, label: '行情' },
  { key: '/trade', icon: <SwapOutlined />, label: '交易' },
  { key: '/positions', icon: <WalletOutlined />, label: '持仓' },
  { key: '/strategies', icon: <ExperimentOutlined />, label: '策略' },
  { key: '/statistics', icon: <BarChartOutlined />, label: '统计' },
  { key: '/ai', icon: <RobotOutlined />, label: 'AI助手' },
  { key: '/accounts', icon: <BankOutlined />, label: '账户' },
]

// 根据索引计算位置（指示器36px，菜单项40px，居中对齐）
// 公式：index * 间距 + 首个菜单项的GAP + 居中偏移
const getItemTop = (index: number) => {
  const ITEM_HEIGHT = 40
  const GAP = 4
  const INDICATOR_HEIGHT = 36
  const offset = (ITEM_HEIGHT - INDICATOR_HEIGHT) / 2 // 居中偏移 = 2
  return index * (ITEM_HEIGHT + GAP) + GAP + offset // 5*44+4+2 = 230
}

function Sidebar({ onMenuClick }: SidebarProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const [indicatorTop, setIndicatorTop] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const prevKeyRef = useRef(location.pathname)
  const animatingRef = useRef(false)
  const timeoutRef = useRef<number | null>(null)

  const menuItems: MenuProps['items'] = menuItemsList

  // 初始化位置
  useEffect(() => {
    const index = menuItemsList.findIndex(item => item.key === location.pathname)
    if (index !== -1) {
      setIndicatorTop(getItemTop(index))
    }
    prevKeyRef.current = location.pathname

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  // 监听路由变化
  useEffect(() => {
    const currentKey = location.pathname
    const prevKey = prevKeyRef.current

    if (currentKey !== prevKey) {
      // 如果正在动画中，先清除待执行的timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }

      if (animatingRef.current) {
        // 动画被打断：从当前位置直接滑到新目标（保持动画继续）
        const newIndex = menuItemsList.findIndex(item => item.key === currentKey)
        if (newIndex !== -1) {
          setIndicatorTop(getItemTop(newIndex))
          // 动画继续，不重置isAnimating
        }
        prevKeyRef.current = currentKey
        return
      }

      // 正常动画流程
      const prevIndex = menuItemsList.findIndex(item => item.key === prevKey)
      if (prevIndex !== -1) {
        setIndicatorTop(getItemTop(prevIndex))
      }
      setIsAnimating(false)

      // 短暂延迟后设置到目标位置（有动画）
      timeoutRef.current = window.setTimeout(() => {
        const newIndex = menuItemsList.findIndex(item => item.key === currentKey)
        if (newIndex !== -1) {
          setIndicatorTop(getItemTop(newIndex))
          setIsAnimating(true)
          animatingRef.current = true

          // 动画结束后重置
          setTimeout(() => {
            setIsAnimating(false)
            animatingRef.current = false
          }, 400)
        }
        prevKeyRef.current = currentKey
        timeoutRef.current = null
      }, 50)
    }
  }, [location.pathname])

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
    onMenuClick?.()
  }

  return (
    <Sider width={200} style={{
      background: 'rgba(20,20,20,0.8)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderRight: '1px solid rgba(255,255,255,0.08)',
      position: 'relative'
    }}>
      {/* 流淌指示器 */}
      <div
        style={{
          position: 'absolute',
          top: `${indicatorTop}px`,
          left: '8px',
          right: '8px',
          height: '36px',
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '8px',
          backdropFilter: 'blur(16px) saturate(180%)',
          WebkitBackdropFilter: 'blur(16px) saturate(180%)',
          boxShadow: isAnimating ? '0 0 20px rgba(255,255,255,0.15)' : 'none',
          transition: isAnimating
            ? 'top 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease'
            : 'none',
          zIndex: 0,
          pointerEvents: 'none',
        }}
      />

      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        theme="dark"
        style={{
          height: '100%',
          borderRight: 0,
          background: 'transparent',
          position: 'relative',
          zIndex: 1,
        }}
        items={menuItems}
        onClick={handleMenuClick}
        className="glass-sidebar-menu"
      />

      {/* 自定义样式覆盖 */}
      <style>{`
        .glass-sidebar-menu.ant-menu-dark .ant-menu-item {
          height: 40px !important;
          line-height: 40px !important;
          color: rgba(255, 255, 255, 0.65);
        }
        .glass-sidebar-menu.ant-menu-dark .ant-menu-item:hover {
          color: #fff;
        }
        .glass-sidebar-menu.ant-menu-dark .ant-menu-item-selected {
          color: #fff !important;
          background: transparent !important;
        }
        .glass-sidebar-menu.ant-menu-dark .ant-menu-item-selected::after {
          display: none !important;
        }
      `}</style>
    </Sider>
  )
}

export default Sidebar
