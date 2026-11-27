# Ledger

A small Swift package used by our iOS app to record purchases and refunds and show a balance. Build and test with
`swift build` and `swift test`.
The iOS app `App/LedgerApp.xcodeproj` (scheme `LedgerApp`, UI tests `LedgerAppUITests`, seed with `--seed purchase:5000,refund:1000`) builds with `xcodebuild build -project App/LedgerApp.xcodeproj -scheme LedgerApp -destination 'platform=iOS Simulator,id=<udid>'` and tests with `xcodebuild test` and the same options.
