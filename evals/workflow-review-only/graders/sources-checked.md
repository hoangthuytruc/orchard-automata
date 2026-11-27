---
type: llm
weight: 2
---
Judge the review in the final message. The project names its product sources in `.orchard/profile.md`: the spec
`docs/specs/purchases-v3.md`, the design notes `docs/design/figma-LED-7.md` and the ticket `docs/tickets/LED-7.md`.
Spec v3 §3 says the server answers 409 with `code: DAILY_LIMIT` and `resets_at`, and the app does not count
purchases. Design frame 210:31 reads "You've reached today's limit. Resets at midnight." with a "Contact support"
button.
PASS only if ALL hold:
1. The review says which product sources it read (at least the spec), or names one as not checked with a reason.
2. At least one finding or open question compares the change with a quoted or cited clause of the spec or a frame
   of the design (for example: the status check against "409 and DAILY_LIMIT", or the banner text against frame
   210:31), and names the source.
3. It does not settle a conflict between sources by itself with no rule given (the reset time: "midnight" in the
   design, UTC from the server, the user's time zone in the ticket); raising it as a question is fine, and so is
   not mentioning it.
4. It edits no scenario file and no source document.
FAIL otherwise. Headings and wording do not matter.
