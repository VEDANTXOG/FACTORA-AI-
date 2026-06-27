import { useState, useEffect, useRef } from 'react'
import { SignIn } from '@clerk/clerk-react'

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CUSTOM FACTORA AI LOGIN COMPONENT
// Shows custom login, then Clerk SignIn with Google option, then redirects
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface LoginProps {
    onSignInSuccess?: () => void
}

export default function Login({ onSignInSuccess: _onSignInSuccess }: LoginProps) {
    const [showClerkSignIn, setShowClerkSignIn] = useState(false)
    const canvasRef = useRef<HTMLCanvasElement>(null)

    // Matrix rain effect
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

    // If showing Clerk's sign-in, render it
    if (showClerkSignIn) {
        return (
            <div className="login-container">
                <canvas ref={canvasRef} className="matrix-canvas" />
                <div className="login-content">
                    <div className="login-logo-section">
                        <img src="/logo.png" alt="Factora AI Logo" className="login-logo" />
                        <h1 className="login-title">FACTORA AI</h1>
                        <p className="login-tagline">Dissecting the Fabric of Reality</p>
                    </div>
                    <div className="login-form-wrapper clerk-signin-wrapper">
                        <SignIn
                            routing="virtual"
                            forceRedirectUrl="/frontend_fixed.html"
                            fallbackRedirectUrl="/frontend_fixed.html"
                            appearance={{
                                elements: {
                                    rootBox: { width: '100%', maxWidth: '400px' },
                                    card: {
                                        background: 'rgba(20, 20, 20, 0.95)',
                                        border: '1px solid rgba(177, 156, 217, 0.4)',
                                        borderRadius: '16px',
                                    },
                                    headerTitle: { color: '#b19cd9', fontFamily: 'Cinzel, serif' },
                                    headerSubtitle: { color: 'rgba(255, 255, 255, 0.7)' },
                                    socialButtonsBlockButton: {
                                        background: 'rgba(177, 156, 217, 0.15)',
                                        border: '1px solid rgba(177, 156, 217, 0.4)',
                                        color: '#ffffff',
                                    },
                                    formFieldLabel: { color: 'rgba(255, 255, 255, 0.8)' },
                                    formFieldInput: {
                                        background: 'rgba(255, 255, 255, 0.08)',
                                        border: '1px solid rgba(177, 156, 217, 0.4)',
                                        color: '#ffffff',
                                        borderRadius: '8px',
                                    },
                                    formButtonPrimary: {
                                        background: 'linear-gradient(135deg, #b19cd9, #d4af37)',
                                        color: '#000000',
                                    },
                                    footerActionLink: { color: '#b19cd9' },
                                },
                                variables: {
                                    colorPrimary: '#b19cd9',
                                    colorTextOnPrimaryBackground: '#000000',
                                    colorBackground: '#1a1a1a',
                                    colorInputBackground: 'rgba(255, 255, 255, 0.08)',
                                    colorInputText: '#ffffff',
                                    borderRadius: '8px',
                                    fontFamily: 'Montserrat, sans-serif',
                                }
                            }}
                        />
                    </div>
                    <button className="back-btn" onClick={() => setShowClerkSignIn(false)}>
                        ← Back
                    </button>
                </div>
            </div>
        )
    }

    // Initial welcome screen
    const handleContinue = () => {
        window.location.href = '/frontend_fixed.html'
    }

    const handleSignIn = (e: React.FormEvent) => {
        e.preventDefault()
        setShowClerkSignIn(true)
    }

    return (
        <div className="login-container">
            <canvas ref={canvasRef} className="matrix-canvas" />
            <div className="login-content">
                <div className="login-logo-section">
                    <img src="/logo.png" alt="Factora AI Logo" className="login-logo" />
                    <h1 className="login-title">FACTORA AI</h1>
                    <p className="login-tagline">Dissecting the Fabric of Reality</p>
                </div>

                <div className="login-form-wrapper">
                    <form onSubmit={handleSignIn} className="login-form">
                        <h2 className="login-form-title">Welcome</h2>
                        <p className="login-form-subtitle">Access your truth detection dashboard</p>

                        <button type="submit" className="login-submit-btn">
                            Sign In with Google →
                        </button>
                    </form>

                    <form onSubmit={handleContinue} style={{ marginTop: '12px' }}>
                        <button type="submit" className="login-submit-btn" style={{ background: 'transparent', border: '1px solid rgba(177,156,217,0.4)' }}>
                            Continue as Guest →
                        </button>
                    </form>

                    <p className="login-footer-note">
                        FACTORA AI analyzes patterns. Verify important information independently.
                    </p>
                </div>

                <div className="login-decorative-ring" />
            </div>
        </div>
    )
}
