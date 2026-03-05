#!/bin/sh
set -e

mkdir -p /home/.evaluationScripts
cat > /home/.evaluationScripts/evaluate.json <<'JSON'
{
  "data": [
    {
      "testid": 1,
      "status": "pass",
      "score": 0,
      "maximum marks": 0,
      "message": "No grading configured for this lab."
    }
  ]
}
JSON

cat /home/.evaluationScripts/evaluate.json
