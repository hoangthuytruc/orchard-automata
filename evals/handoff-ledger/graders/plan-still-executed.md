---
type: regex
pattern: 'Status:\s*executed'
match: contains
target:
  source: file
  path: .orchard/runs/plans/led-refund.md
---
