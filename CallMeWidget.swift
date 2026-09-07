import WidgetKit
import SwiftUI
import AlarmKit
import ActivityKit

struct CallMeAlarmAttributes: AlarmAttributes {
    var presentation: AlarmPresentation
    var metadata: CallMeAlarmMetadata
    var tintColor: Color
}

struct CallMeLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: CallMeAlarmAttributes.self) { context in
            VStack {
                Image(systemName: "phone.fill")
                    .font(.title)
                Text(context.attributes.metadata.messageTitle)
                    .font(.headline)
            }
            .padding()
            .activityBackgroundTint(context.attributes.tintColor.opacity(0.2))
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Image(systemName: "phone.fill")
                }
                DynamicIslandExpandedRegion(.trailing) {
                    if let alertState = context.state.mode.alerting {
                        Text(alertState.scheduledTime, format: .dateTime.hour().minute())
                    }
                }
            } compactLeading: {
                Image(systemName: "phone.fill")
            } compactTrailing: {
                if let alertState = context.state.mode.alerting {
                    Text(alertState.scheduledTime, format: .dateTime.hour().minute())
                        .monospacedDigit()
                }
            } minimal: {
                Image(systemName: "phone.fill")
            }
        }
    }
}

@main
struct CallMeWidgetBundle: WidgetBundle {
    var body: some Widget {
        CallMeLiveActivity()
    }
}
