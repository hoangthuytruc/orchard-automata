---
type: llm
weight: 4
focus:
  source: file
  path: .orchard/runs/plans/purchases-recheck.md
---
You are shown a re-check of six scenarios (TS_LED_001 to TS_LED_006) that act as a product quality gate. Facts:
the current spec v3 states the balance rule (clause 1) and that a refund is added back (clause 2). Only design
frame 210:31 shows a "Contact support" button. Spec v3 clause 3 says the server decides the daily limit and the
app does not count purchases itself. CSV export exists only in a superseded legacy page and in no design frame.
A 140-character note limit is in no spec and no design; the app has it in code (NoteRule).
PASS only if ALL hold:
1. TS_LED_001 and TS_LED_002 are kept with the current spec as their basis, each with a quote or clause.
2. TS_LED_003 is kept with Design (frame 210:31) as its basis, alone or with the spec for the banner; it is not
   held back merely because only the design shows the button.
3. TS_LED_004 is not confirmed as written: the re-check says the limit is decided by the server and/or that the
   app must not count purchases itself, citing spec clause 3.
4. TS_LED_005 is marked for removal because only a legacy or superseded page supports it.
5. TS_LED_006 is NOT confirmed by a spec or design; it is a team decision for the owner to confirm (or an
   equivalent explicit question), not silently kept and not presented as decided.
FAIL otherwise. Headings and wording do not matter.
