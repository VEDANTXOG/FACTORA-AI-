import React, { useState, useEffect } from 'react'
import type { CSSProperties } from 'react'
import { saveAuth } from '../utils/auth'

type User = {
    name: string
    profession?: string
    age?: string
    username?: string
}

type LoadingState = 'email' | null

interface HeroGateProps {
    onComplete: () => void
}

const MAIN_APP = 'http://127.0.0.1:5500/frontend_fixed.html'

export default function HeroGate({ onComplete }: HeroGateProps) {
    const stored = localStorage.getItem('factora_user')
    const getUser = (): User => {
        if (!stored) return { name: 'there' }
        try {
            return JSON.parse(stored) as User
        } catch {
            return { name: 'there' }
        }
    }
    const user = getUser()

    const [loading, setLoading] = useState<LoadingState>(null)
    const [showEmailForm, setShowEmailForm] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    type Particle = {
        id: number
        left: string
        top: string
        duration: string
        drift: string
        delay: string
    }

    const particles: Particle[] = Array.from({ length: 48 }).map((_, i) => ({
        id: i,
        left: `${(i * 2.1) % 100}%`,
        top: `${(i * 7.3) % 100}%`,
        duration: `${10 + (i % 10)}s`,
        drift: `${Math.sin(i * 0.7) * 80 + (i % 6) * 18}px`,
        delay: `${(i * 0.4) % 8}s`,
    }))

    const handleGoogleSignIn = (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault()

        // New auth state system
        localStorage.setItem('isLoggedIn', 'true')
        localStorage.setItem('username', 'Google User')

        // Backward compatible (existing behavior)
        localStorage.setItem('factora_user', JSON.stringify({ name: 'Google User' }))

        onComplete()
    }

    const handleEmailClick = (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault()
        setShowEmailForm(true)
        setError('')
    }

    const handleBack = (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault()
        setShowEmailForm(false)
        setEmail('')
        setPassword('')
        setError('')
    }

    const handleEmailSignIn = async () => {
        if (!email || !password) {
            setError('Please enter your email and password.')
            return
        }
        setLoading('email')
        setError('')

        try {
            // Extract username from email (before @)
            const username = email.split('@')[0]
            const response = await fetch('http://127.0.0.1:8000/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            if (!response.ok) {
                throw new Error('Invalid credentials')
            }
            const data = await response.json()

            // New auth state system
            localStorage.setItem('isLoggedIn', 'true')
            localStorage.setItem('username', username)

            // Backward compatible (existing behavior)
            saveAuth({ token: data.token, user: { username, name: username } })
            onComplete()
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Login failed')
        } finally {
            setLoading(null)
        }
    }

    const handleGuestAccess = (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault()

        // New auth state system
        localStorage.setItem('isLoggedIn', 'false')
        localStorage.setItem('username', 'Guest')

        // Backward compatible (existing behavior)
        localStorage.setItem('factora_user', JSON.stringify({ name: 'Guest' }))
        localStorage.setItem('factora_guest', 'true')
        localStorage.removeItem('auth_method')

        onComplete()
    }

    // Auto-complete if already authenticated
    useEffect(() => {
        const token = localStorage.getItem('factora_token')
        if (token || localStorage.getItem('factora_guest') === 'true') {
            onComplete()
        }
    }, [onComplete])

    const ParticleLayer = () => (
        <div className="digital-dust" aria-hidden="true">
            {particles.map((p) => (
                <div
                    key={p.id}
                    className="dust-particle"
                    style={{
                        left: p.left,
                        top: p.top,
                        animationDuration: p.duration,
                        animationDelay: p.delay,
                        '--drift': p.drift,
                    } as React.CSSProperties}
                />
            ))}
        </div>
    )

    if (showEmailForm) {
        return (
            <>
                <ParticleLayer />
                <div className="auth-card" style={{ position: 'relative' }}>
                    <button
                        onClick={handleBack}
                        style={{
                            position: 'absolute', top: '20px', left: '20px',
                            background: 'none', border: 'none',
                            color: 'rgba(255,255,255,0.7)', cursor: 'pointer',
                            fontSize: '14px', display: 'flex', alignItems: 'center',
                            gap: '4px', transition: 'color 0.2s',
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.color = '#fff' }}
                        onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(255,255,255,0.7)' }}
                    >
                        ← Back
                    </button>

                    <div style={{ textAlign: 'center', marginBottom: '32px', paddingTop: '32px' }}>
                        <h1 className="hero-welcome" style={{
                            fontSize: 'clamp(1.8rem, 5vw, 2.5rem)',
                            fontWeight: 700, color: '#fff', marginBottom: '8px',
                        }}>
                            Secure Sign In
                        </h1>
                        <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '14px' }}>
                            Enter your credentials to continue
                        </p>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {error && (
                            <div style={{
                                background: 'rgba(239,68,68,0.15)',
                                border: '1px solid rgba(239,68,68,0.4)',
                                color: '#fca5a5', padding: '12px 16px',
                                borderRadius: '12px', fontSize: '14px',
                            }}>
                                {error}
                            </div>
                        )}

                        <input
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                            className="form-input"
                            disabled={loading === 'email'}
                            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleEmailSignIn()}
                        />

                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                            className="form-input"
                            disabled={loading === 'email'}
                            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleEmailSignIn()}
                        />

                        <button
                            onClick={handleEmailSignIn}
                            disabled={loading === 'email' || !email || !password}
                            className="continue-btn"
                            style={{ marginTop: '8px' }}
                        >
                            {loading === 'email' ? 'Signing in...' : 'Sign In →'}
                        </button>
                    </div>
                </div>
            </>
        )
    }

    return (
        <>
            <ParticleLayer />
            <div className="auth-card">
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <h1 className="hero-welcome" style={{
                        fontSize: 'clamp(2rem, 6vw, 3rem)',
                        fontWeight: 700, color: '#ffffff',
                        marginBottom: '8px', letterSpacing: '-0.02em',
                    }}>
                        Welcome {user.name}!
                    </h1>
                    {user.profession && (
                        <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '15px', marginBottom: '4px' }}>
                            {user.profession}{user.age ? `, age ${user.age}` : ''}
                        </p>
                    )}
                    <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '13px', marginTop: '6px' }}>
                        Choose your secure access method
                    </p>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {/* Google */}
                    <button
                        onClick={handleGoogleSignIn}
                        disabled={!!loading}
                        style={{
                            width: '100%', height: '56px',
                            display: 'flex', alignItems: 'center',
                            justifyContent: 'flex-start', gap: '16px',
                            padding: '0 20px', background: '#ffffff',
                            border: 'none', borderRadius: '14px',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            fontSize: '15px', fontWeight: 600, color: '#1a1a1a',
                            transition: 'all 0.25s ease',
                            boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
                            opacity: loading ? 0.6 : 1,
                        }}
                        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.transform = 'translateY(-2px)' }}
                        onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)' }}
                    >
                        <svg style={{ width: '22px', height: '22px', flexShrink: 0 }} viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                        </svg>
                        Continue with Google
                    </button>

                    {/* Email */}
                    <button
                        onClick={handleEmailClick}
                        disabled={!!loading}
                        style={{
                            width: '100%', height: '56px',
                            display: 'flex', alignItems: 'center',
                            justifyContent: 'flex-start', gap: '16px',
                            padding: '0 20px',
                            background: 'rgba(255,255,255,0.07)',
                            border: '1px solid rgba(255,255,255,0.15)',
                            borderRadius: '14px',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            fontSize: '15px', fontWeight: 600, color: '#ffffff',
                            transition: 'all 0.25s ease',
                            backdropFilter: 'blur(10px)',
                            opacity: loading ? 0.6 : 1,
                        }}
                        onMouseEnter={(e) => { if (!loading) { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.transform = 'translateY(-2px)' } }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.07)'; e.currentTarget.style.transform = 'translateY(0)' }}
                    >
                        <svg style={{ width: '22px', height: '22px', flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.27 7.27c.883.883 2.317.883 3.2 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        Continue with Email
                    </button>
                </div>

                {/* Guest */}
                <div style={{ marginTop: '28px', paddingTop: '24px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                    <button
                        onClick={handleGuestAccess}
                        disabled={!!loading}
                        style={{
                            width: '100%', background: 'none', border: 'none',
                            color: 'rgba(255,255,255,0.5)', fontSize: '14px',
                            fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
                            letterSpacing: '0.04em', padding: '8px',
                            transition: 'color 0.2s',
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.color = '#00ff88' }}
                        onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(255,255,255,0.5)' }}
                    >
                        Enter as Guest →
                    </button>
                </div>
            </div>
        </>
    )
}