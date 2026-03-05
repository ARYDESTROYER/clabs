# Lab-G: Stored XSS (TechStore) with OWASP ZAP

This lab contains an intentionally vulnerable e-commerce application. Your objective is to find and exploit the stored XSS in the product reviews to capture the flags.

## Run locally

```bash
docker build -t lab-g .
docker run --rm -p 30000:30000 -p 30003:30003 -p 30004:30004 -p 8080:8080 lab-g
```

Allow about 60 seconds for all services to initialize.

## Important endpoints

- App: `http://localhost:30000`
- ZAP UI: `http://localhost:30004`
- Dashboard: `http://localhost:30000/dashboard`
- Optional proxy: `localhost:8080`

## Admin credentials

- Username: `admin`
- Password: `SecureAdminPass2025!`

## Evaluation

Inside the container:
```bash
bash /home/.evaluationScripts/evaluate.sh
```

Refer to `WALKTHROUGH.md` for the detailed student workflow.
