# TraceGuard AI - Production Deployment Runbook

## 1. Hosting Architecture Selection

To ensure high availability, WebSocket compatibility, cost-efficiency, and minimal operational overhead, the following production topology is selected:

| Component | Target Provider | Justification |
|-----------|-----------------|---------------|
| Frontend SPA | **Vercel** / **Cloudflare Pages** | Global edge CDN caching, automatic SPA rewrites, instant HTTPS SSL provisioning. |
| Backend API & WebSockets | **Render** / **Railway** / **Fly.io** | Native Docker container hosting, continuous ASGI WebSocket support, automatic health checks. |
| Database | **Render Managed PostgreSQL** / **Neon** | Fully managed automated backups, high availability, connection pooling, zero-downtime scaling. |

---

## 2. Environment Variables Checklist

Set these variables in your hosting provider's secrets manager (never commit `.env`):

```bash
# General
APP_NAME="TraceGuard AI"
ENVIRONMENT="production"
SECRET_KEY="<generate-64-char-random-hex-string>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="1440"

# Database
DATABASE_URL="postgresql://<user>:<password>@<db-host>:5432/traceguard?sslmode=require"

# Network & CORS
ALLOWED_ORIGINS="https://traceguard.app,https://api.traceguard.app"

# Quotas & Limits
MAX_UPLOAD_SIZE_BYTES="10485760"
MAX_EVENTS_PER_SIMULATION="2000"
RATE_LIMIT_PER_MINUTE="120"
```

---

## 3. Step-by-Step Deployment Instructions

### Backend (Docker / Render / Railway):
1. Connect your repository to the hosting provider.
2. Select **Docker** deployment mode using the included `Dockerfile`.
3. Provide environment secrets as defined above.
4. Set the Health Check path to `/api/health`.
5. Deploy. The entrypoint automatically binds to `0.0.0.0:8000`.

### Database Migrations:
Execute Alembic migrations either in the build step or release command:
```bash
alembic upgrade head
```

### Frontend (Vercel):
1. Set the root directory to `frontend`.
2. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Set environment variable:
   - `VITE_API_URL`: `https://api.traceguard.app`
4. Configure SPA routing rewrites in `vercel.json`:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
   }
   ```

---

## 4. Rollback & Disaster Recovery Procedures

1. **Application Rollback**: In Render/Vercel dashboard, click **Rollback to Previous Deployment** (instant traffic diversion).
2. **Database Rollback**:
   ```bash
   alembic downgrade -1
   ```
3. **Point-in-Time Recovery**: Restore PostgreSQL instance from the latest pre-incident automated snapshot.
