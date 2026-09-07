import AppIntents
import AVFoundation

struct AnswerCallIntent: LiveActivityIntent, Sendable {
    static var title: LocalizedStringResource = "Answer Call"
    static var description = IntentDescription("Answer the incoming call alert")
    static var openAppWhenRun: Bool = true

    @Parameter(title: "Message ID")
    var messageID: String

    func perform() async throws -> some IntentResult {
        AudioPlayer.shared.start(messageID: messageID)
        return .result()
    }

    public init(messageID: String) {
        self.messageID = messageID
    }

    public init() {
        self.messageID = ""
    }
}
