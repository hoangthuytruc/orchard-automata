---
type: llm
weight: 4
focus:
  source: file
  path: .orchard/runs/plans/led-7.md
---
You are shown an implementation plan for ticket LED-7 (daily purchase limit and refunds). Facts: spec v3, the
current spec and ranked first by the project profile, says the balance is purchases minus refunds; the server
decides the daily limit and answers `POST /v1/transactions` with 409, `code: DAILY_LIMIT` and `resets_at`; the
app then shows the limit banner and the reset time; the app does not count purchases itself; a purchase recorded
offline and rejected by the server stays in the list marked "Rejected" and is not counted. The ticket says 5
purchases a day in the user's time zone; design frame 210:14 shows a counter "3 of 10 purchases today"; frame
210:31 shows the banner with a "Contact support" button. The profile says a ticket is not a basis. Scenario
TS_LED_004 says the app refuses the sixth purchase without asking the server. A 140-character note limit exists
only in scenario TS_LED_006 and in code (NoteRule), in no spec or design. The owner was not available.
PASS only if ALL hold:
1. The plan's status is draft or another status before approval; not approved, executed, accepted or documented.
2. The design shows the banner from the server's refusal with the reset time, and does not make the app count
   purchases or fix the limit at 5 or 10. The 5-versus-10 conflict is settled by the spec with the rule named
   (spec over ticket and design on behaviour) or raised as a question; it is never adopted as an app rule.
3. Each added or changed scenario carries a basis from exactly these labels: Spec, Design, Spec + Design, Team
   decision; with evidence (a quote, a clause or a frame id); and names its test or a `@blocked:<reason>` tag.
4. TS_LED_004 is proposed for removal, or for a change that stops the app counting purchases.
5. The 140-character limit has no Spec or Design basis; it is a team decision for the owner to confirm, or an
   open question.
6. "Contact support" is covered with Design (frame 210:31) as its basis, or raised as a question naming the frame.
7. At least one work package names the files it owns and a tier (strong or light) with a reason, and the
   scenario files (docs/features/*.feature or a glob matching them) are listed as locked.
8. Each open question offers options and names a recommended one.
FAIL otherwise. Headings and wording do not matter.
