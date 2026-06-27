import { useState } from 'react'
import OnboardingForm from './components/OnboardingForm'
import HeroGate from './components/HeroGate'
import './style.css'

function App() {
    const [step, setStep] = useState(1)
    const [userData, setUserData] = useState({ name: '', profession: '', age: '' })

    const handleOnboardingComplete = (name: string, profession: string, age: string) => {
        setUserData({ name, profession, age })
        setStep(2)
    }

    const handleAuthComplete = () => {
        // Step 3: Robust hand-off to production server
        try {
            window.location.assign('http://127.0.0.1:5500/frontend_fixed.html')
        } catch (error) {
            console.error('Production redirect failed:', error)
            // Fallback: Mark as complete locally
            localStorage.setItem('factora_onboard_complete', 'true')
            alert('Onboarding complete! (Local fallback - check frontend_fixed.html manually)')
        }
    }

    return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 background-dynamics">
            <div className="bg-animation">
                <div className="matrix-grid">
                    <div className="scanline"></div>
                </div>
                <div className="neural-drift">
                    <div className="neural-blob"></div>
                    <div className="neural-blob"></div>
                    <div className="neural-blob"></div>
                </div>
                <div className="digital-dust">
                    {Array.from({ length: 40 }, (_, i) => (
                        <div
                            key={i}
                            className="dust-particle"
                            style={{
                                '--duration': `${12 + Math.random() * 8}s`,
                                '--drift': `${(Math.random() - 0.5) * 100}px`,
                                left: `${Math.random() * 100}%`,
                            } as React.CSSProperties}
                        />
                    ))}
                </div>
            </div>
            {step === 1 && (
                <OnboardingForm onComplete={handleOnboardingComplete} />
            )}
            {step === 2 && (
                <HeroGate userData={userData} onComplete={handleAuthComplete} />
            )}
        </div>
    )
}

export default App
