/// <reference types="vite/client" />

// Allow CSS imports as side effects
declare module '*.css' {
    const content: string
    export default content
}
