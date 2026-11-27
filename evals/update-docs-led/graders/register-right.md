---
type: llm
weight: 2
focus:
  source: file
  path: docs/features/Purchases.requirements.md
---
You are shown a requirements register written for a feature file. PASS only if ALL hold:
1. It has a row for TS_LED_002 and a row for TS_LED_007, each with a basis (Spec, Design, Spec + Design or Team
   decision), quoted evidence from the spec (and the design frame 210:31 when the basis names Design), and the
   test that proves it.
2. It has no row for a rejected offline purchase scenario and no row for TS_LED_004.
FAIL otherwise. Rows for other scenarios, or a note that the register does not yet cover the whole feature, are
fine.
