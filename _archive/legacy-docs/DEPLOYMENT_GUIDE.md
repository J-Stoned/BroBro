# BroBro Deployment Guide

Production deployment guide for BroBro - GoHighLevel Expert AI Assistant.

## Prerequisites

- Python 3.10+
- Node.js 16+
- Required API credentials:
  - Anthropic Claude API key
  - Google Gemini API key
  - GHL API token (optional, for GHL integration)

## Environment Setup

### Backend Configuration

1. **Set environment variables** (`.env` file):

```bash
# Required
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
GEMINI_FILE_SEARCH_STORE_ID=fileSearchStores/your-store-id

# Optional
GHL_API_TOKEN=your-ghl-token
CLAUDE_FORCE_TEXT_ONLY=false
```

2. **Install Python dependencies**:

```bash
cd web/backend
pip install -r requirements.txt
```

3. **Start backend server**:

```bash
# Development
python -m uvicorn main:app --reload

# Production (use Gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Frontend Configuration

1. **Install Node dependencies**:

```bash
cd web/frontend
npm install
```

2. **Build for production**:

```bash
npm run build
```

3. **Start frontend server**:

```bash
# Development
npm run dev

# Production (serve dist folder)
npm run build && npx serve dist
```

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Key Endpoints

### Chat
- `POST /api/chat` - AI-powered chat with knowledge base context
  - Rate limited: 10 requests/minute
  - Requires: `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

### Search
- `POST /api/search` - Semantic search using Gemini File Search
- `GET /api/search/unified` - Unified intelligent search
- `GET /api/search/quick` - Quick search endpoint

### Health & Status
- `GET /api/health` - Health check (both APIs required)
- `GET /api/system/info` - System information
- `GET /api/collections` - List knowledge base collections

### Gemini Integration
- `GET /api/gemini/status` - Gemini service status
- `POST /api/gemini/query` - Direct Gemini file search query

## Security Checklist

- ✅ API keys stored in `.env` (never committed to git)
- ✅ Input validation on all endpoints
- ✅ Rate limiting on expensive endpoints
- ✅ CORS configured for specific origins
- ✅ HTTPS recommended for production
- ✅ Environment variable validation at startup

## Monitoring & Logging

### Logging Configuration

Structured logging is enabled by default:
- Log level: INFO (configurable)
- Format: `timestamp - logger - level - message`
- Available methods: `logger.info()`, `logger.warning()`, `logger.error()`

### Health Monitoring

Health check endpoint: `GET /api/health`

Response includes:
- Status: "healthy" or "unhealthy"
- Available APIs: Gemini, Claude
- Timestamps

## Database (Analytics)

Optional: Add database for persistent analytics

```python
# Using SQLite (development)
SQLALCHEMY_DATABASE_URL = "sqlite:///./brobro.db"

# Using PostgreSQL (production)
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/brobro"
```

## Docker Deployment

No Docker required for knowledge base (Gemini is cloud-hosted).

Optional: Docker for containerized deployment

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t brobro-backend .
docker run -e ANTHROPIC_API_KEY=xxx -e GOOGLE_API_KEY=yyy -p 8000:8000 brobro-backend
```

## Performance Tuning

### Backend
- Workers: 4 (adjust based on CPU cores)
- Max connections: 100
- Request timeout: 30s

### Frontend
- Bundle size: ~1.5MB (gzipped)
- Code splitting: Enabled
- Caching: Static assets cached with versioning

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Verify .env file exists and has required keys
- Check logs for import errors

### Health check failing
- Ensure both `ANTHROPIC_API_KEY` and `GOOGLE_API_KEY` are set
- Verify API keys are valid and not expired
- Check network connectivity to API providers

### Rate limiting errors
- `/api/chat` limited to 10 req/min
- Implement client-side request throttling
- Consider upgrading for higher limits

### Slow searches
- Check Gemini File Search store is populated
- Verify network connectivity
- Consider response caching

## Scaling Recommendations

### Single Server
- Max 100 concurrent users
- Use Gunicorn with 4-8 workers
- Monitor: CPU, memory, API rate limits

### Multi-Server (Load Balanced)
- Use load balancer (nginx, HAProxy)
- Share `.env` configuration
- Centralize logging (ELK, Datadog)
- Add Redis for caching/sessions

## Maintenance

### Regular Tasks
- Monitor API usage and costs
- Review logs for errors
- Update dependencies monthly
- Backup database (if using SQLite)

### Updates
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update
npm run build
```

## Support

For issues or questions:
1. Check health endpoint: `GET /api/health`
2. Review logs for error messages
3. Consult API documentation at `/docs`
4. Verify .env configuration

---

**Last Updated**: November 2025
**BroBro Version**: 2.0.0
