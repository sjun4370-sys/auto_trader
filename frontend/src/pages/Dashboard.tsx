import { useEffect, useState } from 'react'
import { Row, Col, Statistic } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

function Dashboard() {
  const [data, setData] = useState<{time: string; value: number}[]>([])

  useEffect(() => {
    // 模拟数据
    const mockData = Array.from({ length: 24 }, (_, i) => ({
      time: `${i}:00`,
      value: Math.random() * 1000 + 5000,
    }))
    setData(mockData)
  }, [])

  const cardStyle: React.CSSProperties = {
    background: 'rgba(30,30,30,0.7)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '12px',
    padding: '20px',
  }

  const titleStyle: React.CSSProperties = {
    color: 'rgba(255,255,255,0.6)',
    fontSize: '13px',
    marginBottom: '8px',
  }

  const valueStyle: React.CSSProperties = {
    color: '#FFFFFF',
    fontSize: '24px',
    fontWeight: 600,
  }

  return (
    <div style={{ color: '#fff' }}>
      <h1 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '24px', color: '#fff' }}>仪表盘</h1>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <div style={cardStyle}>
            <div style={titleStyle}>总资产 (USDT)</div>
            <div style={{ ...valueStyle, color: '#22c55e' }}>52,568.88</div>
          </div>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <div style={cardStyle}>
            <div style={titleStyle}>今日盈亏</div>
            <div style={{ ...valueStyle, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ArrowUpOutlined style={{ color: '#22c55e', fontSize: '14px' }} />
              <span style={{ color: '#22c55e' }}>+1,234.56</span>
            </div>
          </div>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <div style={cardStyle}>
            <div style={titleStyle}>持仓数量</div>
            <div style={valueStyle}>5</div>
          </div>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <div style={cardStyle}>
            <div style={titleStyle}>胜率</div>
            <div style={{ ...valueStyle, color: '#22c55e' }}>68.5%</div>
          </div>
        </Col>
      </Row>
      <div style={{ ...cardStyle, marginTop: '16px' }}>
        <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: '16px', color: 'rgba(255,255,255,0.8)' }}>收益曲线</div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <XAxis dataKey="time" stroke="rgba(255,255,255,0.4)" />
            <YAxis stroke="rgba(255,255,255,0.4)" />
            <Tooltip
              contentStyle={{
                background: 'rgba(0,0,0,0.8)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Line type="monotone" dataKey="value" stroke="#fff" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default Dashboard
