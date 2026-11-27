# LED-7: Daily purchase limit and refunds in the balance

Type: Story · Status: Ready for development · Fix version: 2.4.0 · Figma: see figma-LED-7.md

## Description
Users overspend by mistake. We cap purchases per day and show refunds correctly in the balance.

## Acceptance criteria
1. The balance adds refunds back: balance = sum of purchases subtracted from the starting amount, plus refunds.
2. A user can record at most 5 purchases per calendar day in their own time zone. Refunds do not count.
3. When the limit is reached, recording another purchase is refused and the user sees why, with the time the limit resets.
4. The backend enforces the same limit: POST /v1/transactions answers 409 with code DAILY_LIMIT when it is reached.
5. Offline purchases are queued; when the queue syncs and the backend answers 409, the queued purchase is marked rejected and the user is told.

## Comments
- Backend (Minh): 409 body is {"code":"DAILY_LIMIT","resets_at":"<ISO-8601 UTC>"}. Available on staging from sprint 32.
- QA (Lan): what happens to a purchase recorded at 23:59 that syncs after midnight?
