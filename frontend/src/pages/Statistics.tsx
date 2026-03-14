import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic } from 'antd'

function Statistics() {
  const [stats, setStats] = useState({
    total_pnl: 0,
    today_pnl: 0,
    win_rate: 0,
    total_trades: 0,
    winning_trades: 0,
    losing_trades: 0,
  })

  useEffect(() => {
    // 模拟数据
    setStats({
      total_pnl: 15678.88,
      today_pnl: 1234.56,
      win_rate: 68.5,
      total_trades: 156,
      winning_trades: 107,
      losing_trades: 49,
    })
  }, [])

  return (
    <div>
      <h1>统计</h1>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="总盈亏" value={stats.total_pnl} precision={2} suffix="USDT" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="今日盈亏" value={stats.today_pnl} precision={2} suffix="USDT" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="胜率" value={stats.win_rate} precision={1} suffix="%" />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic title="总交易次数" value={stats.total_trades} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="盈利次数" value={stats.winning_trades} valueStyle={{ color: '#3f8600' }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="亏损次数" value={stats.losing_trades} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Statistics
