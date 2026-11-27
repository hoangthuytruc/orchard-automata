# Workflow: review-only

## Trigger

A change that already exists and needs an independent review: a pull request, a branch, a commit range, a path, or the uncommitted working tree. It may have been written by someone else, or without the skill set.

## Inputs

- The target, and the plan file when one exists.
- The project profile `.orchard/profile.md`: `guides`, `review_rules`, `pr_template`, `base_branch`. No command is run.
- The agents map (`.orchard/agents.md`, overridden by `.orchard/agents.local.md`), for the reviewer.

## Roles and isolation

- Isolation: the reviewer is always a separate agent; nothing else is started. Logged as Shared.

| State | Role | Tier | Skill |
| --- | --- | --- | --- |
| Intake | Coordinator (the developer's session) | Light | `review` |
| Review | Reviewer, separate agent, read-only | Strong | `review` (reviewer by `roles/reviewer.md`) |
| Ready | Coordinator | Light | `review` |

- Plan verification: not applicable; this workflow has no plan.

## States

| State | Entry | Action | Exit | Evidence |
| --- | --- | --- | --- | --- |
| Intake | A target is named, or none (the working tree) | Resolve the target to a diff and a repository root; find the plan when one exists | The target resolves to a non-empty diff | The target, recorded by `runlog.py start --task` |
| Review | Target resolved | The reviewer reads the project's guides and rules, then a general review, a mechanical scan, a line review and a search for counterexamples. It does not run tests: it judges the evidence that exists and names what is missing | The reviewer's final message: general comments, then inline findings anchored to lines | The review file, saved unchanged |
| Ready | Review saved | Show the review unchanged; on `--draft` or `--post`, leave one review on the pull request | Review shown; with a flag, `post_review.py` printed the review URL and counts | The review file; `post_review.py` output |

## Transitions

- `Intake → Review` when the target resolves to a diff with at least one changed file.
- `Review → Ready` when the reviewer's final message is saved and every inline finding's line lies inside a diff hunk.
- No transition returns to Implement: this workflow changes nothing in the repository.

## Decision points

| When | Person decides | Shown |
| --- | --- | --- |
| Before | Nothing | |
| After | What to do with the findings; whether to post the review | Findings with type, severity, line, evidence and fix; open questions in plain words; what evidence exists and what is missing |

## Ends early when

- The target does not resolve (no such pull request, branch or range) or its diff is empty.
- The pull request's head moved after the review and before posting: review again instead of posting.

## Recovery

- A comment line outside the diff → `post_review.py` moves it into the summary; never post with a bare API call.
- A pending review already exists on the pull request → stop and say so; never delete it.

## Handoffs

- Acting on the findings, submitting or editing a draft review, and any approval belong to the developer. The workflow never approves.
