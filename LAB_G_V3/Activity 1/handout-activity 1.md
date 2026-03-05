# Lab-Z Handout: OWASP ZAP Fundamentals 

## Objective
Learn a complete beginner-to-practical ZAP workflow on default OWASP Juice Shop:
1. Configure and use ZAP correctly
2. Build endpoint coverage (discovery)
3. Analyze passive and active scan findings
4. Fuzz real parameters from captured traffic
5. Validate interesting behavior manually

## Lab Scope
- Target app: `http://localhost:30000`
- ZAP Web UI: `http://localhost:30004/zap/`
- ZAP Proxy: localhost:30003


### Phase 1: Setup and Baseline Traffic
1. Open Juice Shop: `http://localhost:30000`.
2. Open ZAP UI: `http://localhost:30004/zap/`.
3. In ZAP, keep **Intercept OFF** initially.
4. Browse Juice Shop normally for 5-10 minutes:
- Home and product pages
- Search
- Login/Register pages
- Any flow that triggers API calls
5. In ZAP, confirm traffic appears in:
- **Sites** tree
- **History**

Goal: collect realistic traffic before scanning.

### Phase 2: Discovery
1. Right-click target in Sites tree (`http://localhost:30000`).
2. Run **Spider**.
3. Let it finish and review newly discovered paths.

Goal: increase coverage beyond manual clicks.

### Phase 3: Scan and Alert Review
1. Run **Active Scan** on the target scope.
2. Open the **Alerts** tab and review at least 3 alerts.
3. For each alert, capture these details in notes:
- Risk level
- Affected URL/parameter
- Evidence shown by ZAP
- Related request/response pair from History

Goal: learn how to read findings, not just run tools.

### Phase 4: Fuzzing (Discover-First)
1. From History, choose one request with meaningful input parameters.
- Query params, body fields, or IDs are all valid targets.
2. Send that request to **Fuzzer**.
3. Fuzz one parameter position at a time.

Use payload groups like:
- Numeric boundaries: `-1`, `0`, `1`, `999999`
- Type mismatch: `abc`, `true`, `null`
- Encoding/special chars: `%27`, `%22`, `%2e%2e%2f`, `%252e%252e%252f`
- Input length variants: very short vs very long strings

For each run, compare:
- HTTP status code
- Response length
- Response body (error text, missing fields, extra fields)
- Any unusual timing differences

Goal: identify behavior changes that suggest weak validation or access control gaps.

### Phase 5: Manual Validation (Repeater)
1. Send 1-2 interesting requests to **Repeater**.
2. Change one parameter at a time.
3. Re-send and verify whether behavior is consistent.

Goal: separate real findings from noise/false positives.


