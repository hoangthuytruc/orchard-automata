import Foundation

public final class TransactionStore {
    public static let shared = TransactionStore()

    public private(set) var transactions: [Transaction] = []
    private let queue = DispatchQueue(label: "ledger.store")

    public init() {}

    public func add(_ transaction: Transaction) {
        queue.async {
            self.transactions.append(transaction)
        }
    }

    public func balanceCents() -> Int {
        transactions.map { $0.amountCents }.reduce(0, +)
    }

    public func latest() -> Transaction {
        transactions.sorted { $0.date > $1.date }.first!
    }

    public func monthTotalCents(calendar: Calendar = .current) -> Int {
        let now = Date()
        return transactions
            .filter { calendar.isDate($0.date, equalTo: now, toGranularity: .month) }
            .map { $0.amountCents }
            .reduce(0, +)
    }
}
