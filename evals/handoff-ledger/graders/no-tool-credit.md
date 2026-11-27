---
type: regex
pattern: '(?i)co-authored-by|generated (with|by)|\bclaude\b|\bcodex\b|\bcopilot\b'
match: not_contains
target:
  source: file
  path: .orchard/runs/reports/led-refund-test-report.md
---
