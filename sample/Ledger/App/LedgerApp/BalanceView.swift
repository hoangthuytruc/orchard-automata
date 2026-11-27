import Ledger
import SwiftUI

struct BalanceView: View {
    let model: BalanceModel
    @State private var adding: Ledger.Transaction.Kind?

    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack {
                        Text("Balance")
                        Spacer()
                        Text(model.balanceText)
                            .font(.title2.monospacedDigit())
                            .accessibilityIdentifier("balance.amount")
                    }
                }
                Section("Transactions") {
                    ForEach(Array(model.transactions.enumerated()), id: \.element.id) { index, transaction in
                        HStack {
                            Text(transaction.kind == .purchase ? "Purchase" : "Refund")
                            Spacer()
                            Text(LedgerFormatter.string(forCents: transaction.amountCents))
                        }
                        .accessibilityElement(children: .combine)
                        .accessibilityIdentifier("transaction.row.\(index)")
                    }
                }
            }
            .navigationTitle("Ledger")
            .toolbar {
                ToolbarItemGroup(placement: .bottomBar) {
                    Button("Add purchase") { adding = .purchase }
                        .accessibilityIdentifier("balance.addPurchase")
                    Spacer()
                    Button("Add refund") { adding = .refund }
                        .accessibilityIdentifier("balance.addRefund")
                }
            }
            .sheet(item: $adding) { kind in
                AddTransactionView(kind: kind) { cents in
                    Task { await model.add(amountCents: cents, kind: kind) }
                }
            }
        }
    }
}

extension Ledger.Transaction.Kind: @retroactive Identifiable {
    public var id: String { rawValue }
}
