import { useEffect, useState } from 'react'
import { Table, Button, Tag, Card, message, Space } from 'antd'
import { strategyApi, StrategyData } from '../api/strategy'

function Strategies() {
  const [strategies, setStrategies] = useState<StrategyData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await strategyApi.list()
      setStrategies(res.data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (id: number, isActive: boolean) => {
    try {
      if (isActive) {
        await strategyApi.stop(id)
      } else {
        await strategyApi.start(id)
      }
      loadData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const columns = [
    { title: '策略名称', dataIndex: 'name', key: 'name' },
    { title: '类型', dataIndex: 'strategy_type', key: 'strategy_type', render: (v: string) => <Tag>{v}</Tag> },
    { title: '总盈亏', dataIndex: 'total_pnl', key: 'total_pnl', render: (v: number) => (
      <span style={{ color: v >= 0 ? '#3f8600' : '#cf1322' }}>{v?.toFixed(2)}</span>
    )},
    { title: '胜率', dataIndex: 'win_rate', key: 'win_rate', render: (v: number) => `${v?.toFixed(1)}%` },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => (
      <Tag color={v ? 'green' : 'default'}>{v ? '运行中' : '已停止'}</Tag>
    )},
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
    { title: '操作', key: 'action', render: (_: any, record: StrategyData) => (
      <Space>
        <Button size="small" type={record.is_active ? 'default' : 'primary'} onClick={() => handleToggle(record.id, record.is_active)}>
          {record.is_active ? '停止' : '启动'}
        </Button>
        <Button size="small" danger>删除</Button>
      </Space>
    )},
  ]

  return (
    <div>
      <h1>策略</h1>
      <Card>
        <Button type="primary" style={{ marginBottom: 16 }}>创建策略</Button>
        <Table columns={columns} dataSource={strategies} rowKey="id" loading={loading} />
      </Card>
    </div>
  )
}

export default Strategies
