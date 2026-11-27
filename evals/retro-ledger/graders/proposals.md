---
type: llm
weight: 4
focus:
  source: file
  path: .orchard/runs/retro.md
---
You are shown the output of a retrospective over a run log. Facts about the log: six runs. In three runs on
different tasks (LED-8, LED-9, LED-12) the reviewer raised a finding that a test waits with sleep instead of an
injected clock or an awaited call, citing the test strategy's no-sleeps rule; one of those runs (LED-9) was also
sent back at acceptance for the same reason. One run had one flaky test (SyncClientTests.testRetry); one run
ended early once because the profile's lint key was missing. Four runs are feature-development at the standard
isolation level and two are bug-fix at the shared level, so no group has five runs.
PASS only if ALL hold:
1. There is a proposal for the repeated sleep-in-tests signal that names the runs behind it, its cause, the
   smallest change that removes it (for example a check a script can run, or a sharper rule plus an eval case
   that fails before and passes after) and where that change lives.
2. No proposal is made for the flaky test or for the missing lint key: each is set aside as a single event
   (mentioning it as a note is fine).
3. No proposal loosens a rule, removes a check or widens what an agent may decide.
4. Figures are grouped by workflow and isolation, and no trend is claimed: each group is reported as having no
   baseline yet (fewer than five runs).
5. It does not claim to have changed any skill, reference, script, profile or review rule; the owner decides.
FAIL otherwise. Headings and wording do not matter.
