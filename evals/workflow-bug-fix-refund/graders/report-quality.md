---
type: llm
weight: 3
focus:
  source: file
  path: .orchard/runs/reports/refund-sign-test-report.md
---
You are shown the test report of a bug fix (a refund made the balance go up). PASS only if ALL hold:
1. It opens with a verdict in plain words for the developer.
2. It shows the regression test failing before the fix and passing after it, on the final change.
3. It lists the review's findings with type, severity and state, or says plainly the review found none.
4. It lists the checks run with their actual results, and what did not run with the reason.
5. It claims no commit, push or pull request and does not say a scenario file was edited.
FAIL otherwise. Headings and wording do not matter.
