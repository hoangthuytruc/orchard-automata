import Ledger
import SwiftUI

struct AddTransactionView: View {
    let kind: Ledger.Transaction.Kind
    let onSave: (Int) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var amount = ""

    /// Amount typed as a decimal with a dot (`12.50`), converted to cents.
    private var cents: Int? {
        guard let value = Decimal(string: amount), value > 0 else { return nil }
        return NSDecimalNumber(decimal: value * 100).intValue
    }

    var body: some View {
        NavigationStack {
            Form {
                TextField("Amount", text: $amount)
                    .keyboardType(.decimalPad)
                    .accessibilityIdentifier("add.amount")
            }
            .navigationTitle(kind == .purchase ? "Add purchase" : "Add refund")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .accessibilityIdentifier("add.cancel")
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        if let cents { onSave(cents) }
                        dismiss()
                    }
                    .disabled(cents == nil)
                    .accessibilityIdentifier("add.save")
                }
            }
        }
    }
}
