# BroBro Web Interface - Deployment Guide

## 📋 Table of Contents

1. [Development Environment](#development-environment)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## 🔧 Development Environment

### Local Development Setup

#### Prerequisites
```bash
# Check versions
python --version  # Should be 3.8+
node --version    # Should be 18+
npm --version     # Should be 9+
```

#### 1. Start ChromaDB
```bash
# From project root
npm run start-chroma
```

#### 2. Start Backend
```bash
cd web/backend
pip install -r requirements.txt
python main.py
```

Backend will be available at: http://localhost:8000

#### 3. Start Frontend
```bash
cd web/frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

### Environment Variables

Create `.env` in project root:
```env
# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Optional: Change server ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## 🚀 Production Deployment

### Backend Production Setup

#### 1. Install Dependencies
```bash
cd web/backend
pip install -r requirements.txt
```

#### 2. Production Server (Gunicorn)

Install Gunicorn:
```bash
pip install gunicorn
```

Create `gunicorn.conf.py`:
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
```

Run with Gunicorn:
```bash
gunicorn main:app -c gunicorn.conf.py
```

#### 3. Production Environment Variables

Create `.env.production`:
```env
CHROMA_HOST=your-chroma-host
CHROMA_PORT=8001
ALLOWED_ORIGINS=https://your-domain.com
```

### Frontend Production Build

#### 1. Build for Production
```bash
cd web/frontend
npm run build
```

This creates a `dist/` folder with optimized static files.

#### 2. Serve Static Files

**Option A: Using Nginx**

Install Nginx and create `/etc/nginx/sites-available/brobro`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/web/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/brobro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Option B: Using Node.js (serve)**
```bash
npm install -g serve
serve -s dist -l 3000
```

## 🐳 Docker Deployment

### Backend Dockerfile

Create `web/backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `web/frontend/Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Create `web/frontend/nginx.conf`:
```nginx
server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://backend:8000;
    }
}
```

### Docker Compose

Create `web/docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CHROMA_HOST=chroma
      - CHROMA_PORT=8000
    depends_on:
      - chroma
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    restart: unless-stopped

volumes:
  chroma_data:
```

Deploy with Docker Compose:
```bash
cd web
docker-compose up -d
```

## ☁️ Cloud Deployment

### Railway.app Deployment

#### 1. Backend Deployment

Create `railway.toml` in `web/backend`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

Deploy:
```bash
railway login
railway up
```

#### 2. Frontend Deployment

Create `railway.toml` in `web/frontend`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "npm run preview"
```

### Vercel Deployment (Frontend Only)

Install Vercel CLI:
```bash
npm i -g vercel
```

Create `vercel.json` in `web/frontend`:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Deploy:
```bash
cd web/frontend
vercel --prod
```

### AWS Deployment

#### Backend (EC2)

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip nginx
```

4. Clone repository and install:
```bash
git clone your-repo
cd brobro/web/backend
pip3 install -r requirements.txt
```

5. Create systemd service `/etc/systemd/system/brobro-backend.service`:
```ini
[Unit]
Description=BroBro Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/brobro/web/backend
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

6. Start service:
```bash
sudo systemctl enable brobro-backend
sudo systemctl start brobro-backend
```

#### Frontend (S3 + CloudFront)

1. Build frontend:
```bash
cd web/frontend
npm run build
```

2. Create S3 bucket:
```bash
aws s3 mb s3://brobro-frontend
```

3. Upload build:
```bash
aws s3 sync dist/ s3://brobro-frontend --acl public-read
```

4. Create CloudFront distribution pointing to S3 bucket

5. Update API proxy in CloudFront behaviors

## 📊 Monitoring & Maintenance

### Health Checks

#### Backend Health
```bash
curl http://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "chroma_connected": true,
  "collections": {
    "ghl-knowledge-base": 252,
    "ghl-docs": 960
  },
  "model_loaded": true,
  "timestamp": "2025-10-29T..."
}
```

### Logging

#### Backend Logs (Systemd)
```bash
journalctl -u brobro-backend -f
```

#### Nginx Logs
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### Docker Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Performance Monitoring

Add application monitoring:

**Sentry** for error tracking:
```bash
pip install sentry-sdk[fastapi]
```

In `main.py`:
```python
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

### Backup Strategy

#### ChromaDB Data
```bash
# Backup
docker-compose exec chroma tar -czf /backup/chroma-$(date +%Y%m%d).tar.gz /chroma/chroma

# Restore
docker-compose exec chroma tar -xzf /backup/chroma-20251029.tar.gz -C /
```

### Updates & Maintenance

#### Update Backend
```bash
cd web/backend
git pull
pip install -r requirements.txt
sudo systemctl restart brobro-backend
```

#### Update Frontend
```bash
cd web/frontend
git pull
npm install
npm run build
# Copy dist/ to production location
```

## 🔒 Security Checklist

- [ ] Set up HTTPS/SSL (Let's Encrypt)
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable firewall (UFW/Security Groups)
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Implement authentication (future)

## 🚨 Troubleshooting

### Backend Issues

**ChromaDB Connection Failed**
```bash
# Check ChromaDB is running
docker ps | grep chroma

# Check network connectivity
telnet localhost 8001
```

**High Memory Usage**
```bash
# Reduce workers in gunicorn.conf.py
workers = 2
```

### Frontend Issues

**API Calls Failing**
- Check CORS settings in backend
- Verify proxy configuration in vite.config.js
- Check network tab in browser DevTools

**Build Failures**
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

## 📞 Support

For deployment issues:
1. Check logs first
2. Review health endpoint status
3. Verify all services are running
4. Check firewall/security group rules

---

**Built with BMAD-METHOD** | Production-Ready Deployment Guide
