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
        title={null}
        className="strategy-modal"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={400}
        style={{ top: 60 }}
        centered
      >
        <div className="strategy-modal-inner">
          <div className="strategy-modal-header">
            <span className="strategy-modal-icon">✦</span>
            <h2 className="strategy-modal-title">创建策略</h2>
          </div>

          <Form form={form} onFinish={handleCreate} layout="vertical" className="strategy-form">
            <Form.Item name="name" rules={[{ required: true, message: '请输入策略名称' }]}>
              <Input
                placeholder="策略名称"
                className="strategy-input"
              />
            </Form.Item>
            <Form.Item name="strategy_type" rules={[{ required: true, message: '请选择策略类型' }]}>
              <Select
                placeholder="选择策略类型"
                className="strategy-select"
              >
                <Select.Option value="grid">网格交易</Select.Option>
                <Select.Option value="trend">趋势跟踪</Select.Option>
                <Select.Option value="arbitrage">套利</Select.Option>
              </Select>
            </Form.Item>

            <div className="strategy-modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setModalVisible(false)}>
                取消
              </button>
              <button type="submit" className="btn-create">
                创建
              </button>
            </div>
          </Form>
        </div>
      </Modal>

      <style>{`
        .strategy-modal .ant-modal-content {
          background: rgba(22,22,22,0.96) !important;
          border: 1px solid rgba(255,255,255,0.08) !important;
          border-radius: 14px !important;
          box-shadow: 0 20px 60px rgba(0,0,0,0.55), 0 0 1px rgba(255,255,255,0.05) inset !important;
        }
        .strategy-modal .ant-modal-close {
          display: none !important;
        }
        .strategy-modal-inner {
          padding: 0 !important;
        }
        .strategy-modal-header {
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          padding: 18px 22px !important;
          border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        }
        .strategy-modal-icon {
          width: 28px !important;
          height: 28px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          background: rgba(255,255,255,0.06) !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 7px !important;
          color: rgba(255,255,255,0.6) !important;
          font-size: 13px !important;
        }
        .strategy-modal-title {
          font-size: 15px !important;
          font-weight: 600 !important;
          color: #fff !important;
          margin: 0 !important;
        }
        .strategy-form {
          padding: 16px 22px 20px !important;
          margin: 0 !important;
        }
        .strategy-form .ant-form-item {
          margin-bottom: 12px !important;
        }
        .strategy-form .ant-form-item:last-child {
          margin-bottom: 0 !important;
        }
        .strategy-input {
          height: 40px !important;
          background: rgba(255,255,255,0.04) !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 8px !important;
          color: #fff !important;
          font-size: 14px !important;
        }
        .strategy-input:hover, .strategy-input:focus {
          border-color: rgba(255,255,255,0.18) !important;
        }
        .strategy-input::placeholder {
          color: rgba(255,255,255,0.3) !important;
        }
        .strategy-select .ant-select-selector {
          height: 40px !important;
          background: rgba(255,255,255,0.04) !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 8px !important;
          font-size: 14px !important;
        }
        .strategy-select .ant-select-selector:hover {
          border-color: rgba(255,255,255,0.18) !important;
        }
        .strategy-select .ant-select-placeholder {
          color: rgba(255,255,255,0.3) !important;
        }
        .strategy-select .ant-select-arrow {
          color: rgba(255,255,255,0.4) !important;
        }
        .strategy-modal-actions {
          display: flex !important;
          gap: 10px !important;
          margin-top: 16px !important;
        }
        .btn-cancel {
          flex: 1 !important;
          height: 38px !important;
          background: transparent !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 8px !important;
          color: rgba(255,255,255,0.65) !important;
          font-size: 14px !important;
          cursor: pointer !important;
        }
        .btn-cancel:hover {
          border-color: rgba(255,255,255,0.18) !important;
          color: #fff !important;
        }
        .btn-create {
          flex: 1 !important;
          height: 38px !important;
          background: #fff !important;
          border: none !important;
          border-radius: 8px !important;
          color: #000 !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          cursor: pointer !important;
        }
        .btn-create:hover {
          background: rgba(255,255,255,0.92) !important;
        }
      `}</style>
    </div>
  )
}

export default Strategies
