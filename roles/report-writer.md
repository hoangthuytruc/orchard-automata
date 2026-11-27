# Role: report writer (Strict only)

At the Strict isolation level (risk, or a long run whose context is full) the test report is written by a separate agent that starts from the files alone. The verdict does not depend on who writes the report: `scripts/verdict.py` computes it at every level and the report quotes it. The writer follows the `handoff` skill ([skills/handoff/SKILL.md](../skills/handoff/SKILL.md)) from its files alone.

| Receives | Is not given | May write | Returns |
| --- | --- | --- | --- |
| The brief below | The conversation; the implementers' returns; the coordinator's view of the run | `<reports_dir>/<YYYY-MM-DD>-<name>-test-report.md` only | The report path and its top part, as its final message |

Tier: light.

## The brief (the coordinator fills it in)

```markdown
# Brief: test report for <name>

Repository root: <absolute path>
Skill set: <absolute path>. Follow skills/handoff/SKILL.md.
Plan: <plans_dir>/<name>.md
Evidence: <reports_dir>/<name>/evidence.jsonl
Reviews: <plans_dir>/<name>/review-round-1.md … review-round-<n>.md
Screens: <reports_dir>/<name>/screens/
Workflow: <name> · Isolation: Strict · Rounds: <n> · Run: <RUN_ID>
Ended early: <reason with both sides, quoted>, or no.

Write <reports_dir>/<YYYY-MM-DD>-<name>-test-report.md from <skill set>/templates/test-report.md. The verdict is the output of
`verdict.py <evidence file> <plan> --reviews <plans_dir>/<name>/` (with `--ended-early` when the run ended early), quoted.
Every claim links to a record in the evidence file made on the final change (`evidence.py stale` prints nothing).
What has no record is "not run".
Edit nothing else. Never commit. Never mention an AI or a tool.
```
