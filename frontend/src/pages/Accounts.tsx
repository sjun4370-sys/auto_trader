import { useEffect, useState } from 'react'
import { Card, Table, Tag, Form, Input, Switch, Button, message, Row, Col, Alert } from 'antd'
import { accountApi, AccountData } from '../api/account'

function Accounts() {
  const [accounts, setAccounts] = useState<AccountData[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form] = Form.useForm()

  const loadAccounts = async () => {
    setLoading(true)
    try {
      const res = await accountApi.list()
      setAccounts(res.data)
    } catch (error) {
      console.error(error)
      message.error('加载账户列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAccounts()
  }, [])

  const onFinish = async (values: Partial<AccountData>) => {
    setSubmitting(true)
    try {
      await accountApi.create(values)
      message.success('账户创建成功')
      form.resetFields()
      loadAccounts()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '账户创建失败')
    } finally {
      setSubmitting(false)
    }
  }

  const columns = [
    { title: '交易所', dataIndex: 'exchange', key: 'exchange' },
    { title: '账户名', dataIndex: 'account_name', key: 'account_name', render: (v: string) => v || '-' },
    {
      title: '网络',
      dataIndex: 'is_testnet',
      key: 'is_testnet',
      render: (v: boolean) => <Tag color={v ? 'orange' : 'green'}>{v ? '模拟盘' : '实盘'}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '启用' : '停用'}</Tag>,
    },
    {
      title: '可交易',
      dataIndex: 'has_api_credentials',
      key: 'has_api_credentials',
      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '是' : '否（缺少密钥）'}</Tag>,
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  ]

  return (
    <div>
      <h1>账户管理</h1>
      <Row gutter={16}>
        <Col xs={24} lg={14}>
          <Card title="账户列表">
            <Table columns={columns} dataSource={accounts} rowKey="id" loading={loading} />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="新增账户">
            <Alert type="info" showIcon message="账户需配置 API Key 和 API Secret 才能用于交易" style={{ marginBottom: 16 }} />
            <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ is_testnet: true }}>
              <Form.Item name="exchange" label="Exchange" rules={[{ required: true, message: '请输入 exchange' }]}>
                <Input placeholder="例如 binance" />
              </Form.Item>
              <Form.Item name="account_name" label="Account Name">
                <Input placeholder="例如 主账户" />
              </Form.Item>
              <Form.Item name="api_key" label="API Key" rules={[{ required: true, message: '请输入 api_key' }]}>
                <Input />
              </Form.Item>
              <Form.Item name="api_secret" label="API Secret" rules={[{ required: true, message: '请输入 api_secret' }]}>
                <Input.Password />
              </Form.Item>
              <Form.Item name="passphrase" label="Passphrase">
                <Input.Password />
              </Form.Item>
              <Form.Item name="is_testnet" label="Is Testnet" valuePropName="checked">
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={submitting}>
                  新增账户
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Accounts
