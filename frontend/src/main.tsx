import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
      <ConfigProvider
        theme={{
          algorithm: theme.darkAlgorithm,
          token: {
            colorPrimary: '#fff',
            colorBgContainer: 'rgba(30,30,30,0.7)',
            colorBgElevated: 'rgba(40,40,40,0.8)',
            colorBgLayout: '#000000',
            colorBorder: 'rgba(255,255,255,0.1)',
            colorText: '#ffffff',
            colorTextSecondary: 'rgba(255,255,255,0.65)',
            borderRadius: 8,
          },
        }}
      >
        <App />
      </ConfigProvider>
    </BrowserRouter>
)
