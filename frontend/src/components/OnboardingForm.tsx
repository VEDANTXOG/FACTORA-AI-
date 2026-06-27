import { useState } from 'react'

interface OnboardingFormProps {
    onComplete: (name: string, profession: string, age: string) => void
}

export default function OnboardingForm({ onComplete }: OnboardingFormProps) {
    const [formData, setFormData] = useState({ name: '', profession: '', age: '' })
    const [loading, setLoading] = useState(false)

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!formData.name || !formData.profession || !formData.age) return

        setLoading(true)

        // New auth state system (primary)
        localStorage.setItem('username', formData.name)
        localStorage.setItem('isLoggedIn', 'true')

        // Backward compatible (existing behavior)
        localStorage.setItem('factora_user', JSON.stringify(formData))

        setTimeout(() => {
            onComplete(formData.name, formData.profession, formData.age)
        }, 800)
    }

    return (
        <div className="onboarding-container">
            <div className="onboarding-content">
                <div className="onboarding-header">
                    <h1 className="onboarding-title text-5xl md:text-6xl font-bold mb-6 font-cinzel leading-tight">
                        Welcome to Factora AI
                    </h1>
                    <p className="onboarding-subtitle text-xl font-inter">
                        Let's get to know you
                    </p>
                </div>

                <div className="onboarding-glass-card">
                    <form onSubmit={handleSubmit} className="onboarding-form space-y-8 p-0">
                        <div className="form-field">
                            <label className="block text-white/90 text-sm font-medium mb-3 font-inter">Full Name</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="form-input"
                                placeholder="Enter your full name"
                                required
                            />
                        </div>

                        <div className="form-field">
                            <label className="block text-white/90 text-sm font-medium mb-3 font-inter">Profession</label>
                            <select
                                value={formData.profession}
                                onChange={(e) => setFormData({ ...formData, profession: e.target.value })}
                                className="form-select"
                                required
                            >
                                <option value="" disabled>Select your profession</option>
                                <option value="Journalist">Journalist</option>
                                <option value="Student">Student</option>
                                <option value="Content Creator">Content Creator</option>
                                <option value="Researcher">Researcher</option>
                                <option value="Financial Analyst">Financial Analyst</option>
                                <option value="News Enthusiast">News Enthusiast</option>
                            </select>
                        </div>

                        <div className="form-field">
                            <label className="block text-white/90 text-sm font-medium mb-3 font-inter">Age</label>
                            <input
                                type="number"
                                min="5"
                                max="100"
                                value={formData.age}
                                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                                className="form-input"
                                placeholder="25"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="continue-btn"
                            style={{ marginTop: '32px' }}
                        >
                            {loading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-black" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Continuing...
                                </span>
                            ) : (
                                'Continue →'
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}