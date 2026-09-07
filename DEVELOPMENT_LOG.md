# CallMe — Development Log

## Environment
- **OS**: Windows 10 (development machine)
- **iOS build target**: iPhone (simulated via browser-based research; no local Xcode)
- **Goal**: Prove the core AlarmKit → ANSWER → local audio flow using AlarmKit on iOS 26

## 2026-09-07 — Research & Architecture

### What is AlarmKit
- iOS 26+ only (WWDC25). No backport to iOS 18 or earlier.
- System-level alarms that break through Silent, Do Not Disturb, and Focus by design.
- Requires `NSAlarmKitUsageDescription` in Info.plist + user consent.
- Entitlement `com.apple.developer.alarmkit` required (Apple Developer Portal request + review).
- `AlarmManager.shared` is the main API: authorize, schedule, cancel, observe `alarmUpdates`.

### Alarm structure
- `AlarmConfiguration` with either `.alarm(schedule:)` or `.timer(countdownDuration:)`.
- Schedule shapes: `.fixed(Date)`, `.relative(hour:minute, repeats:)` supporting weekly recurrence.
- `AlarmPresentation`: `.Alert` (system-rendered alert UI), `.Countdown`, `.Paused`.
- Alert UI = title + stop button (required) + optional secondary button + tint.
- The **alert UI is system-rendered**, not custom SwiftUI. You can only configure title, buttons, tint.

### Custom actions
- Custom buttons → `AlarmButton` → associated with an App Intent via `secondaryIntent`.
- Button behavior: `.countdown` (snooze) or `.custom` (runs the intent).
- Intents must conform to `LiveActivityIntent` (runs in app process), `AudioPlaybackIntent`, or `AppIntent` (widget process by default).
- **`openAppWhenRun = true`** on a `LiveActivityIntent` causes the intent to run in the **app's process** and bring it to the foreground.

### Key findings relevant to "ANSWER → audio plays"
1. **Yes, a custom secondary button is supported** on the alert UI. You can title it "ANSWER".
2. **Yes, tapping it runs an App Intent in the app process** — the app launches/activates.
3. **Yes, the intent can run arbitrary app code**, including starting AVAudioPlayer.
4. **The app must have a Widget Extension with an `ActivityConfiguration`** if using countdown presentation. For `.alarm` (fixed time) without a countdown, a widget is still strongly recommended (and for Dynamic Island/Lock Screen countdown UI it's required). Without it, countdown alarms disappear silently.
5. **Sound**: AlarmKit supports `AlertConfiguration.AlertSound.named("...")` with a system sound name, or default. Custom audio files as *alarm sounds* are limited — you reference a system sound name. Custom audio playback after ANSWER must be done via AVAudioPlayer inside the intent, not via AlarmKit's sound slot.
6. **Permissions**: AlarmKit authorization + the standard audio session (AVAudioSession) — for playback when locked/backgrounded you need the audio session configured for `.playback` and likely the `audio` background mode (`UIBackgroundModes` = `audio`) so the app can play after launch from the lock screen.
7. **Locked phone**: AlarmKit alert appears on the Lock Screen. **Apple's documentation says the secondary intent is only available after first unlock.** The app may need Face ID / passcode authentication. LiveActivityIntent with `openAppWhenRun` is designed to launch the app. Audio playback after launch from the lock screen is supported with the audio background mode + proper AVAudioSession category — but the custom alarm action may require first unlock.
8. **Background / suspended**: The alarm fires via system infrastructure independent of the app's state. The intent launches the app if needed. So scenarios B, D should work in principle: the app does *not* need to be running when the alarm fires.

### Limitations identified
- The **alert UI itself is not fully custom** — you cannot build a completely bespoke "incoming call" UI in the alert. You get title + buttons + tint. You can approximate the *feel* but not replicate a full call-screen UI. The closest is to make the title dramatic and the ANSWER button prominent.
- **Custom audio as the alarm sound** is limited to named system sounds. The "alarm sound" is the pre-ANSWER sound. After ANSWER, you play your own audio via AVAudioPlayer — this is the key design: AlarmKit wakes the user, the ANSWER action launches the app and plays the message audio.
- **Widget Extension required** for countdown presentation. For a fixed-time alarm with a short pre-alert, you likely still want the widget for Lock Screen / Dynamic Island polish. This is a real build-complexity cost for Phase 1, but it's required by the framework for a robust experience.
- **Simulator limitations**: The entitlement requires a provisioning profile with the entitlement. Simulator support exists but needs signed profile. Real-device testing is the true test.
- **Secondary intent availability**: Apple's current documentation indicates custom alarm actions (secondary intent) may only be available after first unlock. This needs testing on a real device.

### Phase 1 Bugs FOUND AND FIXED (2026-09-07, post-ZIP review)

Four concrete bugs were identified by external review:

**Bug 1: Audio file extension mismatch.**
- `AudioPlayer.swift` looked for `.mp3` extension (`let ext = "mp3"`).
- Bundled file is `test-message.wav`.
- **Fix**: Changed `let ext = "mp3"` → `let ext = "wav"` in `AudioPlayer.swift:48`.

**Bug 2: Intent received alarmUUID instead of messageID.**
- `AlarmScheduler.scheduleTestAlarm()` created `AnswerCallIntent(alarmID: id.uuidString)`.
- `AudioPlayer.bundleAudioURL(for:)` maps `"test"` → `test-message.wav`, but any other string → `<string>.wav` which doesn't exist.
- **Fix**: Changed `AnswerCallIntent` parameter from `alarmID` to `messageID`, initialized with `messageID: "test"`. `AlarmScheduler` now passes `AnswerCallIntent(messageID: messageID)`.

**Bug 3: Test Call and Preview buttons were empty.**
- `ContentView.swift` had `Button("Test Call") {}` and `Button("Preview") {}`.
- **Fix**: Wired up buttons to actual actions:
  - "Preview" → `AudioPlayer.shared.start(messageID: "test")`
  - "Test Call" → `AlarmScheduler.scheduleTestAlarm()`

**Bug 4: Missing `EnvironmentKey` for `authorizationState`.**
- `ContentView.swift` used `@Environment(\.authorizationState)` but no `EnvironmentKey` was defined.
- `CallMeApp.swift` called `.environment(\.authorizationState, ...)` without defining the key.
- **Fix**: Added `AuthorizationStateKey: EnvironmentKey` and `EnvironmentValues.authorizationState` extension in `ContentView.swift`.

### Phase 1 Bugs Found and Fixed (2026-09-07, post-ZIP review)

Four concrete bugs were identified by external review:

**Bug 1: Audio file extension mismatch.**
- `AudioPlayer.swift` looked for `.mp3` extension (`let ext = "mp3"`).
- Bundled file is `test-message.wav`.
- **Fix**: Changed `let ext = "mp3"` → `let ext = "wav"` in `AudioPlayer.swift:48`.

**Bug 2: Intent received alarmUUID instead of messageID.**
- `AlarmScheduler.scheduleTestAlarm()` created `AnswerCallIntent(alarmID: id.uuidString)`.
- `AudioPlayer.bundleAudioURL(for:)` maps `"test"` → `test-message.wav`, but any other string → `<string>.wav` which doesn't exist.
- **Fix**: Changed `AnswerCallIntent` parameter from `alarmID` to `messageID`, initialized with `messageID: "test"`. `AlarmScheduler` now passes `AnswerCallIntent(messageID: messageID)`.

**Bug 3: Test Call and Preview buttons were empty.**
- `ContentView.swift` had `Button("Test Call") {}` and `Button("Preview") {}`.
- **Fix**: Wired up buttons to actual actions:
  - "Preview" → `AudioPlayer.shared.start(messageID: "test")`
  - "Test Call" → `AlarmScheduler.scheduleTestAlarm()`

**Bug 4: Missing `EnvironmentKey` for `authorizationState`.**
- `ContentView.swift` used `@Environment(\.authorizationState)` but no `EnvironmentKey` was defined.
- `CallMeApp.swift` called `.environment(\.authorizationState, ...)` without defining the key.
- **Fix**: Added `AuthorizationStateKey: EnvironmentKey` and `EnvironmentValues.authorizationState` extension in `ContentView.swift`.

- Single SwiftUI app target + Widget Extension target.
- Metadata type: `CallMeAlarmMetadata` (nonisolated, AlarmMetadata) carrying `messageTitle: String`, `messageID: String`.
- App Intent: `AnswerCallIntent: LiveActivityIntent` with `openAppWhenRun = true`, `@Parameter messageID`, and `perform()` that:
  - calls `AudioPlayer.shared.start(messageID:)`,
  - which configures AVAudioSession `.playback` and plays the bundled audio file.
- `AlarmPresentation.Alert` with:
  - title: message title (e.g. "Morning Motivation"),
  - system-provided stop button (no `stopIntent`),
  - secondaryButton: "ANSWER" with `.custom` behavior + `AnswerCallIntent(messageID:)`.
- `AlarmScheduler.scheduleTestAlarm()` schedules an alarm ~60s ahead using `.fixed(Date)`.
- Home screen: shows next alarm, Test Call button (schedules 60s test), Preview button (plays audio immediately), denied-state alert.
- Bundled audio: `test-message.wav` (2s G-major arpeggio, mono 44100Hz 16-bit WAV).

## Files in the ZIP

| Path | Purpose |
|---|---|
| `CallMe.xcodeproj/project.pbxproj` | Xcode project (app + widget targets) |
| `CallMe.xcodeproj/project.xcworkspace/contents.xcworkspacedata` | Workspace ref |
| `CallMe/CallMeApp.swift` | `@main` entry, AlarmKit auth check |
| `CallMe/ContentView.swift` | Home screen + EnvironmentKey for authorizationState |
| `CallMe/CallMeAlarmMetadata.swift` | `AlarmMetadata` type |
| `CallMe/AnswerCallIntent.swift` | `LiveActivityIntent` with `openAppWhenRun`, now takes `messageID` |
| `CallMe/AudioPlayer.swift` | `AVAudioPlayer` wrapper, `.playback` session, now looks for `.wav` |
| `CallMe/AlarmScheduler.swift` | `scheduleTestAlarm()`, `cancelAlarm()`, ANSWER button extension |
| `CallMe/Info.plist` | `NSAlarmKitUsageDescription`, `UIBackgroundModes = audio` |
| `CallMe/CallMe.entitlements` | `com.apple.developer.alarmkit = true` |
| `CallMe/test-message.wav` | 2s G-major arpeggio test audio |
| `CallMeWidget/CallMeWidget.swift` | `WidgetBundle` + `ActivityConfiguration` for Live Activity |
| `CallMeWidget/CallMeWidgetIntentPlaceholder.swift` | Placeholder for compilation |
| `CallMeWidget/Info.plist` | Widget extension plist |
| `DEVELOPMENT_LOG.md` | This file |
| `README.md` | Requirements, build commands |
| `project.yml` | XcodeGen spec (alternative to hand-crafted `.xcodeproj`) |
| `build_test_audio.py` | Regenerates `test-message.wav` |
| `gen2.py`, `gen3.py`, `gen_final.py`, `gen_xcodeproj.py`, `generate_xcodeproj.py`, `generate_test_audio.py` | Earlier generator iterations |

## Build prerequisites

1. **macOS + Xcode 26+** — opens `CallMe.xcodeproj` directly (no XcodeGen needed)
2. **iOS 26+ deployment target**
3. **AlarmKit entitlement approval** — `com.apple.developer.alarmkit` must be granted by Apple to your team ID before `AlarmManager.shared.schedule` will work
4. **Code signing** — a provisioning profile carrying the entitlement (simulator or device)

## Build commands

```bash
# Open in Xcode
open CallMe.xcodeproj

# Or CLI on macOS
xcodebuild -project CallMe.xcodeproj -scheme CallMe -sdk iphonesimulator -configuration Debug build
xcodebuild -project CallMe.xcodeproj -scheme CallMe -destination 'platform=iOS Simulator,name=iPhone 16' run
```

## Test scenarios (Phase 1, to be run on real iPhone later)

A. App open → alarm fires → ANSWER → audio
B. App backgrounded → alarm → ANSWER → audio
C. iPhone locked → alarm → ANSWER → audio *(may require first unlock per Apple docs)*
D. App removed from recents → alarm → ANSWER → audio
E. Silent / Focus mode

## Known limitations

- The alarm **alert UI is system-rendered** — you get title + stop button + custom ANSWER button + tint, not a fully bespoke incoming-call screen.
- The **alarm sound** is a system sound name; the message audio plays **after ANSWER** via AVAudioPlayer (this is the intended architecture).
- Widget Extension is **required for countdown presentation**; for pure fixed-time alarms it's strongly recommended for Lock Screen / Dynamic Island polish.
- Simulator requires a provisioning profile with the entitlement.
- **Secondary intent availability**: Apple's current documentation indicates custom alarm actions (secondary intent) may only be available after first unlock. This needs testing on a real device.
- The entitlement `com.apple.developer.alarmkit` is managed by Apple and must be approved before scheduling works.

## Next steps

1. Get this ZIP onto a Mac / cloud Mac.
2. Open `CallMe.xcodeproj` in Xcode 26+.
3. Build for iOS Simulator or physical iPhone.
4. Test scenarios A–E.
5. Report failures → fix → repeat.

