---
type: llm
weight: 3
focus:
  source: file
  path: .orchard/runs/plans/purchases-recheck.md
---
You are shown a re-check of six scenarios (TS_LED_001 to TS_LED_006) of a product quality gate. The contract
for it: every kept scenario names its basis with one of exactly these labels: "Spec", "Design", "Spec + Design"
or "Team decision"; a design frame is a valid basis on its own for a visible control.
PASS only if ALL hold:
1. Each scenario it keeps or confirms has a basis with those labels (in a Basis column or an explicit "Basis:"
   statement), not only free prose such as "traceable" or "partly".
2. There is a distinct team-decision list or section, and TS_LED_006 is in it as "to confirm" (not decided).
3. Every open question to the owner offers at least two concrete options and names a recommended one.
4. It does not cite numbered rules of some other document (for example "rule 4") as the reason for a verdict.
5. Its status is not approved or accepted.
FAIL otherwise.
