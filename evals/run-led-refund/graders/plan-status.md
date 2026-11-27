---
type: llm
weight: 1
focus:
  source: file
  path: .orchard/runs/plans/led-refund.md
---
You are shown a plan file after it was run. PASS only if BOTH hold: (1) its status line reads "executed" (not
"approved", and not "accepted" or "documented"); (2) its Result section is filled with what was delivered and the
test for each item. FAIL otherwise.
