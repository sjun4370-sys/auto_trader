/**
 * @author Jun
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, ShieldCheck, UserPlus, Eye, EyeOff, Check, X } from 'lucide-react'
import { message } from 'antd'
import { authApi } from '../api/auth'
import BackgroundDecoration from '../components/BackgroundDecoration'

function Register() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      message.error('两次输入的密码不一致')
      return
    }

    if (formData.password.length < 6) {
      message.error('密码至少6位')
      return
    }

    setLoading(true)
    try {
      await authApi.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      })
      message.success('注册成功，请登录')
      navigate('/login')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  const passwordRequirements = [
    { met: formData.password.length >= 6, text: '至少6个字符' },
    { met: /[A-Z]/.test(formData.password), text: '包含大写字母' },
    { met: /[0-9]/.test(formData.password), text: '包含数字' }
  ]

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
          gap: '28px',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '24px',
          padding: '40px 36px',
          border: '1px solid rgba(255,255,255,0.1)',
          boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
          animation: 'fadeInUp 0.6s ease-out',
          zIndex: 1
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
          {/* Brand Logo */}
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '18px',
              background: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <UserPlus style={{ width: '32px', height: '32px', color: '#000000' }} />
          </div>

          <div style={{ textAlign: 'center' }}>
            <h1
              style={{
                fontSize: '24px',
                fontWeight: 600,
                color: '#FFFFFF',
                margin: '0 0 6px 0',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              创建账户
            </h1>
            <p
              style={{
                fontSize: '13px',
                fontWeight: 400,
                color: 'rgba(255,255,255,0.6)',
                margin: 0,
                fontFamily: 'Inter, sans-serif'
              }}
            >
              填写以下信息完成注册
            </p>
          </div>
        </div>

        {/* Form Section */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Username Input */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              style={{
                fontSize: '12px',
                fontWeight: 500,
                color: 'rgba(255,255,255,0.8)',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              用户名
            </label>
            <div style={{ position: 'relative' }}>
              <UserPlus
                style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '16px',
                  height: '16px',
                  color: 'rgba(255,255,255,0.4)'
                }}
              />
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="选择一个用户名"
                required
                style={{
                  width: '100%',
                  height: '44px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '10px',
                  padding: '0 14px 0 44px',
                  fontSize: '13px',
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

          {/* Email Input */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              style={{
                fontSize: '12px',
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
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '16px',
                  height: '16px',
                  color: 'rgba(255,255,255,0.4)'
                }}
              />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                required
                style={{
                  width: '100%',
                  height: '44px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '10px',
                  padding: '0 14px 0 44px',
                  fontSize: '13px',
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              style={{
                fontSize: '12px',
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
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '16px',
                  height: '16px',
                  color: 'rgba(255,255,255,0.4)'
                }}
              />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="创建密码"
                required
                style={{
                  width: '100%',
                  height: '44px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '10px',
                  padding: '0 44px 0 44px',
                  fontSize: '13px',
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
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {showPassword ? (
                  <EyeOff style={{ width: '16px', height: '16px', color: 'rgba(255,255,255,0.4)' }} />
                ) : (
                  <Eye style={{ width: '16px', height: '16px', color: 'rgba(255,255,255,0.4)' }} />
                )}
              </button>
            </div>

            {/* Password Strength Indicator */}
            {formData.password.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '4px' }}>
                <div style={{ display: 'flex', gap: '4px' }}>
                  {passwordRequirements.map((req, i) => (
                    <div
                      key={i}
                      style={{
                        flex: 1,
                        height: '3px',
                        borderRadius: '2px',
                        background: req.met
                          ? 'rgba(255,255,255,0.9)'
                          : 'rgba(255,255,255,0.1)',
                        transition: 'all 0.3s ease'
                      }}
                    />
                  ))}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {passwordRequirements.map((req, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '10px',
                        color: req.met ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.3)',
                        fontFamily: 'Inter, sans-serif',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {req.met ? (
                        <Check style={{ width: '10px', height: '10px' }} />
                      ) : (
                        <X style={{ width: '10px', height: '10px' }} />
                      )}
                      {req.text}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password Input */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              style={{
                fontSize: '12px',
                fontWeight: 500,
                color: 'rgba(255,255,255,0.8)',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              确认密码
            </label>
            <div style={{ position: 'relative' }}>
              <ShieldCheck
                style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '16px',
                  height: '16px',
                  color: 'rgba(255,255,255,0.4)'
                }}
              />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="再次输入密码"
                required
                style={{
                  width: '100%',
                  height: '44px',
                  background: 'rgba(255,255,255,0.05)',
                  border: `1px solid ${
                    formData.confirmPassword && formData.password !== formData.confirmPassword
                      ? 'rgba(239,68,68,0.5)'
                      : 'rgba(255,255,255,0.1)'
                  }`,
                  borderRadius: '10px',
                  padding: '0 44px 0 44px',
                  fontSize: '13px',
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
                  e.target.style.borderColor =
                    formData.confirmPassword && formData.password !== formData.confirmPassword
                      ? 'rgba(239,68,68,0.5)'
                      : 'rgba(255,255,255,0.1)'
                  e.target.style.background = 'rgba(255,255,255,0.05)'
                }}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {showConfirmPassword ? (
                  <EyeOff style={{ width: '16px', height: '16px', color: 'rgba(255,255,255,0.4)' }} />
                ) : (
                  <Eye style={{ width: '16px', height: '16px', color: 'rgba(255,255,255,0.4)' }} />
                )}
              </button>
            </div>
            {formData.confirmPassword && formData.password !== formData.confirmPassword && (
              <span style={{ fontSize: '10px', color: '#EF4444', fontFamily: 'Inter, sans-serif' }}>
                两次输入的密码不一致
              </span>
            )}
          </div>

          {/* Register Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              height: '48px',
              background: '#FFFFFF',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 600,
              color: '#000000',
              fontFamily: 'Inter, sans-serif',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              marginTop: '8px',
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
                    width: '16px',
                    height: '16px',
                    border: '2px solid rgba(0,0,0,0.3)',
                    borderTopColor: '#000000',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite'
                  }}
                />
                注册中...
              </>
            ) : (
              <>
                <UserPlus style={{ width: '16px', height: '16px' }} />
                创建账户
              </>
            )}
          </button>
        </form>

        {/* Login Link */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
          <span
            style={{
              fontSize: '13px',
              color: 'rgba(255,255,255,0.5)',
              fontFamily: 'Inter, sans-serif'
            }}
          >
            已有账户?
          </span>
          <button
            type="button"
            onClick={() => navigate('/login')}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '13px',
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
            立即登录
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

export default Register
