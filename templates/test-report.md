# Test report: <name>

<!-- Top part: for the developer. One screen, plain words, enough to accept or send back. Verdict first.
     No paths, type names, test names or commands up here. -->

## Verdict
<Ready to accept | Not ready | Blocked>, in one sentence with the reason.
<!-- The verdict is the first line printed by scripts/verdict.py, quoted, never written by hand; its reasons, in plain words.
     Every delivered scenario links at least one piece of evidence (docs/principles.md, "What counts as evidence").
     Pictures that could not be captured are the script's gaps, named under What was built; they do not decide the verdict. -->

## What was built
- <behaviour, in the person's words> <screenshot, or screen recording for a journey, where one could be captured; otherwise "no picture: <why>">

## What was not built
- <behaviour>: <why>. Its code and tests were removed.
Or: everything in the plan was built.

## How it was checked
<n> automated tests added, all passing on the final change. <n> review rounds; the last review found nothing that blocks.
Real backend: <what was checked and what it showed>, or not needed.
Not checked: <what, and why>.

## What I need from you
1. <a NOTE, Low finding, NIT or open question, in plain words>. I recommend <fix | leave>, because <one line>.
Or: nothing; say "accept" to close.

---

# Detail
Plan: <path> · Final change: <commit + diff hash> · Workflow: <name> · Isolation: <level> · Rounds: <n>

## Scenarios
<!-- A ticket's acceptance criterion appears here only through its scenario, or as the plan's stated reason for none
     under Not delivered or Not run. There is no separate criteria table.
     Evidence: the test's record, plus whichever of these exist: the screenshot or recording (named by scenario id),
     the network log, the code reference. A picture that could not be captured is written "no picture: <reason>". -->
| Scenario | Delivered | Kind | Test | Result on final change | Screenshot or recording | Network log | Code reference | Check record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Design frames
<!-- One row per frame in scope. The app picture shows that frame's state, no other; when no state matches, say so.
     A design comparison has a person as oracle: it is listed under manual checks until a snapshot is approved. -->
| Frame | State | Design picture | App screenshot | Match (for a person to judge) |
| --- | --- | --- | --- | --- |

## Findings
| # | Type | Severity | Where | Finding | Final state (fixed in round n · open · for the developer) |
| --- | --- | --- | --- | --- | --- |

## Checks run
<!-- Every row from the verify evidence file: the command, the state of the change it ran against, the exit status. -->
| Check | Command | Selection | Ran on | Exit | Summary | Time |
| --- | --- | --- | --- | --- | --- | --- |

## Not run
| Check | Why | What would run it |
| --- | --- | --- |

## Real-backend checks
| Hypothesis | Environment | Request shape | Status | Reply shape | Cleaned up | Gap class and owner |
| --- | --- | --- | --- | --- | --- | --- |

## Manual checks for a person
| Item | Why no automated check reaches it |
| --- | --- |

## Not delivered
| Scenario | Why | Code and tests removed |
| --- | --- | --- |

## Draft pull-request body
<Filled from the project's PR template when the profile names one. Carries the top part of this report (verdict
with its reasons, what was built and not, how it was checked, what is needed from the reviewer) and links or embeds
each screenshot and recording, named by scenario. The plan, this report and the evidence files stay out of git.
Never mentions an AI or a tool.>
