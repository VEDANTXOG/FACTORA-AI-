# Implementation Plan

**Overview**  
Fix all TypeScript compilation errors and runtime issues in `frontend/src/components/HeroGate.tsx` while preserving all existing functionality, UI behavior, and inline styles. The component handles authentication flows (Google, email, guest) with particle animations and form states. Errors stem from missing imports/types, broken dynamic imports, unsafe parsing, unused props, and type mismatches. Approach: static imports, proper typing, safe parsing, use onComplete for navigation, add auto-auth check.

**Types**  
Update/define these types/interfaces:  
- `User`: `{ name: string; profession?: string; age?: string; username?: string }` - for safe localStorage parsing.  
- `LoadingState`: `'email' | null` - precise union for loading state.  
- Event handlers: `React.MouseEvent<HTMLButtonElement>`, `React.KeyboardEvent<HTMLInputElement>`, `React.ChangeEvent<HTMLInputElement>`.  
- `Particle`: `{ id: number; left: string; top: string; duration: string; drift: string; delay: string }` - inline type for particles array.  
No new global types; all local to component.

**Files**  
Only one file to modify: `frontend/src/components/HeroGate.tsx` (add imports/types/logic fixes).  
- No new files.  
- No deletions.  
- No config changes (tsconfig.json/package.json unchanged).

**Functions**  
New/modified local functions (all within HeroGate.tsx):  
- `handleEmailSignIn`: Add proper async error typing (`unknown` catch), static `saveAuth` call, `onComplete()` navigation.  
- `handleGoogleSignIn`, `handleGuestAccess`, `handleEmailClick`, `handleBack`: Add `React.MouseEvent` param, use `onComplete()`.  
- No removals.  
ParticleLayer remains unchanged (functional component).

**Classes**  
No classes involved (pure functional component).

**Dependencies**  
No new packages needed. Use existing `react` and `./utils/auth`. Ensure `@types/react` implied via tsconfig.

**Testing**  
Manual: TS compilation (no red squiggles), runtime login flows (email/guest/Google simulation), particle animation, form validation/errors, auto-redirect on auth. Run `npm run dev` post-fix to verify Vite build succeeds without errors.

**Implementation Order**  
1. Create `implementation_plan.md` with this content.  
2. Update checkboxes in task_progress as steps complete.  
3. Edit HeroGate.tsx with multi-diff for all fixes atomically.
