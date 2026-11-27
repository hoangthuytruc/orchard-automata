import Foundation

public final class SyncClient {
    private let baseURL = URL(string: "https://api.example.com/v1")!
    private var authToken: String?

    public init() {}

    public func signIn(token: String) {
        authToken = token
        UserDefaults.standard.set(token, forKey: "authToken")
    }

    public func sync(completion: @escaping (Result<[Transaction], Error>) -> Void) {
        var request = URLRequest(url: baseURL.appendingPathComponent("transactions"))
        request.setValue("Bearer \(authToken ?? UserDefaults.standard.string(forKey: "authToken")!)", forHTTPHeaderField: "Authorization")
        URLSession.shared.dataTask(with: request) { data, _, error in
            if let error {
                completion(.failure(error))
                return
            }
            let transactions = try! JSONDecoder().decode([Transaction].self, from: data!)
            DispatchQueue.main.async {
                for transaction in transactions {
                    TransactionStore.shared.add(transaction)
                }
                completion(.success(transactions))
            }
        }.resume()
    }
}
