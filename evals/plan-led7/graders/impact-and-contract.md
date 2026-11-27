---
type: llm
weight: 3
focus:
  source: file
  path: .orchard/runs/plans/led-7.md
---
You are shown an implementation plan for ticket LED-7 on a small Swift package in which
`TransactionStore.balanceCents()` sums every amount and ignores whether it is a refund, `SyncClient` has no
handling for HTTP 409, and there is no daily limit and no offline queue.
PASS only if ALL hold:
1. Today's behaviour is described from the code with file references (for example TransactionStore.swift for the
   balance, SyncClient.swift for the network call), not only restated from the ticket.
2. An impact section answers the twelve perspectives: UI and UX, business rules, data and API, backend,
   persistence and migration, other features, platform and permissions, analytics, copy and localization,
   accessibility, security and privacy, release. Each has an impact or "none, because ..."; at most one is
   missing.
3. The contract for `POST /v1/transactions` with the 409 reply, its code DAILY_LIMIT and `resets_at`, and what
   the app does with it, is written down.
4. Requirements are listed with their source and a quote, and each maps to a scenario or states why it has none.
5. The ticket comment about a purchase recorded at 23:59 that syncs after midnight is addressed, as a question
   or a decided rule.
FAIL otherwise. Wording and headings do not matter.
