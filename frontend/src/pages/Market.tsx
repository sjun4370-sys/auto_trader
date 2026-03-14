import { useEffect, useState } from 'react'
import { Table, Input } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { marketApi, Ticker } from '../api/market'

function Market() {
  const [tickers, setTickers] = useState<Ticker[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await marketApi.getTickers()
      const data = Object.values(res.data).filter((t: any) => !t.error)
      setTickers(data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: '交易对', dataIndex: 'symbol', key: 'symbol' },
    { title: '最新价', dataIndex: 'last', key: 'last', render: (v: number) => v?.toFixed(2) },
    { title: '24h涨跌', dataIndex: 'change_percent', key: 'change_percent', render: (v: number) => (
      <span style={{ color: v >= 0 ? '#3f8600' : '#cf1322' }}>
        {v?.toFixed(2)}%
      </span>
    )},
    { title: '24h最高', dataIndex: 'high', key: 'high', render: (v: number) => v?.toFixed(2) },
    { title: '24h最低', dataIndex: 'low', key: 'low', render: (v: number) => v?.toFixed(2) },
    { title: '24h成交量', dataIndex: 'volume', key: 'volume', render: (v: number) => v?.toFixed(2) },
  ]

  return (
    <div>
      <h1>行情</h1>
      <Input
        placeholder="搜索交易对"
        prefix={<SearchOutlined />}
        style={{ marginBottom: 16, width: 300 }}
      />
      <Table
        columns={columns}
        dataSource={tickers}
        rowKey="symbol"
        loading={loading}
      />
    </div>
  )
}

export default Market
