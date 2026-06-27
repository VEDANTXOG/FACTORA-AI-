# FACTORA AI - Frontend Setup with Clerk Authentication

## ✅ Project Created Successfully!

The Vite + React + TypeScript frontend with Clerk authentication has been set up.

## 📁 Project Structure
```
frontend/
├── .env                    # Environment variables (YOUR CLERK KEY HERE)
├── index.html              # Entry HTML
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── tsconfig.node.json     # Node TypeScript config
├── vite.config.ts         # Vite config with React
├── public/
└── src/
    ├── main.tsx           # Main entry with ClerkProvider + fail-safe
    ├── App.tsx           # App with SignedOut/SignedIn guards + UserButton
    ├── style.css        # Complete styling
    └── vite-env.d.ts    # Vite type declarations
```

## 🔑 CRITICAL: Add Your Clerk Publishable Key

1. Open the `.env` file in the `frontend/` folder
2. Replace the placeholder with your actual Clerk Publishable Key:
   ```
   VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxx
   ```
3. Get your key from: **https://dashboard.clerk.com/listsite/app_.../api-keys**

## 🚀 How to Run

```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## 🔐 Authentication Flow

- **Signed Out**: Shows FACTORA AI landing page with sign-in prompt
- **Signed In**: Shows dashboard with "Welcome back, [Name]" and UserButton

## 📝 Key Files Explained

### `src/main.tsx`
- Wraps entire app in `<ClerkProvider>`
- Fail-safe: App renders configuration message if API key is missing
- Prevents "White Screen of Death"

### `src/App.tsx`
- `<SignedOut>`: Landing page with logo, tagline, features
- `<SignedIn>`: Protected dashboard with UserButton + useUser() hook
- Shows "Welcome back, {Name}" inside dashboard

## 🔄 Next Steps (Migration)

To migrate logic from your old `frontend_fixed.html`:
1. Move API calls to Django from the JavaScript in `frontend_fixed.html` into the React components in `src/App.tsx`
2. Bring over additional CSS styles as needed

## ⚠️ Troubleshooting

**"Module not found" errors?**
```bash
cd frontend
npm install
```

**Build errors?**
```bash
npm run build
```

## 📦 Installed Packages

- `@clerk/clerk-react` - Clerk authentication
- `react` + `react-dom` - React
- `@vitejs/plugin-react` - Vite React plugin
- TypeScript types

---

**Now add your Clerk Publishable Key to `.env` and run `npm run dev`!**
