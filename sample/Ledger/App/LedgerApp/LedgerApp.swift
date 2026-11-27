import SwiftUI

@main
struct LedgerApp: App {
    @State private var model = BalanceModel(seed: LaunchSeed.transactions(from: ProcessInfo.processInfo.arguments))

    var body: some Scene {
        WindowGroup {
            BalanceView(model: model)
        }
    }
}
