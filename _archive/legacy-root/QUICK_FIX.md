# 🚨 QUICK FIX - Copy & Paste This NOW

## The Problem
Your chat is failing because localStorage has 227+ corrupted messages (50+MB)

## The Solution
Copy and paste this into your browser console RIGHT NOW:

```javascript
// PASTE THIS INTO CONSOLE (F12 → Console tab)
localStorage.removeItem('ghl-wiz-conversation');
sessionStorage.clear();
console.log('✅ Cleared. Refreshing...');
setTimeout(() => location.reload(), 500);
```

## Then What?
1. Page refreshes automatically
2. Chat starts fresh
3. Send a message to test
4. Should work!

## If Still Not Working
1. Close Chrome COMPLETELY
2. Delete folder: `C:\Users\[your user]\AppData\Local\Google\Chrome\User Data\Default\Cache`
3. Reopen Chrome
4. Try the console command again

## That's It!
The system is now fixed to prevent this happening again.

---
**Need more help?** See FIXES/README.md for detailed explanation
