import AVFoundation

actor AudioPlayer {
    static let shared = AudioPlayer()

    private var player: AVAudioPlayer?
    private var currentMessageID: String?

    func start(messageID: String) {
        currentMessageID = messageID
        guard let url = bundleAudioURL(for: messageID) else {
            NSLog("[CallMe] Audio file not found for messageID: \(messageID)")
            return
        }

        do {
            try configureAudioSession()
            player = try AVAudioPlayer(contentsOf: url)
            player?.delegate = nil
            player?.prepareToPlay()
            player?.play()
            NSLog("[CallMe] Playing audio for \(messageID)")
        } catch {
            NSLog("[CallMe] Audio playback error: \(error)")
        }
    }

    func stop() {
        player?.stop()
        player = nil
        currentMessageID = nil
    }

    private func configureAudioSession() throws {
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playback, mode: .default, options: [.allowBluetooth, .mixWithOthers])
        try session.setActive(true, options: [.notifyOthersOnDeactivation])
    }

    private func bundleAudioURL(for messageID: String) -> URL? {
        let filename: String
        switch messageID {
        case "test":
            filename = "test-message"
        default:
            filename = messageID
        }
        let ext = "wav"
        guard let url = Bundle.main.url(forResource: filename, withExtension: ext) else {
            return nil
        }
        return url
    }
}

// MARK: - App-side helpers

@MainActor
func scheduleTestAlarmFromApp() async {
    do {
        _ = try await AlarmScheduler.scheduleTestAlarm()
    } catch {
        print("CallMe: Failed to schedule test alarm: \(error)")
    }
}
