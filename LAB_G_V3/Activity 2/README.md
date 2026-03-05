# Lab-G: Stored XSS Tutorial (TechStore) with OWASP ZAP

This lab is a guided Stored XSS exercise in a vulnerable e-commerce application.

Allow about 60 seconds for all services to initialize.

## Services

- App: `http://localhost:30000`
- ZAP UI: `http://localhost:30004/zap/`
- Optional proxy: `localhost:8080`

## Build and Run

```bash
docker build -t trustlab-lab-g:latest .
docker run -d --name lab-g -p 31000:30000 -p 31003:30003 -p 31004:30004 -p 18080:8080 trustlab-lab-g:latest
```

Use these URLs after startup:
- App: `http://localhost:31000`
- ZAP UI: `http://localhost:31004/zap/`
- Optional proxy: `localhost:18080`

## Admin credentials

- Username: `admin`
- Password: `SecureAdminPass2025!`

## Activity model

The lab is organized into 4 activities:
1. Basic recon and XSS fundamentals
2. Automated recon and analysis with ZAP
3. Pop first XSS payload
4. Escalate to admin context and capture admin flag via CLI listener

Only `FLAG1` and `FLAG4` are required.

