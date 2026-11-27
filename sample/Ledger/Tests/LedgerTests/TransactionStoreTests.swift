import XCTest
@testable import Ledger

final class TransactionStoreTests: XCTestCase {
    func testAddIncreasesBalance() {
        let store = TransactionStore()
        store.add(Transaction(amountCents: 500, kind: .purchase))
        sleep(1)
        XCTAssertEqual(store.balanceCents(), 500)
    }
}
