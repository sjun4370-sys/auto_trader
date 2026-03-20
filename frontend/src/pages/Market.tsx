import { useEffect, useState } from 'react'
import { Table } from 'antd'
import { marketApi, Ticker } from '../api/market'

function Market() {
  const [tickers, setTickers] = useState<Ticker[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    loadData(controller.signal)
    return () => controller.abort()
  }, [])

  const loadData = async (signal?: AbortSignal) => {
    setLoading(true)
    try {
      const res = await marketApi.getTickers({ signal })
      const data = Object.values(res.data as Record<string, Ticker>).filter((t: Ticker) => !(t as any).error)
      setTickers(data)
    } catch (error) {
      if ((error as Error).name === 'AbortError') return
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
