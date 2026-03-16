import { useEffect, useState } from 'react'
import { Table, Button, Tag, Card, message, Space, Modal, Form, Input, Select, Popconfirm } from 'antd'
import { strategyApi, StrategyData } from '../api/strategy'

function Strategies() {
  const [strategies, setStrategies] = useState<StrategyData[]>([])
  const [loading, setLoading] = useState(true)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

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

  const handleDelete = async (id: number) => {
    try {
      await strategyApi.delete(id)
      message.success('删除成功')
      loadData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleCreate = async (values: { name: string; strategy_type: string }) => {
    try {
      // 构建 config 字段
      const config: Record<string, any> = {}
      if (values.strategy_type === 'grid') {
        config.symbol = 'BTC/USDT:USDT'
        config.grid_count = 10
        config.price_range = 1000
      } else if (values.strategy_type === 'trend') {
        config.symbol = 'BTC/USDT:USDT'
        config.indicators = ['MA', 'MACD']
      } else if (values.strategy_type === 'arbitrage') {
        config.symbol = 'BTC/USDT:USDT'
        config.spread_threshold = 0.5
      }

      await strategyApi.create({
        name: values.name,
        strategy_type: values.strategy_type,
        config
      })
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error) {
      message.error('创建失败')
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
        <Popconfirm
          title="确认删除"
          description="确定要删除这个策略吗？"
          onConfirm={() => handleDelete(record.id)}
          okText="确认"
          cancelText="取消"
        >
          <Button size="small" danger>删除</Button>
        </Popconfirm>
      </Space>
    )},
  ]

  return (
    <div>
      <h1>策略</h1>
      <Card>
        <Button type="primary" style={{ marginBottom: 16 }} onClick={() => setModalVisible(true)}>创建策略</Button>
        <Table columns={columns} dataSource={strategies} rowKey="id" loading={loading} />
      </Card>

      <Modal
        title="创建策略"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={form.submit}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="策略名称" rules={[{ required: true, message: '请输入策略名称' }]}>
            <Input placeholder="请输入策略名称" />
          </Form.Item>
          <Form.Item name="strategy_type" label="策略类型" rules={[{ required: true, message: '请选择策略类型' }]}>
            <Select placeholder="请选择策略类型">
              <Select.Option value="grid">网格交易</Select.Option>
              <Select.Option value="trend">趋势跟踪</Select.Option>
              <Select.Option value="arbitrage">套利</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Strategies
