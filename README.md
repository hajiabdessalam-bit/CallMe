# CallMe

Personal Voice Alarm for iPhone.

## Requirements
- Xcode 26+
- iOS 26+ deployment target
- AlarmKit entitlement (requires Apple Developer approval)

## Project
Generated with XcodeGen from `project.yml`. Generate with:
```bash
xcodegen generate
```

## Build
```bash
xcodebuild -project CallMe.xcodeproj -scheme CallMe -sdk iphoneos build
```

## Test MP3
Place a short MP3 at `CallMe/audio/test-message.mp3` and re-run generate.
