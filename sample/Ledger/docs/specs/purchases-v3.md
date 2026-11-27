# Purchases (spec v3, current, status: SPECS READY)

1. **Balance.** The balance is the sum of all purchases minus all refunds.
2. **Refunds.** A refund is added back to the balance at once. It never shows as a negative purchase.
3. **Daily limit.** The server decides how many purchases a day are allowed (5 at launch, may change without an app
   release). When the limit is reached the server answers `POST /v1/transactions` with 409 and `code: DAILY_LIMIT`,
   `resets_at`. The app then shows the limit banner and the reset time. The app does not count purchases itself.
4. **Offline.** A purchase recorded offline is sent when the connection returns. If the server rejects it, it stays in
   the list marked "Rejected" and is not counted in the balance.
