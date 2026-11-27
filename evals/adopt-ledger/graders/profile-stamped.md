---
type: regex
pattern: 'file:[^\s|#`]+#[0-9a-f]{8}'
match: contains
target:
  source: file
  path: .orchard/profile.md
---
