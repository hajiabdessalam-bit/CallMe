import SwiftUI

@main
struct CallMeApp: App {
    @State private var authorizationState: AuthorizationState = .unknown

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.authorizationState, authorizationState)
                .onAppear {
                    checkAuthorization()
                }
        }
    }

    private func checkAuthorization() {
        authorizationState = AlarmManager.authorizationState
        if authorizationState == .notDetermined {
            Task {
                await AlarmManager.shared.requestAuthorization()
                authorizationState = AlarmManager.authorizationState
            }
        }
    }
}

enum AuthorizationState: Equatable {
    case unknown
    case notDetermined
    case authorized
    case denied
}
