import { Layout, Menu } from 'antd'
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

function Sidebar({ onMenuClick }: SidebarProps) {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
    { key: '/market', icon: <LineChartOutlined />, label: '行情' },
    { key: '/trade', icon: <SwapOutlined />, label: '交易' },
    { key: '/positions', icon: <WalletOutlined />, label: '持仓' },
    { key: '/strategies', icon: <ExperimentOutlined />, label: '策略' },
    { key: '/statistics', icon: <BarChartOutlined />, label: '统计' },
    { key: '/ai', icon: <RobotOutlined />, label: 'AI助手' },
    { key: '/accounts', icon: <BankOutlined />, label: '账户' },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
    onMenuClick?.()
  }

  return (
    <Sider width={200} style={{ background: '#fff' }}>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        style={{ height: '100%', borderRight: 0 }}
        items={menuItems}
        onClick={handleMenuClick}
      />
    </Sider>
  )
}

export default Sidebar
