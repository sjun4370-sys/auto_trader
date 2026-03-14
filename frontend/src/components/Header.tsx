import { Layout, Button, Space } from 'antd'
import { LogoutOutlined, UserOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Header } = Layout

function HeaderComponent() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', background: '#001529', padding: '0 24px' }}>
      <Space>
        <Button type="text" icon={<UserOutlined />} style={{ color: '#fff' }}>
          个人中心
        </Button>
        <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout} style={{ color: '#fff' }}>
          退出
        </Button>
      </Space>
    </Header>
  )
}

export default HeaderComponent
