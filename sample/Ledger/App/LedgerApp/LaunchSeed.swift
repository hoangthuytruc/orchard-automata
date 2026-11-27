import Foundation
import Ledger

/// Reads the starting transactions from the launch arguments, so a test can open the app in a known state.
/// Form: `--seed purchase:5000,refund:1200` (amounts in cents). No `--seed` means an empty ledger.
enum LaunchSeed {
    static func transactions(from arguments: [String]) -> [Transaction] {
        guard let index = arguments.firstIndex(of: "--seed"), index + 1 < arguments.count else { return [] }
        return arguments[index + 1]
            .split(separator: ",")
            .compactMap { entry in
                let parts = entry.split(separator: ":")
                guard parts.count == 2,
                      let kind = Transaction.Kind(rawValue: String(parts[0])),
                      let cents = Int(parts[1]) else { return nil }
                return Transaction(amountCents: cents, kind: kind)
            }
    }
}
