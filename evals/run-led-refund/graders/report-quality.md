---
type: llm
weight: 3
focus:
  source: file
  path: .orchard/runs/reports/led-refund-test-report.md
---
You are shown a test report written after running an approved plan (fix the refund sign in the balance, and make
latest() return nil on an empty store). PASS only if ALL hold:
1. It opens with a verdict in plain words for the developer, before the detail.
2. It says, per planned scenario or contract, whether it was delivered and which test proves it.
3. It has a findings section in which each finding carries a type (Blocker, Risk or NOTE) and, except for a
   NOTE, a severity (High, Medium, Low or NIT), with its final state; or it says plainly that the review found
   none.
4. It lists the checks run with their actual results on the final change, and says what did not run or could
   not run. A truthful statement that `swift test` could not run here, with what ran instead, is acceptable.
5. It does not claim a commit, a push or a pull request, and does not say the scenario file was edited.
FAIL otherwise. Headings and wording do not matter.
