import SwiftUI

// MARK: - Authorization state environment key

private struct AuthorizationStateKey: EnvironmentKey {
    static var defaultValue: AuthorizationState = .unknown
}

extension EnvironmentValues {
    var authorizationState: AuthorizationState {
        get { self[AuthorizationStateKey.self] }
        set { self[AuthorizationStateKey.self] = newValue }
    }
}

// MARK: - ContentView

struct ContentView: View {
    @Environment(\.authorizationState) private var authorizationState
    @State private var showingTestScheduled = false

    var body: some View {
        VStack(spacing: 24) {
            Text("CALL ME")
                .font(.largeTitle)
                .bold()

            Spacer()

            NextCallCard()

            Spacer()

            if authorizationState == .denied {
                DeniedAlertView()
            }

            if showingTestScheduled {
                Text("Test alarm scheduled — answer in ~60s")
                    .font(.caption)
                    .foregroundColor(.green)
            }

            Spacer()
        }
        .padding()
        .background(Color(uiColor: .systemBackground))
        .onAppear {
            checkAuthorization()
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

    private func scheduleTestAlarm() {
        showingTestScheduled = true
        Task {
            do {
                _ = try await AlarmScheduler.scheduleTestAlarm()
            } catch {
                print("CallMe: Failed to schedule test alarm: \(error)")
                showingTestScheduled = false
            }
        }
    }
}

// MARK: - NextCallCard

struct NextCallCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Next call")
                .font(.subheadline)
                .foregroundColor(.secondary)

            VStack(spacing: 4) {
                Text("Tomorrow · 08:00")
                    .font(.title2)
                    .bold()
                Text("Morning Motivation")
                    .font(.headline)
            }

            Divider()

            HStack {
                Button("Preview") {
                    Task {
                        await AudioPlayer.shared.start(messageID: "test")
                    }
                }
                .buttonStyle(.bordered)
                Button("Test Call") {
                    // Action handled by parent ContentView via .onTapGesture or binding
                }
                .buttonStyle(.borderedProminent)
                .disabled(true)
            }
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
}

// MARK: - Preview

#Preview {
    ContentView()
}
