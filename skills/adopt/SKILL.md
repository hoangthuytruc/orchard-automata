---
name: adopt
description: Set a project up for the Orchard skill set by drafting its project profile from repository discovery, each value with the file it was found in and that file's hash, or marked missing; the developer confirms it. Also re-discovers only the values whose source file changed. Use for "adopt orchard", "set up the skill set here", "write the project profile", "the profile check failed", "a profile source changed", or before any other skill in a project with no `.orchard/profile.md`.
argument-hint: "[repo root] [--recheck]"
---

# adopt

Writes `.orchard/profile.md`, the one place a project's facts live: commands, folders, locked files, base branch, source ranking, real-backend rules. Every other skill reads its facts from there and stops when a required one it reads is missing. `adopt` records how the project works; it never decides how it should work. `$ORCHARD` is the folder two levels above this file.

## Contract

| Reads | Writes | Never | Needs from the developer | Evidence |
| --- | --- | --- | --- | --- |
| The repository: build files, guides (`CLAUDE.md`, `AGENTS.md`, nested guides), lint and CI settings, PR template, test folders | `.orchard/profile.md` as a draft; with `--recheck`, only the values whose source changed | Guesses a value; fills a missing one from habit; edits code, tests, CI or build settings; commits | Confirmation of each value, and the values no file states | `profile_check.py stamp` and `check` output; each value's `file:<path>#<hash>` or `stated: <who> <date>` |

## Why

A guessed command or path makes every later result wrong while it looks right. It rests on configuration as an explicit contract: a value is either written somewhere and hashed, or stated by the owner, or missing.

## Stance

Clerk. Where is this fact written down? If nowhere, it is missing, not guessed. Tier: light, recommended.

## General steps

1. List the facts the work will depend on. 2. Look for each in a primary source. 3. Record the value with its source. 4. Mark a fact with no source as missing; do not fill it in. 5. Have the owner confirm, and check again when a source changes.

## Method

1. **Open.** If `.orchard/profile.md` exists, run the profile check from [AGENTS.md](../../AGENTS.md#a-skill-called-alone) without `--skill` (every key) and keep its exit-3 list: with `--recheck`, that list is the whole scope. Then `python3 -I "$ORCHARD/scripts/runlog.py" start --workflow alone --skill adopt --task "<project>: profile"`.
2. **Discover.** `bash "$ORCHARD/scripts/discover.sh" <repo root>`. Read every guide and file it lists, and any `.orchard/` files it shows.
3. **Draft.** Copy `$ORCHARD/templates/project-profile.md` to `.orchard/profile.md` (or, with `--recheck`, open the existing one). For each key, in the template's order:
   - Find the value in a file: a `Makefile` target, `Package.swift`, `project.yml`, `Project.swift`, a `.xcworkspace`, a CI workflow, `.swiftlint.yml`, a testing guide, the PR template. Write it and the source `file:<path>`, only when git tracks that file (`git ls-files --error-unmatch <path>` succeeds).
   - A value found only in an untracked or ignored file (a private note, a local guide): write it with `stated: <who> <date>` after the developer confirms it in step 4, and name the file in a note. Never cite it as `file:`.
   - A command found only in a guide's prose is still a source: cite the guide.
   - No file states it: write `missing`. Never fill a value from what is usual for iOS projects.
   - Prefer the project's own wrapper (`make test`, a script) over a raw `xcodebuild` or `swift test`.
   - The knowledge base is the project's Gherkin `.feature` files and is always required (template note under "Knowledge base"). When the project has none yet, propose in step 4 the folder where they will live (it may be empty), with `locked_globs` covering it, and say that the first `plan` drafts the first scenarios. Never offer `none`.
   - `locked_globs`: draft the default listed in the template under "Task folders", with the knowledge base and register filled in. Keep a glob for a file the project does not have yet: it locks an empty set. Remove one only on the developer's word.
4. **Ask once.** Put every `missing` required key, and every key where two files disagree, to the developer in one message: the key, what was found where, and a recommended value. Record answers as `stated: <who> <date>`.
5. **Stamp.** `python3 -I "$ORCHARD/scripts/profile_check.py" stamp .orchard/profile.md --root .` rewrites each `file:<path>` source with its hash. Exit 3 lists sources git does not track: turn each into `stated:` as step 3 says.
6. **Check.** `python3 -I "$ORCHARD/scripts/profile_check.py" check .orchard/profile.md --root .` must exit 0. Exit 2 lists what is still missing: back to step 4. When the answers are still pending (the developer has not replied, or cannot be reached in this run), stop here: the profile stays `draft` and the outcome is `blocked`, with the pending keys as findings (step 10).
7. **Keep task files out of git.** `git check-ignore -q <plans_dir>` and `<reports_dir>`. When not ignored, say so and recommend adding them to the exclude file; on the developer's word, append them, creating its folder first, which a fresh or unusual checkout may lack: `exclude=$(git rev-parse --git-path info/exclude); mkdir -p "$(dirname "$exclude")"; printf '%s\n' <plans_dir> <reports_dir> >> "$exclude"`. Record the answer as `plan_files_excluded`.
8. **Review rules.** When `.orchard/review-rules.md` is absent, offer a draft from `$ORCHARD/templates/review-rules.md` holding only rules the guides state, each citing its line. Never invent a rule. When a guide states a rule but no severity, write the severity that the definitions in [references/review-checklist.md](../../references/review-checklist.md) (part D) give a breach, and mark it "to confirm" for the developer.
9. **Confirm.** Show the profile. Set `Status: confirmed <date> by <who>` only on the developer's words; until then it stays `draft`, and other skills may read it but the developer has not vouched for it.
10. **Close.** `runlog.py finish RUN_ID --outcome delivered --findings <missing or disputed keys>`; `--outcome blocked` when step 6 stopped with answers pending.

**Changed sources (`--recheck`, or another skill stopped on exit 3).** Discover only the listed keys again. Same value: re-stamp. Different value: show the confirmed value, the new one and the changed file; write the new value only on the developer's word.

## Rule that always holds

No value without a source. Project guides override core; the profile records them, it does not argue with them.

## Gotchas

- **The default branch is not the base branch.** A ticket that builds on another often starts from that ticket's branch. Record the usual base branch; the plan confirms it again at approval.
- **A command that needs a simulator** also needs `device_policy`: two runs on one simulator stall each other.
- **A new test file may need the project regenerated** before the test command sees it; that is the `generate` key.
- **Personal settings are not project facts.** A model choice or a token goes in `.orchard/agents.local.md`, never in the profile.
