/**
 * @author Jun
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, ShieldCheck, Sparkles, Apple, Github } from 'lucide-react'
import { message } from 'antd'
import { authApi } from '../api/auth'

function Login() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    remember: false
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authApi.login(formData)
      localStorage.setItem('token', res.data.access_token)
      window.dispatchEvent(new Event('token-change'))
      message.success('登录成功')
      navigate('/dashboard')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div
      style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        background: '#0A0A0A',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background Image */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundImage: 'url(https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      />

      {/* Overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(180deg, rgba(10,10,10,0.5) 0%, rgba(10,10,10,0) 50%, rgba(10,10,10,0.5) 100%)'
        }}
      />

      {/* Content */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'space-between'
        }}
      >
        {/* Left Panel */}
        <div
          style={{
            flex: 1,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            padding: '80px',
            gap: '32px',
            alignItems: 'center'
          }}
        >
          {/* Brand Logo */}
          <div
            style={{
              width: '120px',
              height: '120px',
              borderRadius: '32px',
              background: 'radial-gradient(circle, #A78BFA 0%, #7C3AED 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              boxShadow: '0 12px 32px rgba(124,58,237,0.5)'
            }}
          >
            <ShieldCheck style={{ width: '60px', height: '60px', color: '#FFFFFF' }} />
          </div>

          {/* Brand Title */}
          <h1
            style={{
              fontSize: '48px',
              fontWeight: 700,
              color: '#FFFFFF',
              margin: 0,
              fontFamily: 'Inter, sans-serif',
              textAlign: 'center'
            }}
          >
            管理后台
          </h1>

          {/* Brand Description */}
          <p
            style={{
              fontSize: '18px',
              fontWeight: 400,
              color: 'rgba(255,255,255,0.6)',
              margin: 0,
              fontFamily: 'Inter, sans-serif',
              textAlign: 'center',
              width: '400px'
            }}
          >
            安全可靠的企业级管理平台
          </p>
        </div>
        {/* Right Panel */}
        <div
          style={{
            width: '600px',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            padding: '80px 60px'
          }}
        >
          {/* Glass Card */}
          <div
            style={{
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: '28px',
              background: 'rgba(255,255,255,0.08)',
              backdropFilter: 'blur(40px)',
              borderRadius: '32px',
              padding: '48px 40px',
              border: '1px solid rgba(255,255,255,0.25)',
              boxShadow: '0 20px 60px rgba(0,0,0,0.25)',
              backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.06) 100%)'
            }}
          >
            {/* Header */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
              {/* Logo */}
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '20px',
                  background: 'radial-gradient(circle, #A78BFA 0%, #7C3AED 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 8px 24px rgba(124,58,237,0.4)'
                }}
              >
                <Sparkles style={{ width: '32px', height: '32px', color: '#FFFFFF' }} />
              </div>

              <h1
                style={{
                  fontSize: '28px',
                  fontWeight: 600,
                  color: '#FFFFFF',
                  margin: 0,
                  fontFamily: 'Inter, sans-serif',
                  textAlign: 'center',
                  width: '100%'
                }}
              >
                欢迎回来
              </h1>

              <p
                style={{
                  fontSize: '14px',
                  fontWeight: 400,
                  color: 'rgba(255,255,255,0.6)',
                  margin: 0,
                  fontFamily: 'Inter, sans-serif',
                  textAlign: 'center',
                  width: '100%'
                }}
              >
                登录以继续使用
              </p>
            </div>

            {/* Form Section */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Email Input */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label
                  style={{
                    fontSize: '14px',
                    fontWeight: 500,
                    color: 'rgba(255,255,255,0.8)',
                    fontFamily: 'Inter, sans-serif'
                  }}
                >
                  邮箱地址
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="your@email.com"
                  required
                  style={{
                    width: '100%',
                    height: '48px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.13)',
                    borderRadius: '12px',
                    padding: '0 16px',
                    fontSize: '14px',
                    color: 'rgba(255,255,255,0.4)',
                    fontFamily: 'Inter, sans-serif',
                    outline: 'none'
                  }}
                />
              </div>

              {/* Password Input */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label
                  style={{
                    fontSize: '14px',
                    fontWeight: 500,
                    color: 'rgba(255,255,255,0.8)',
                    fontFamily: 'Inter, sans-serif'
                  }}
                >
                  密码
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  required
                  style={{
                    width: '100%',
                    height: '48px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.13)',
                    borderRadius: '12px',
                    padding: '0 16px',
                    fontSize: '14px',
                    color: 'rgba(255,255,255,0.4)',
                    fontFamily: 'Inter, sans-serif',
                    outline: 'none'
                  }}
                />
              </div>

              {/* Options Row */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    name="remember"
                    checked={formData.remember}
                    onChange={handleChange}
                    style={{
                      width: '18px',
                      height: '18px',
                      accentColor: '#A78BFA',
                      cursor: 'pointer'
                    }}
                  />
                  <span
                    style={{
                      fontSize: '13px',
                      color: 'rgba(255,255,255,0.8)',
                      fontFamily: 'Inter, sans-serif'
                    }}
                  >
                    记住我
                  </span>
                </label>
                <button
                  type="button"
                  style={{
                    background: 'transparent',
                    border: 'none',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#A78BFA',
                    fontFamily: 'Inter, sans-serif',
                    cursor: 'pointer'
                  }}
                >
                  忘记密码?
                </button>
              </div>

              {/* Login Button */}
              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%',
                  height: '48px',
                  background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: 600,
                  color: '#FFFFFF',
                  fontFamily: 'Inter, sans-serif',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  boxShadow: '0 8px 24px rgba(124,58,237,0.4)',
                  opacity: loading ? 0.7 : 1
                }}
              >
                登录
              </button>
            </form>

            {/* Divider */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.13)' }} />
              <span
                style={{
                  fontSize: '13px',
                  color: 'rgba(255,255,255,0.4)',
                  fontFamily: 'Inter, sans-serif'
                }}
              >
                或
              </span>
              <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.13)' }} />
            </div>

            {/* Social Login */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
              <button
                type="button"
                style={{
                  width: '56px',
                  height: '56px',
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.13)',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer'
                }}
              >
                <Apple style={{ width: '24px', height: '24px', color: '#FFFFFF' }} />
              </button>

              <button
                type="button"
                style={{
                  width: '56px',
                  height: '56px',
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.13)',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer'
                }}
              >
                <Mail style={{ width: '24px', height: '24px', color: '#FFFFFF' }} />
              </button>

              <button
                type="button"
                style={{
                  width: '56px',
                  height: '56px',
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.13)',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer'
                }}
              >
                <Github style={{ width: '24px', height: '24px', color: '#FFFFFF' }} />
              </button>
            </div>

            {/* Sign Up Link */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
              <span
                style={{
                  fontSize: '14px',
                  color: 'rgba(255,255,255,0.6)',
                  fontFamily: 'Inter, sans-serif'
                }}
              >
                还没有账户?
              </span>
              <button
                type="button"
                onClick={() => navigate('/register')}
                style={{
                  background: 'transparent',
                  border: 'none',
                  fontSize: '14px',
                  fontWeight: 600,
                  color: '#A78BFA',
                  fontFamily: 'Inter, sans-serif',
                  cursor: 'pointer'
                }}
              >
                注册
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
