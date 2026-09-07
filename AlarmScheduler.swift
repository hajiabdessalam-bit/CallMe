import AlarmKit
import SwiftUI

struct AlarmScheduler {
    static func scheduleTestAlarm() async throws -> UUID {
        let id = UUID()
        let messageID = "test"
        let messageTitle = "Morning Motivation"

        let metadata = CallMeAlarmMetadata(messageTitle: messageTitle, messageID: messageID)

        let presentation = AlarmPresentation(
            alert: .init(
                title: messageTitle,
                secondaryButton: .answerButton,
                secondaryButtonBehavior: .custom
            )
        )

        let attributes = AlarmAttributes(
            presentation: presentation,
            metadata: metadata,
            tintColor: .accentColor
        )

        let schedule = Alarm.Schedule.fixed(date: Date().addingTimeInterval(60))

        let configuration = AlarmManager.AlarmConfiguration.alarm(
            schedule: schedule,
            attributes: attributes,
            stopIntent: nil,
            secondaryIntent: AnswerCallIntent(messageID: messageID),
            sound: .default
        )

        try await AlarmManager.shared.schedule(id: id, configuration: configuration)
        return id
    }

    static func cancelAlarm(id: UUID) async throws {
        try await AlarmManager.shared.stop(id: id)
    }

    static func activeAlarms() -> [Alarm] {
        AlarmManager.shared.alarms
    }
}

extension AlarmPresentation.Alert {
    static var answerButton: AlarmButton {
        AlarmButton(
            text: "ANSWER",
            textColor: .white,
            systemImageName: "phone.fill"
        )
    }
}
