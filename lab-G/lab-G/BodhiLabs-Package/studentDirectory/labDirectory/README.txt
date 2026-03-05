Lab-G: Stored XSS & OWASP ZAP Challenge
========================================

OBJECTIVE:
Find and exploit XSS vulnerabilities in the TechStore ecommerce application.

SERVICES:
- Ecommerce App: http://localhost:30000
- OWASP ZAP GUI: http://localhost:30004 (WebSwing - browser-based)
- ZAP Proxy: localhost:8080 (configure in your browser)
- Exploit Dashboard: http://localhost:30000/dashboard

ADMIN CREDENTIALS (for reference):
- Username: admin
- Password: SecureAdminPass2025!

CHALLENGE STEPS:
1. Explore the application (home, products, cart, reviews pages)
2. Use OWASP ZAP to scan for vulnerabilities
3. Find and exploit the XSS vulnerability in product reviews
4. Exfiltrate the admin's secret using XSS

SUBMISSION FILES (save in /home/labDirectory/):
- flag.txt         : All captured flags (one per line)
- zap-report.html  : Your OWASP ZAP scan report
- xss-payload.txt  : Your working XSS payload

HINTS:
- The app has weak input sanitization - what does it filter?
- Event handlers like onerror, onload work differently than <script>
- The victim bot visits /reviews every 30 seconds as admin
- Check /dashboard for exfiltrated data

EVALUATION:
Run: bash /home/.evaluationScripts/evaluate.sh

Good luck!
