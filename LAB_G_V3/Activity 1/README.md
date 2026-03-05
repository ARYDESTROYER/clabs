# Lab-Z: OWASP ZAP Fundamentals with Default Juice Shop

Single-activity lab focused on core ZAP learning using a default OWASP Juice Shop app.

## Services
- Juice Shop app: `http://localhost:30000`
- ZAP UI (WebSwing): `http://localhost:30004/zap/`

## Build and Run
```bash
docker build -t trustlab/lab-z:latest .
docker run -d --name lab-z -p 30000:30000 -p 30003:30003 -p 30004:30004 trustlab/lab-z:latest
```

Use:
- App: `http://localhost:31000`
- ZAP UI: `http://localhost:31004/zap/`
- Proxy: 30003
