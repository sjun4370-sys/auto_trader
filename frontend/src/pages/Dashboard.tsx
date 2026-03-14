import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

function Dashboard() {
  const [data, setData] = useState([])

  useEffect(() => {
    // 模拟数据
    const mockData = Array.from({ length: 24 }, (_, i) => ({
      time: `${i}:00`,
      value: Math.random() * 1000 + 5000,
    }))
    setData(mockData)
  }, [])

  return (
    <div>
      <h1>仪表盘</h1>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总资产 (USDT)"
              value={52568.88}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日盈亏"
              value={1234.56}
              precision={2}
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="持仓数量"
              value={5}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="胜率"
              value={68.5}
              precision={1}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>
      <Card title="收益曲线" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#1890ff" />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </div>
  )
}

export default Dashboard
