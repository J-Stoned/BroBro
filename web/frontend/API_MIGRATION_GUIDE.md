# API Configuration Migration Guide

## Overview

The BroBro frontend now uses a centralized API configuration system instead of hardcoded localhost URLs. This allows for easy switching between development, staging, and production environments.

---

## What Changed

### Before (Hardcoded URLs)
```javascript
// OLD - In individual components
const response = await fetch('http://localhost:8000/api/analytics/metrics');
const data = await axios.get('http://localhost:8000/api/search');
```

### After (Centralized Config)
```javascript
// NEW - Using centralized config
import API_CONFIG from '@/config/api';

const response = await fetch(API_CONFIG.ANALYTICS.METRICS);
const data = await axios.get(API_CONFIG.GEMINI.SEARCH);
```

---

## Components to Update

The following components currently have hardcoded `http://localhost:8000` URLs and should be updated:

### 1. Analytics Components
- `src/components/analytics/AlertCenter.jsx`
- `src/components/analytics/AnalyticsDashboard.jsx`
- `src/components/analytics/ComparativeAnalysis.jsx`
- `src/components/analytics/ExecutionTimeline.jsx`
- `src/components/analytics/PerformanceCharts.jsx`
- `src/components/analytics/ReportGenerator.jsx`
- `src/components/analytics/ROICalculator.jsx`
- `src/components/analytics/SearchAnalyticsDashboard.jsx`

### 2. Other Components (if applicable)
- Any component making API calls to `http://localhost:8000`

---

## Migration Steps

### Step 1: Import API Config
```javascript
import API_CONFIG from '@/config/api';
```

### Step 2: Replace Hardcoded URLs

**For Analytics:**
```javascript
// OLD
const response = await fetch('http://localhost:8000/api/analytics/metrics');

// NEW
const response = await fetch(API_CONFIG.ANALYTICS.METRICS);
```

**For Search:**
```javascript
// OLD
const data = await axios.get('http://localhost:8000/api/search');

// NEW
const data = await axios.get(API_CONFIG.GEMINI.SEARCH);
```

**For Chat:**
```javascript
// OLD
const response = await fetch('http://localhost:8000/api/chat', { ... });

// NEW
const response = await fetch(API_CONFIG.CHAT, { ... });
```

### Step 3: Test in Development
```bash
npm run dev
# API calls will use http://localhost:8000 (from .env.development)
```

### Step 4: Test in Production
```bash
npm run build
# API calls will use https://api.brobro.com (from .env.production)
```

---

## Environment Variables

### Development (.env.development)
```env
VITE_API_URL=http://localhost:8000
VITE_WEBSOCKET_URL=ws://localhost:8000/ws/collaborate
VITE_LOG_LEVEL=debug
VITE_DEBUG=true
```

### Production (.env.production)
```env
VITE_API_URL=https://api.brobro.com
VITE_WEBSOCKET_URL=wss://api.brobro.com/ws/collaborate
VITE_LOG_LEVEL=info
VITE_DEBUG=false
```

### Custom Deployment
Create `.env.staging` or `.env.[custom]` files as needed:
```env
VITE_API_URL=https://staging.brobro.com
VITE_WEBSOCKET_URL=wss://staging.brobro.com/ws/collaborate
VITE_LOG_LEVEL=info
VITE_DEBUG=false
```

---

## Available API Endpoints

See `config/api.js` for complete list of available endpoints:

```javascript
API_CONFIG.SEARCH              // Search endpoint
API_CONFIG.CHAT                // Chat endpoint
API_CONFIG.ANALYTICS.*         // Analytics endpoints
API_CONFIG.WORKFLOWS.*         // Workflow endpoints
API_CONFIG.SEARCH_ANALYTICS.*  // Search analytics
API_CONFIG.AI_GENERATION.*     // AI generation endpoints
API_CONFIG.GEMINI.*            // Gemini search endpoints
API_CONFIG.HEALTH              // Health check
API_CONFIG.STATUS              // Detailed status
```

---

## Best Practices

1. **Always use API_CONFIG** instead of hardcoding URLs
2. **Don't create duplicate endpoints** - check config/api.js first
3. **Use environment variables** for non-standard deployments
4. **Update .env files** when deploying to new environments
5. **Test API connectivity** using the `/health` or `/api/status` endpoints

---

## Troubleshooting

### "Cannot reach API"
- Check that backend is running on the configured URL
- Verify VITE_API_URL matches your backend
- Check browser console for CORS errors

### "API_CONFIG undefined"
- Ensure import path is correct: `@/config/api`
- Check that @ alias is configured in vite.config.js

### "Wrong API endpoint in production"
- Verify .env.production has correct VITE_API_URL
- Run `npm run build` to create production build
- Don't use dev server (npm run dev) for production testing

---

## Completion Checklist

- [ ] Create API config (config/api.js) ✅ DONE
- [ ] Create environment files (.env.development, .env.production) ✅ DONE
- [ ] Update AlertCenter.jsx
- [ ] Update AnalyticsDashboard.jsx
- [ ] Update ComparativeAnalysis.jsx
- [ ] Update ExecutionTimeline.jsx
- [ ] Update PerformanceCharts.jsx
- [ ] Update ReportGenerator.jsx
- [ ] Update ROICalculator.jsx
- [ ] Update SearchAnalyticsDashboard.jsx
- [ ] Test development environment
- [ ] Test production build
- [ ] Document any custom endpoints added

---

Last Updated: 2025-11-16
