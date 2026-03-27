# Activity 1: Manual Rebinding Pivot

## Goal

Use one hostname (`evil.attacker.local`) and show that changing its backend routing gives a different result.

## Do This

```bash
cd /home/labDirectory
labfctl status
fetch-sim evil.attacker.local /admin
labfctl set evil.attacker.local admin-a
fetch-sim evil.attacker.local /admin
```

## What Should Happen

1. First `/admin` request does not return the token.
2. After `set ... admin-a`, the same `/admin` request returns `IITB{...}`.

## Submit

Put only the token in `SUBMIT_FLAG.txt`.

## If You Get Stuck

1. Check routing state: `labfctl status`
2. Check request routing log: `labfctl logs proxy`
3. Optional browser view: `http://127.0.0.1:8080`
