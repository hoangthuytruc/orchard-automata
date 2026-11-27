# Review rules: Ledger (sample)

| Id | Rule | How a breach shows | Severity |
| --- | --- | --- | --- |
| LR-1 | Secrets never go to `UserDefaults` | `UserDefaults` near `token`, `secret`, `password` | High |
| LR-2 | The store is the only writer of transactions | a write to `transactions` outside `TransactionStore` | Medium |
| LR-3 | Money is integer cents end to end | `Double` or `Float` used for an amount before formatting | Medium |

## Project smells for the mechanical scan

- `TransactionStore.shared`: a singleton in a new call site hides a dependency the tests cannot replace.

## Architecture

- Layers: one module, `Ledger`. Models (`Transaction`), store (`TransactionStore`), formatting (`LedgerFormatter`), network (`SyncClient`).
- State: the store owns the list of transactions.
- Dependency injection: by initializer.

## Tests

- XCTest or Swift Testing; time, ids and randomness injected; no `sleep`.
