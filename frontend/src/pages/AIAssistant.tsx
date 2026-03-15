import { useState } from 'react'
import { Card, Input, List, Avatar } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

function AIAssistant() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: 'assistant',
      content: '您好！我是AI交易助手，可以帮您分析市场、解读策略、回答交易问题。有什么可以帮您的？',
      timestamp: new Date(),
    },
  ])

  const handleSend = () => {
    if (!input.trim()) return

    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }
    setMessages([...messages, userMsg])
    setInput('')

    // 模拟AI回复
    setTimeout(() => {
      const aiMsg: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '感谢您的提问！AI对话功能正在开发中，敬请期待...',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, aiMsg])
    }, 1000)
  }

  return (
    <div>
      <h1>AI助手</h1>
      <Card style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflow: 'auto', marginBottom: 16 }}>
          <List
            dataSource={messages}
            renderItem={(item) => (
              <List.Item style={{ justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <Card
                  size="small"
                  style={{
                    maxWidth: '70%',
                    background: item.role === 'user' ? '#1890ff' : '#f0f0f0',
                    color: item.role === 'user' ? '#fff' : '#000',
                  }}
                >
                  <Avatar
                    icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ marginRight: 8 }}
                  />
                  {item.content}
                </Card>
              </List.Item>
            )}
          />
        </div>
        <Input.Search
          placeholder="输入您的问题..."
          enterButton={<SendOutlined />}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onSearch={handleSend}
        />
      </Card>
    </div>
  )
}

export default AIAssistant
