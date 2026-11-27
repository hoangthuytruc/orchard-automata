// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Ledger",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [
        .library(name: "Ledger", targets: ["Ledger"])
    ],
    targets: [
        .target(name: "Ledger", swiftSettings: [.swiftLanguageMode(.v5)]),
        .testTarget(name: "LedgerTests", dependencies: ["Ledger"], swiftSettings: [.swiftLanguageMode(.v5)])
    ]
)
