import Foundation

public struct Transaction: Codable, Equatable, Identifiable {
    public enum Kind: String, Codable {
        case purchase
        case refund
    }

    public let id: UUID
    public let amountCents: Int
    public let kind: Kind
    public let date: Date

    public init(id: UUID = UUID(), amountCents: Int, kind: Kind, date: Date = Date()) {
        self.id = id
        self.amountCents = amountCents
        self.kind = kind
        self.date = date
    }
}
