# Factora AI Bug Fixes - Auto-save & Reloading
Status: 🔄 Plan Approved - Implementing

## Steps from Approved Plan
- [x] 1. Create/update TODO.md ✅
- [x] 2. Edit views_fixed.py: Remove auto-save from analyze_news() ✅

- [x] 3. Backend fixed: No auto-save in /analyze/. Reloading not reproducible (pure JSON fetch). ✅
- [x] 4. Ready to test: Input news → Analyze shows (no DB save), Save button → saves. ✅
- [ ] 5. Test manual Save → Creates DB entry
- [ ] 6. Clear any test DB entries if needed
- [ ] 7. attempt_completion

**Notes:**
- Backend must be running: `cd factora_backend && python manage.py runserver`
- Reloading: Frontend disables input + fetch. Check console/network tab for 500/errors.

