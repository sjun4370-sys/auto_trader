import { useEffect, useState } from 'react'
import { Table, Button, Tag, message } from 'antd'
import { positionApi, PositionData } from '../api/position'

function Positions() {
  const [positions, setPositions] = useState<PositionData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await positionApi.list('open')
      setPositions(res.data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = async (id: number) => {
    try {
      await positionApi.close(id)
      message.success('平仓成功')
      loadData()
    } catch (error) {
      message.error('平仓失败')
    }
  }

  const columns = [
    { title: '交易对', dataIndex: 'symbol', key: 'symbol' },
    { title: '方向', dataIndex: 'side', key: 'side', render: (v: string) => (
      <Tag color={v === 'long' ? 'green' : 'red'}>{v === 'long' ? '多' : '空'}</Tag>
    )},
    { title: '数量', dataIndex: 'quantity', key: 'quantity' },
    { title: '开仓价', dataIndex: 'entry_price', key: 'entry_price' },
    { title: '当前价', dataIndex: 'current_price', key: 'current_price' },
    { title: '杠杆', dataIndex: 'leverage', key: 'leverage', render: (v: number) => `${v}x` },
    { title: '未实现盈亏', dataIndex: 'unrealized_pnl', key: 'unrealized_pnl', render: (v: number) => (
      <span style={{ color: v >= 0 ? '#3f8600' : '#cf1322' }}>{v?.toFixed(2)}</span>
    )},
    { title: '状态', dataIndex: 'status', key: 'status' },
    { title: '操作', key: 'action', render: (_: any, record: PositionData) => (
      <Button size="small" danger onClick={() => handleClose(record.id)}>
        平仓
      </Button>
    )},
  ]

  return (
    <div>
      <h1>持仓</h1>
      <Table columns={columns} dataSource={positions} rowKey="id" loading={loading} />
    </div>
  )
}

export default Positions
