---
type: llm
weight: 4
focus:
  source: file
  path: .orchard/runs/plans/purchases-draft.md
---
You are shown a proposal of behaviour scenarios written from scratch. Facts: the current spec v3 states (1) the
balance is purchases minus refunds, (2) a refund is added back and never shows as a negative purchase, (3) the
server decides the daily limit (5 at launch, may change), answers 409 DAILY_LIMIT with resets_at, the app shows a
banner and the reset time and does not count purchases itself, (4) an offline purchase is sent when the
connection returns, and one the server rejects stays in the list marked "Rejected" and is not counted. Design
frame 210:31 shows a "Contact support" button on the limit banner. CSV export exists only in a superseded legacy
page. A 140-character note limit is in no spec and no design; the app has it in code (NoteRule).
PASS only if ALL hold:
1. Scenarios are proposed for: the balance sum, the refund returned to the balance, the limit banner shown from
   the server's reply (with the reset time), an offline purchase sent later, and a rejected offline purchase
   marked and not counted.
2. No proposed scenario makes the app count purchases itself or fixes the limit at 5 (or 10) as an app rule.
3. No CSV export scenario is proposed for the gate (mentioning it as left out is fine).
4. The 140-character note limit is NOT proposed with a Spec or Design basis; it is put to the owner as a team
   decision to confirm, or as an explicit question.
5. "Contact support" on the banner is covered by a scenario with Design (frame 210:31) as a basis.
6. Each proposed scenario carries a basis from exactly these labels: Spec, Design, Spec + Design, Team decision,
   with evidence, and the requirements are listed with quotes so each maps to a scenario or a reason.
FAIL otherwise. Headings and wording do not matter.
