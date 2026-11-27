import Foundation
import Ledger
import Observation

@MainActor
@Observable
final class BalanceModel {
    private let store = TransactionStore()
    private(set) var transactions: [Transaction] = []
    private(set) var balanceText = LedgerFormatter.string(forCents: 0)

    init(seed: [Transaction]) {
        seed.forEach(store.add)
        Task { await refresh(expecting: seed.count) }
    }

    func add(amountCents: Int, kind: Transaction.Kind) async {
        store.add(Transaction(amountCents: amountCents, kind: kind))
        await refresh(expecting: transactions.count + 1)
    }

    /// The store records a transaction asynchronously; wait until it lists the expected count, then read it.
    private func refresh(expecting count: Int) async {
        for _ in 0..<200 where store.transactions.count < count {
            try? await Task.sleep(for: .milliseconds(10))
        }
        transactions = store.transactions
        balanceText = LedgerFormatter.string(forCents: store.balanceCents())
    }
}
