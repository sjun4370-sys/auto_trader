/**
 * @author Jun
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, ShieldCheck, Apple, Github } from 'lucide-react'
import { message } from 'antd'
import { authApi } from '../api/auth'
import BackgroundDecoration from '../components/BackgroundDecoration'

function Login() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: ''
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
        background: '#000000',
        position: 'relative',
        overflow: 'hidden',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      {/* Background Decoration */}
      <BackgroundDecoration />

      {/* Centered Card */}
      <div
        style={{
          position: 'relative',
          width: '440px',
          maxWidth: '90vw',
          display: 'flex',
          flexDirection: 'column',
          gap: '32px',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '24px',
          padding: '48px 40px',
          border: '1px solid rgba(255,255,255,0.1)',
          boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
          animation: 'fadeInUp 0.6s ease-out',
          zIndex: 1
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center' }}>
          {/* Brand Logo */}
          <div
            style={{
              width: '72px',
              height: '72px',
              borderRadius: '20px',
              background: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <ShieldCheck style={{ width: '36px', height: '36px', color: '#000000' }} />
          </div>

          <div style={{ textAlign: 'center' }}>
            <h1
              style={{
                fontSize: '28px',
                fontWeight: 600,
                color: '#FFFFFF',
                margin: '0 0 8px 0',
                fontFamily: 'Inter, sans-serif'
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
                fontFamily: 'Inter, sans-serif'
              }}
            >
              登录以继续使用
            </p>
          </div>
        </div>

        {/* Form Section */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Email Input */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label
              style={{
                fontSize: '13px',
                fontWeight: 500,
                color: 'rgba(255,255,255,0.8)',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              邮箱地址
            </label>
            <div style={{ position: 'relative' }}>
              <Mail
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '18px',
                  height: '18px',
                  color: 'rgba(255,255,255,0.4)'
                }}
              />
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
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  padding: '0 16px 0 48px',
                  fontSize: '14px',
                  color: '#FFFFFF',
                  fontFamily: 'Inter, sans-serif',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.3)'
                  e.target.style.background = 'rgba(255,255,255,0.08)'
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.1)'
                  e.target.style.background = 'rgba(255,255,255,0.05)'
                }}
              />
            </div>
          </div>

          {/* Password Input */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label
              style={{
                fontSize: '13px',
                fontWeight: 500,
                color: 'rgba(255,255,255,0.8)',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              密码
            </label>
            <div style={{ position: 'relative' }}>
              <ShieldCheck
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '18px',
                  height: '18px',
                  color: 'rgba(255,255,255,0.4)'
                }}
              />
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
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  padding: '0 16px 0 48px',
                  fontSize: '14px',
                  color: '#FFFFFF',
                  fontFamily: 'Inter, sans-serif',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.3)'
                  e.target.style.background = 'rgba(255,255,255,0.08)'
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.1)'
                  e.target.style.background = 'rgba(255,255,255,0.05)'
                }}
              />
            </div>
          </div>

          {/* Options Row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div />
            <button
              type="button"
              style={{
                background: 'transparent',
                border: 'none',
                fontSize: '13px',
                fontWeight: 500,
                color: 'rgba(255,255,255,0.6)',
                fontFamily: 'Inter, sans-serif',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#FFFFFF'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'rgba(255,255,255,0.6)'
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
              height: '50px',
              background: '#FFFFFF',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '14px',
              fontSize: '15px',
              fontWeight: 600,
              color: '#000000',
              fontFamily: 'Inter, sans-serif',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.currentTarget.style.background = '#000000'
                e.currentTarget.style.color = '#FFFFFF'
                e.currentTarget.style.borderColor = '#FFFFFF'
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.currentTarget.style.background = '#FFFFFF'
                e.currentTarget.style.color = '#000000'
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)'
              }
            }}
          >
            {loading ? (
              <>
                <div
                  style={{
                    width: '18px',
                    height: '18px',
                    border: '2px solid rgba(0,0,0,0.3)',
                    borderTopColor: '#000000',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite'
                  }}
                />
                登录中...
              </>
            ) : (
              '登录'
            )}
          </button>
        </form>

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.1)' }} />
          <span
            style={{
              fontSize: '13px',
              color: 'rgba(255,255,255,0.4)',
              fontFamily: 'Inter, sans-serif'
            }}
          >
            或
          </span>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.1)' }} />
        </div>

        {/* Social Login */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
          {[
            { icon: Apple, label: 'Apple' },
            { icon: Mail, label: '邮箱' },
            { icon: Github, label: 'Github' }
          ].map(({ icon: Icon, label }) => (
            <button
              key={label}
              type="button"
              aria-label={label}
              style={{
                width: '52px',
                height: '52px',
                background: 'transparent',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.08)'
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.3)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'
              }}
            >
              <Icon style={{ width: '22px', height: '22px', color: '#FFFFFF' }} />
            </button>
          ))}
        </div>

        {/* Sign Up Link */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
          <span
            style={{
              fontSize: '14px',
              color: 'rgba(255,255,255,0.5)',
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
              color: '#FFFFFF',
              fontFamily: 'Inter, sans-serif',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'rgba(255,255,255,0.7)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = '#FFFFFF'
            }}
          >
            注册
          </button>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}

export default Login
