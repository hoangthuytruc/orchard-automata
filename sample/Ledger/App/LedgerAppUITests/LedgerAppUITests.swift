import XCTest

final class LedgerAppUITests: XCTestCase {
    override func setUp() {
        continueAfterFailure = false
    }

    func testPurchaseThenRefundShowsBalance() {
        let app = XCUIApplication()
        app.launchArguments = ["--seed", "purchase:5000", "-AppleLocale", "en_US", "-AppleLanguages", "(en)"]
        app.launch()

        add(in: app, button: "balance.addPurchase", amount: "25.00")
        add(in: app, button: "balance.addRefund", amount: "10.00")

        XCTAssertTrue(app.descendants(matching: .any)["transaction.row.2"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.staticTexts["balance.amount"].label, "$65.00")
    }

    private func add(in app: XCUIApplication, button: String, amount: String) {
        app.buttons[button].tap()
        let field = app.textFields["add.amount"]
        XCTAssertTrue(field.waitForExistence(timeout: 5))
        field.tap()
        field.typeText(amount)
        app.buttons["add.save"].tap()
        XCTAssertTrue(app.buttons[button].waitForExistence(timeout: 5))
    }
}
