import { Layout, Button, Space } from 'antd'
import { LogoutOutlined, UserOutlined, MenuOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Header } = Layout

interface HeaderProps {
  isMobile?: boolean
  onMenuClick?: () => void
}

function HeaderComponent({ isMobile, onMenuClick }: HeaderProps) {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    // 触发自定义事件通知 App 组件 token 已变化
    window.dispatchEvent(new Event('token-change'))
    navigate('/login')
  }

  return (
    <Header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: isMobile ? 'space-between' : 'flex-end',
      background: 'rgba(20,20,20,0.8)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      padding: isMobile ? '0 12px' : '0 24px'
    }}>
      {/* 移动端显示汉堡菜单按钮 */}
      {isMobile && (
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={onMenuClick}
          style={{ color: '#fff', fontSize: 18 }}
        />
      )}

      <Space>
        <Button type="text" icon={<UserOutlined />} style={{ color: 'rgba(255,255,255,0.8)' }}>
          {isMobile ? '' : '个人中心'}
        </Button>
        <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout} style={{ color: 'rgba(255,255,255,0.8)' }}>
          {isMobile ? '' : '退出'}
        </Button>
      </Space>
    </Header>
  )
}

export default HeaderComponent
