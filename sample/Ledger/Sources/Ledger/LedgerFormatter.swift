import Foundation

public enum LedgerFormatter {
    static let formatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        return formatter
    }()

    public static func string(forCents cents: Int) -> String {
        formatter.string(from: NSNumber(value: Double(cents) / 100))!
    }
}
