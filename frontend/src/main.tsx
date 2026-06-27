import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App'
import './style.css'

// Get Clerk key
const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

// Root element
const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Failed to find the root element')
}

// Render with Clerk provider
createRoot(rootElement).render(
  <StrictMode>
    {clerkPublishableKey ? (
      <ClerkProvider publishableKey={clerkPublishableKey}>
        <App />
      </ClerkProvider>
    ) : (
      <App />
    )}
  </StrictMode>
)
