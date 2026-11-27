---
name: review
description: Review a change to an iOS or Swift codebase - a pull request number, a branch, a commit range, a path, or the uncommitted working tree - with a separate, read-only reviewer that never saw the author's reasoning. Findings are anchored to a line each, with type (Blocker, Risk, NOTE), severity (High, Medium, Low, NIT), evidence and a concrete fix; how the change is built and how it fits the codebase is asked as open questions in plain words. On request it leaves the result as a draft review on the pull request; it never approves. Use for "review", "look over this", "PR 42", "before I merge", "second opinion on this diff", "code review", "audit this change".
argument-hint: "[PR number | branch | base..head | path] [--plan <plan file>] [--draft | --post]"
---

# review

Resolves the target, starts one separate reviewer, shows its result unchanged, and records the run. The judge is never the session that wrote or discussed the change, so this skill always starts a reviewer, even when called alone. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The target; the plan when one exists. The reviewer reads the rest itself, including the product sources (spec, design, ticket) the profile names | Nothing in the repository. The review in `<plans_dir>/<name>/review-round-<r>.md` in a run; with `--draft` or `--post`, one review on the pull request | Edits code; reviews in this session; approves; posts one comment per finding outside a review; mentions an AI or a tool in posted text | Nothing; `--draft` or `--post` to write to the pull request | The reviewer's final message, saved unchanged; `post_review.py` output when posting |

## Why

A reviewer who read the author's reasoning tends to confirm it; tests cover only what someone thought to test. It rests on independent review, separation of duties, checklists and counterexamples.

## Stance

Adversary. Which input, state or ordering breaks this? Tier: strong for the full review; light for a review of fixes.

## General steps

1. Read the intent and the result, not the author's reasoning. 2. Judge the whole: does it fit the problem and its surroundings, and does it do what the product sources require? 3. Scan for known patterns of failure. 4. For each suspicion, construct the specific case that breaks it. 5. Report only what has a breaking case or missing evidence, each with a fix; put what cannot be decided as a question.

## Method

1. **Open** as in [AGENTS.md](../../AGENTS.md#a-skill-called-alone), with `--skill review --task "review <target>"`. In a run, the coordinator has opened the log.
2. **Resolve the target**:
   - a number → pull request `<n>` (needs `gh`);
   - a branch name → that branch against the default branch;
   - `a..b` → that commit range;
   - a path → the files under it at `HEAD`;
   - nothing → the uncommitted working tree plus commits ahead of the default branch.
   Repository root: `git rev-parse --show-toplevel`. `--draft` and `--post` default off.
3. **Start one reviewer** by [roles/reviewer.md](../../roles/reviewer.md), on the strong tier, the way the tool's adapter says (`$ORCHARD/adapters/<tool>/README.md`). Its prompt is one line and nothing else: `Review <target> in the repository at <root>. Follow <skill set>/roles/reviewer.md.` Add `Plan: <path>.` when a plan exists. Never pass the conversation, an implementer's return, or your own view. Do not review in parallel yourself.
4. **Review of fixes** (in a run, after a fix round): the reviewer on the light tier, given the findings that were fixed and the change since the last review, as [references/run-flow.md](../../references/run-flow.md) says.
5. **Show the result.** The general comments in full, then the inline findings most severe first, each with its `path:line`. Change nothing in them. Add at most one line when something conflicts with a decision the developer already made in this session.
6. **Record.** Count the findings; log each blocking one with `runlog.py event RUN_ID finding --note "<type> <severity> <rule cited>"`. Take tokens from the tool's completion report when it gives them, else `na`. Alone: `runlog.py finish RUN_ID --outcome delivered --findings <N>`; later, `runlog.py rate RUN_ID --accepted <acted on> --rejected <dismissed>` measures precision.
7. **Write to the pull request only with `--draft` or `--post`**, and only for a pull request target: `python3 -I "$ORCHARD/scripts/post_review.py" <n> <payload> --draft|--post`.
   - `--draft` leaves one pending review only the developer sees; prefer it when they have not said which.
   - `--post` submits it: "request changes" when a Blocker, a Risk, or a High or Medium finding exists, otherwise "comment". Never "approve".
   Give the review URL and the counts the script prints. Without either flag, say nothing was written.

## Rule that always holds

Read-only; a finding names a failing case; it never approves.

## Gotchas

- **The hosting service rejects a whole review when one comment's line is outside the diff.** The script checks every anchor first and moves one it cannot anchor into the summary; never post the payload with a bare API call.
- **A pending review blocks a second one.** One user holds one pending review per pull request; the script says so and stops rather than deleting it.
- **A force-push after the review moves the lines.** The payload names the commit it was written for; when the head moved, review again instead of posting.
- **One review per run.** Never a second review to fix the first; to change a draft, the developer edits it.
- **A project may ship its own review agent or checklist.** Say so in one line; the reviewer still applies the project's rules through the profile.
