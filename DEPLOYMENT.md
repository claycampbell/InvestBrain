# Deployment Guide

## Prerequisites

### Required Environment Variables
```bash
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
DATABASE_URL=<postgresql-connection-string>
SESSION_SECRET=<random-secret-key>
```

### Optional Configuration
```bash
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
SIGNAL_CHECK_INTERVAL=300
PRICE_CHANGE_THRESHOLD=0.05
```

## Replit Deployment

1. **Environment Setup**: Configure all required secrets in Replit's secrets manager
2. **Database**: PostgreSQL database is automatically configured
3. **Run Command**: Application starts with `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

## Production Deployment

### Database Setup
```sql
-- Required tables are auto-created on first run
-- Ensure PostgreSQL 12+ is available
```

### Application Start
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 main:app
```

### Health Check
- Endpoint: `/`
- Expected: 200 OK with analysis interface

## Features Available Post-Deployment

1. **Investment Thesis Analysis** - AI-powered thesis evaluation
2. **Signal Monitoring** - Real-time market signal tracking  
3. **Backtesting** - Historical performance validation
4. **Advanced Analytics** - Cross-thesis pattern analysis
5. **Document Processing** - Research document analysis

## Performance Notes

- Backtesting responses: ~5-8 seconds
- AI analysis: ~10-15 seconds  
- Signal monitoring: Real-time updates
- Document processing: 1-3 minutes for large files