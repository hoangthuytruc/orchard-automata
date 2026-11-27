# Impact checklist

Walked by `plan` for every change that gets a full plan (a compact bug-fix plan does not walk it; see
`$ORCHARD/workflows/bug-fix.md`). The answers go into the plan's section 4, "Impact"
(`$ORCHARD/templates/plan.md`), one row per perspective with its owner.

## How to walk it

1. **Read the current behaviour first**, in the code of every area the change touches: screens, view models, use
   cases, repositories, endpoints, fixtures, and the tests that bind the area today. Each claim about current
   behaviour carries `path:line`. Code shows what the app does today; it is never a requirement.
2. **Answer every perspective** below for the change; with several tickets, for each ticket and then across them.
   Every perspective gets an answer. "None, because …" with the reason is a valid answer; a perspective left out
   is not. No perspective is skipped in silence.
3. **Name the owner** of each impact: the app (this plan), the backend, product, design, another feature, QA or
   release. An impact owned outside this plan is an open question or a "Not covered" line in the plan, never work
   the plan takes on quietly.
4. **Reconcile.** Every conflict the walk turns up (ticket against ticket, acceptance criteria against design,
   design against spec, requirement against current backend behaviour, requirement against another feature's rule)
   is settled by `$ORCHARD/docs/boundaries.md`, "Conflicts": the agent settles it only when a written rule picks the
   winner; otherwise both readings, their sources, the consequence of each and the owner go to the plan's open
   questions, asked once with the rest.

## The twelve perspectives

| Perspective | Questions to answer |
| --- | --- |
| UI and UX | Which screens, states (loading, empty, error, offline, maintenance, partial), navigation entries and exits, sheets and dialogs change? Which design frames have no current screen, and which current states have no frame? Dark mode, Dynamic Type, smallest device, landscape if supported. |
| Business rules | Which rules change: role, plan or entitlement gates, limits, ordering, priority between states, time windows, eligibility? Where does each rule live today (`path:line`) and which layer should own it? |
| Data and API | Which endpoints, request fields, response fields, enum values, error codes, paging, idempotency, caching? Which are new, changed, deprecated? Which fixture shapes must exist (happy, empty, edge, 4xx, 5xx, offline, slow)? |
| Backend | What must the backend build or change, by when, in which environment first? Does an existing contract break for older app versions in the field? Feature flags or config keys? |
| Persistence and migration | Stored data, keychain, user defaults, caches or offline queues that change shape; migration and rollback for people who update with old data. |
| Other features | Which features share the touched types, endpoints, fixtures or strings? Which of their tests and scenarios could break? Shared components changed for one feature (`$ORCHARD/references/standards.md`, section 3). |
| Platform and permissions | Notifications, background work, extensions, deep links, universal links, entitlements, privacy prompts, App Store privacy declarations. |
| Analytics | Events and properties added, changed or removed; dashboards that depend on them. |
| Copy and localisation | New or changed strings and their keys, plurals, string length on small screens, translation timing. |
| Accessibility | Labels, traits, focus order, identifiers for UI tests on every new control. |
| Security and privacy | Personal data shown, stored, logged or sent; sign-in and session effects. |
| Release | Target version, flag or remote-config rollout, minimum backend version, store review risk, what QA needs to check by hand. |

An impact that touches stored data, sign-in, payments, concurrency or a shared contract is a reason to give its
package the strong tier and to consider the Strict isolation level (`$ORCHARD/docs/workflow-model.md`, "Tiers" and
"Isolation levels").
