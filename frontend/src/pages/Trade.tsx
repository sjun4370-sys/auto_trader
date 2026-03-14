import { useState } from 'react'
import { Card, Form, Input, Select, InputNumber, Button, message, Space } from 'antd'
import { tradeApi } from '../api/trade'
import { accountApi } from '../api/account'

function Trade() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [accounts, setAccounts] = useState<any[]>([])

  useState(() => {
    accountApi.list().then(res => setAccounts(res.data))
  })

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      await tradeApi.createOrder(values, values.accountId)
      message.success('下单成功')
      form.resetFields()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '下单失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>交易</h1>
      <Card title="下单">
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="accountId" label="账户" rules={[{ required: true }]}>
            <Select placeholder="选择账户">
              {accounts.map(a => (
                <Select.Option key={a.id} value={a.id}>
                  {a.account_name || a.exchange} ({a.is_testnet ? '模拟' : '实盘'})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="symbol" label="交易对" rules={[{ required: true }]}>
            <Input placeholder="如 BTC/USDT" />
          </Form.Item>
          <Form.Item name="side" label="方向" rules={[{ required: true }]}>
            <Select placeholder="选择方向">
              <Select.Option value="buy">买入</Select.Option>
              <Select.Option value="sell">卖出</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="order_type" label="订单类型" rules={[{ required: true }]}>
            <Select placeholder="选择类型">
              <Select.Option value="market">市价单</Select.Option>
              <Select.Option value="limit">限价单</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="quantity" label="数量" rules={[{ required: true }]}>
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="price" label="价格（限价单）">
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                下单
              </Button>
              <Button onClick={() => form.resetFields()}>重置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default Trade
