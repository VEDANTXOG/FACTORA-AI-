import { useState, useEffect, useRef } from 'react'
import { useSignIn } from '@clerk/clerk-react'

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CUSTOM FACTORA AI LOGIN COMPONENT
// This is the "Front Door" - the custom login page that replaces generic Clerk redirect
// Uses the Design from frontend_fixed.html converted to React
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface LoginProps {
    onSignInSuccess?: () => void
}

export default function Login({ onSignInSuccess }: LoginProps) {
    const { signIn, setActive, isLoaded } = useSignIn()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const canvasRef = useRef<HTMLCanvasElement>(null)

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // MATRIX RAIN EFFECT - Same as frontend_fixed.html
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext('2d')
        if (!ctx) return

        const resizeCanvas = () => {
            canvas.width = window.innerWidth
            canvas.height = window.innerHeight
        }
        resizeCanvas()
        window.addEventListener('resize', resizeCanvas)

        const yPositions: Record<number, number> = {}

        const draw = () => {
            ctx.fillStyle = 'rgba(20, 20, 20, 0.1)'
            ctx.fillRect(0, 0, canvas.width, canvas.height)
            ctx.fillStyle = 'rgba(177, 156, 217, 0.85)'
            ctx.font = '18px Space Mono, monospace'

            for (let i = 0; i < canvas.width; i += 18) {
                const y = (yPositions[i] || 0) * 18
                ctx.fillText('01'[Math.floor(Math.random() * 2)], i, y)
                yPositions[i] = yPositions[i] === undefined ? 0 : yPositions[i] + 1
                if (y > canvas.height && Math.random() > 0.975) {
                    yPositions[i] = 0
                }
            }

            requestAnimationFrame(draw)
        }

        const animationId = requestAnimationFrame(draw)

        return () => {
            window.removeEventListener('resize', resizeCanvas)
            cancelAnimationFrame(animationId)
        }
    }, [])

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // SIGN IN HANDLER - Using Clerk's useSignIn hook
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const handleSignIn = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (!email || !password) {
            setError('Please enter both email and password')
            return
        }

        setIsLoading(true)

        try {
            if (!signIn) {
                setError('Authentication not available. Please configure Clerk.')
                return
            }

            const result = await signIn.create({
                identifier: email,
                password,
                strategy: "password",
            })

            if (result.status === 'complete') {
                await setActive({ session: result.createdSessionId })
                onSignInSuccess?.()
            } else {
                // Handle multi-factor auth or other intermediate states
                console.log('Sign in requires additional steps:', result)
                setError('Additional verification required')
            }
        } catch (err: any) {
            console.error('Sign in error:', err)
            const errorMessage = err.errors?.[0]?.message || err.message || 'Sign in failed'
            setError(errorMessage)
        } finally {
            setIsLoading(false)
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // RENDER - Custom FACTOA Login UI (Shopify-Style "Front Door")
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    return (
        <div className="login-container">
            {/* Matrix Rain Canvas */}
            <canvas ref={canvasRef} className="matrix-canvas" />

            {/* Content Wrapper */}
            <div className="login-content">
                {/* Logo Section */}
                <div className="login-logo-section">
                    <img
                        src="/logo.png"
                        alt="Factora AI Logo"
                        className="login-logo"
                    />
                    <h1 className="login-title">FACTORA AI</h1>
                    <p className="login-tagline">Dissecting the Fabric of Reality</p>
                </div>

                {/* Sign In Form */}
                <div className="login-form-wrapper">
                    <form onSubmit={handleSignIn} className="login-form">
                        <h2 className="login-form-title">Welcome Back</h2>
                        <p className="login-form-subtitle">Sign in to access your truth detection dashboard</p>

                        {error && (
                            <div className="login-error">
                                {error}
                            </div>
                        )}

                        <div className="login-field">
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                disabled={isLoading || !isLoaded}
                                autoComplete="email"
                            />
                        </div>

                        <div className="login-field">
                            <label htmlFor="password">Password</label>
                            <div className="password-input-wrapper">
                                <input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    disabled={isLoading || !isLoaded}
                                    autoComplete="current-password"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            className={`login-submit-btn ${isLoading ? 'loading' : ''}`}
                            disabled={isLoading || !isLoaded}
                        >
                            {isLoading ? (
                                <span className="loading-dots">Signing in...</span>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    {/* Footer Note */}
                    <p className="login-footer-note">
                        FACTORA AI analyzes patterns. Verify important information independently.
                    </p>
                </div>

                {/* Decorative elements */}
                <div className="login-decorative-ring" />
            </div>
        </div>
    )
}
