#!/usr/bin/env python3
"""
Minimal valid Xcode project generator for CallMe.
Creates a .xcodeproj with:
- CallMe app target (SwiftUI + AlarmKit + AVFoundation)
- CallMeWidget extension target (WidgetKit live activity)
- Pre-written Info.plist, entitlements, test-message.wav bundled as resource
"""
import os, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
XCODEDIR = ROOT / "CallMe.xcodeproj"
WORKSPACE = XCODEDIR / "project.xcworkspace"
PBXPROJ = XCODEDIR / "project.pbxproj"

def uid():
    return str(uuid.uuid4()).upper()

# ═══════════════════════════════════════════════════════════════════════════════
# PASS 1: Collect all UUIDs
# ═══════════════════════════════════════════════════════════════════════════════

# File references
app_swift_refs = {name: uid() for name in
    ["CallMeApp.swift", "ContentView.swift", "CallMeAlarmMetadata.swift",
     "AnswerCallIntent.swift", "AudioPlayer.swift", "AlarmScheduler.swift"]}
widget_swift_refs = {name: uid() for name in
    ["CallMeWidget.swift", "CallMeWidgetIntentPlaceholder.swift"]}
plist_app_ref = uid()
plist_widget_ref = uid()
ent_ref = uid()
audio_ref = uid()

# Build files
app_swift_bf = {ref: uid() for ref in app_swift_refs.values()}
widget_swift_bf = {ref: uid() for ref in widget_swift_refs.values()}
bf_plist_app = uid()
bf_plist_widget = uid()
bf_ent = uid()
bf_audio = uid()

# Build phases
app_src_phase = uid()
app_fw_phase = uid()
app_res_phase = uid()
widget_src_phase = uid()
widget_fw_phase = uid()
widget_res_phase = uid()

# Product references
callme_app_ref = uid()
widget_appex_ref = uid()

# Groups
project_group = uid()
callme_group = uid()
widget_group = uid()

# Build configurations
app_debug_cfg = uid()
app_release_cfg = uid()
app_cfg_list = uid()
widget_debug_cfg = uid()
widget_release_cfg = uid()
widget_cfg_list = uid()
proj_debug_cfg = uid()
proj_release_cfg = uid()
proj_cfg_list = uid()

# Targets
widget_target = uid()
widget_proxy = uid()
app_dep = uid()
callme_target = uid()

# ═══════════════════════════════════════════════════════════════════════════════
# PASS 2: Assemble text for each object
# ═══════════════════════════════════════════════════════════════════════════════

def settings_text(d):
    return " ".join(f"{k} = {v};" for k, v in d.items())

def build_settingsObject(uuid_val, settings_dict, name):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = XCBuildConfiguration;\n"
        f"\t\tbuildSettings = {{{settings_text(settings_dict)}}}\n"
        f"\t\tname = {name};\n"
        f"\t}};"
    )

def buildConfigList(uuid_val, debug, release):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = XCConfigurationList;\n"
        f"\t\tbuildConfigurations = ({debug}, {release});\n"
        f"\t\tdefaultConfigurationName = Debug;\n"
        f"\t}};"
    )

def groupObj(uuid_val, name, path, children):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXGroup;\n"
        f"\t\tname = {name};\n"
        f"\t\tpath = {path};\n"
        f"\t\tchildren = ({children});\n"
        f"\t\tsourceTree = <group>;\n"
        f"\t}};"
    )

def fileRef(uuid_val, path, type_hint="sourcecode.swift"):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXFileReference;\n"
        f"\t\tlastKnownFileType = {type_hint};\n"
        f"\t\tpath = {path};\n"
        f"\t\tsourceTree = SOURCE_ROOT;\n"
        f"\t}};"
    )

def buildFile(uuid_val, file_ref_uuid):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXBuildFile;\n"
        f"\t\tfileRef = {file_ref_uuid};\n"
        f"\t}};"
    )

def sourcesBuildPhase(uuid_val, files_list):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXSourcesBuildPhase;\n"
        f"\t\tbuildActionMask = 2147483647;\n"
        f"\t\tfiles = ({files_list});\n"
        f"\t\trunOnlyWhenInstalling = NO;\n"
        f"\t\tsourceBuildPhase = YES;\n"
        f"\t}};"
    )

def frameworksBuildPhase(uuid_val):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXFrameworksBuildPhase;\n"
        f"\t\tbuildActionMask = 2147483647;\n"
        f"\t\tfiles = ();\n"
        f"\t\trunOnlyWhenInstalling = NO;\n"
        f"\t}};"
    )

def resourcesBuildPhase(uuid_val, files_list="()"):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXResourcesBuildPhase;\n"
        f"\t\tbuildActionMask = 2147483647;\n"
        f"\t\tfiles = {files_list};\n"
        f"\t\trunOnlyWhenInstalling = NO;\n"
        f"\t}};"
    )

def nativeTarget(uuid_val, cfg_list, src_phase, fw_phase, res_phase,
                 deps, product_ref, product_type):
    return (
        f"\t{uuid_val} = {{\n"
        f"\t\tisa = PBXNativeTarget;\n"
        f"\t\tbuildConfigurationList = {cfg_list};\n"
        f"\t\tbuildPhases = ({src_phase}, {fw_phase}, {res_phase});\n"
        f"\t\tbuildRules = ();\n"
        f"\t\tdependencies = ({deps});\n"
        f"\t\tname = ;  # filled below\n"
        f"\t\tproductName = ;  # filled below\n"
        f"\t\tproductReference = {product_ref};\n"
        f"\t\tproductType = {product_type};\n"
        f"\t}};"
    )

# ── App debug/release settings ────────────────────────────────────────────────
app_debug_settings = {
    "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
    "ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME": "AccentColor",
    "CODE_SIGN_IDENTITY": "",
    "CODE_SIGN_STYLE": "Automatic",
    "CURRENT_PROJECT_VERSION": "1",
    "DEVELOPMENT_TEAM": "",
    "ENABLE_PREVIEWS": "YES",
    "INFOPLIST_FILE": "CallMe/Info.plist",
    "MARKETING_VERSION": "1.0.0",
    "PRODUCT_BUNDLE_IDENTIFIER": "com.callme.app",
    "SWIFT_VERSION": "5.0",
    "TARGETED_DEVICE_FAMILY": "1",
    "SDKROOT": "iphoneos",
    "CODE_SIGN_ENTITLEMENTS": "CallMe/CallMe.entitlements",
    "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks",
    "OTHER_LDFLAGS": "$(inherited) -framework AlarmKit -framework AppIntents -framework WidgetKit -framework ActivityKit -framework AVFoundation",
    "CLANG_ENABLE_MODULES": "YES",
    "GENERATE_INFOPLIST_FILE": "NO",
}
app_release_settings = dict(app_debug_settings)
app_release_settings["SWIFT_OPTIMIZATION_LEVEL"] = "-O"
app_release_settings["DEBUG_INFORMATION_FORMAT"] = "dwarf-with-dsym"
del app_release_settings["ENABLE_PREVIEWS"]

# ── Widget debug/release settings ─────────────────────────────────────────────
widget_debug_settings = {
    "SKIP_INSTALL": "YES",
    "PRODUCT_BUNDLE_IDENTIFIER": "com.callme.app.widget",
    "TARGETED_DEVICE_FAMILY": "1",
    "SDKROOT": "iphoneos",
    "SWIFT_VERSION": "5.0",
    "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks @executable_path/../../Frameworks",
    "INFOPLIST_FILE": "CallMeWidget/Info.plist",
    "GENERATE_INFOPLIST_FILE": "NO",
    "CLANG_ENABLE_MODULES": "YES",
}
widget_release_settings = dict(widget_debug_settings)
widget_release_settings["DEBUG_INFORMATION_FORMAT"] = "dwarf-with-dsym"

# ── Project debug/release settings ────────────────────────────────────────────
proj_debug_settings = {
    "ALWAYS_SEARCH_USER_PATHS": "NO",
    "CLANG_ANALYZER_NONNULL": "YES",
    "CLANG_CXX_LANGUAGE_STANDARD": "gnu++20",
    "CLANG_CXX_LIBRARY": "libc++",
    "CLANG_ENABLE_MODULES": "YES",
    "CLANG_ENABLE_OBJC_ARC": "YES",
    "CLANG_WARN_BOOL_CONVERSION": "YES",
    "CLANG_WARN_CONSTANT_CONVERSION": "YES",
    "CLANG_WARN_DIRECT_OBJC_ISA_USAGE": "YES_ERROR",
    "CLANG_WARN_DOCUMENTATION_COMMENTS": "YES",
    "CLANG_WARN_EMPTY_BODY": "YES",
    "CLANG_WARN_INFINITE_RECURSION": "YES",
    "CLANG_WARN_INT_CONVERSION": "YES",
    "CLANG_WARN_NON_LITERAL_NULL_CONVERSION": "YES",
    "CLANG_WARN_OBJC_ROOT_CLASS": "YES_ERROR",
    "CLANG_WARN_SUSPICIOUS_MOVES": "YES",
    "CLANG_WARN_UNREACHABLE_CODE": "YES",
    "CLANG_WARN__DUPLICATE_METHOD_MATCH": "YES",
    "DEBUG_INFORMATION_FORMAT": "dwarf-with-dsym",
    "ENABLE_STRICT_OBJC_MSGSEND": "YES",
    "ENABLE_TESTABILITY": "YES",
    "GCC_OPTIMIZATION_LEVEL": "0",
    "GCC_PRECOMPILE_PREFIX_HEADER": "NO",
    "GCC_WARN_ABOUT_RETURN_TYPE": "YES_ERROR",
    "GCC_WARN_UNINITIALIZED_AUTOS": "YES_AGGRESSIVE",
    "GCC_WARN_UNUSED_FUNCTION": "YES",
    "GCC_WARN_UNUSED_VARIABLE": "YES",
    "IPHONEOS_DEPLOYMENT_TARGET": "26.0",
    "SDKROOT": "iphoneos",
    "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG",
    "SWIFT_OPTIMIZATION_LEVEL": "-Onone",
}
proj_release_settings = dict(proj_debug_settings)
proj_release_settings["SWIFT_OPTIMIZATION_LEVEL"] = "-O"
proj_release_settings["DEBUG_INFORMATION_FORMAT"] = "dwarf-with-dsym"
del proj_release_settings["SWIFT_ACTIVE_COMPILATION_CONDITIONS"]

# ═══════════════════════════════════════════════════════════════════════════════
# PASS 2: Build object texts
# ═══════════════════════════════════════════════════════════════════════════════

texts = {}  # uuid -> text

# File references
for name, ref in app_swift_refs.items():
    texts[ref] = fileRef(ref, f"CallMe/{name}", "sourcecode.swift")
for name, ref in widget_swift_refs.items():
    texts[ref] = fileRef(ref, f"CallMeWidget/{name}", "sourcecode.swift")
texts[plist_app_ref] = fileRef(plist_app_ref, "CallMe/Info.plist", "text.plist.xml")
texts[plist_widget_ref] = fileRef(plist_widget_ref, "CallMeWidget/Info.plist", "text.plist.xml")
texts[ent_ref] = fileRef(ent_ref, "CallMe/CallMe.entitlements", "text.plist.entitlements")
texts[audio_ref] = fileRef(audio_ref, "CallMe/test-message.wav", "audio.wav")

# Build files
for ref, bf in app_swift_bf.items():
    texts[bf] = buildFile(bf, ref)
for ref, bf in widget_swift_bf.items():
    texts[bf] = buildFile(bf, ref)
texts[bf_plist_app] = buildFile(bf_plist_app, plist_app_ref)
texts[bf_plist_widget] = buildFile(bf_plist_widget, plist_widget_ref)
texts[bf_ent] = buildFile(bf_ent, ent_ref)
texts[bf_audio] = buildFile(bf_audio, audio_ref)

# Build phases
app_src_files = ", ".join(app_swift_bf.values())
texts[app_src_phase] = sourcesBuildPhase(app_src_phase, app_src_files)
texts[app_fw_phase] = frameworksBuildPhase(app_fw_phase)
texts[app_res_phase] = resourcesBuildPhase(app_res_phase, str(bf_audio))

widget_src_files = ", ".join(widget_swift_bf.values()) + f", {bf_plist_widget}"
texts[widget_src_phase] = sourcesBuildPhase(widget_src_phase, widget_src_files)
texts[widget_fw_phase] = frameworksBuildPhase(widget_fw_phase)
texts[widget_res_phase] = resourcesBuildPhase(widget_res_phase)

# Groups
texts[project_group] = groupObj(project_group, "CallMe", "",
    ", ".join([
        str(callme_group), str(widget_group), str(plist_app_ref),
        str(plist_widget_ref), str(ent_ref), str(audio_ref),
        str(callme_app_ref), str(widget_appex_ref), str(proj_cfg_list)
    ]))
texts[callme_group] = groupObj(callme_group, "CallMe", "CallMe",
    ", ".join([str(plist_app_ref), str(ent_ref), str(audio_ref)]))
texts[widget_group] = groupObj(widget_group, "CallMeWidget", "CallMeWidget",
    str(plist_widget_ref))

# Build configurations
texts[app_debug_cfg] = build_settingsObject(app_debug_cfg, app_debug_settings, "Debug")
texts[app_release_cfg] = build_settingsObject(app_release_cfg, app_release_settings, "Release")
texts[app_cfg_list] = buildConfigList(app_cfg_list, app_debug_cfg, app_release_cfg)

texts[widget_debug_cfg] = build_settingsObject(widget_debug_cfg, widget_debug_settings, "Debug")
texts[widget_release_cfg] = build_settingsObject(widget_release_cfg, widget_release_settings, "Release")
texts[widget_cfg_list] = buildConfigList(widget_cfg_list, widget_debug_cfg, widget_release_cfg)

texts[proj_debug_cfg] = build_settingsObject(proj_debug_cfg, proj_debug_settings, "Debug")
texts[proj_release_cfg] = build_settingsObject(proj_release_cfg, proj_release_settings, "Release")
texts[proj_cfg_list] = buildConfigList(proj_cfg_list, proj_debug_cfg, proj_release_cfg)

# Product references
texts[callme_app_ref] = (
    f"\t{callme_app_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\texplicitFileType = wrapper.application;\n"
    f"\t\tincludeInIndex = 0;\n"
    f"\t\tpath = CallMe.app;\n"
    f"\t\tsourceTree = BUILT_PRODUCTS_DIR;\n"
    f"\t}};"
)
texts[widget_appex_ref] = (
    f"\t{widget_appex_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\texplicitFileType = wrapper.app-extension;\n"
    f"\t\tincludeInIndex = 0;\n"
    f"\t\tpath = CallMeWidget.appex;\n"
    f"\t\tsourceTree = BUILT_PRODUCTS_DIR;\n"
    f"\t}};"
)

# Targets
widget_deps = "()"
texts[widget_target] = (
    f"\t{widget_target} = {{\n"
    f"\t\tisa = PBXNativeTarget;\n"
    f"\t\tbuildConfigurationList = {widget_cfg_list};\n"
    f"\t\tbuildPhases = ({widget_src_phase}, {widget_fw_phase}, {widget_res_phase});\n"
    f"\t\tbuildRules = ();\n"
    f"\t\tdependencies = {widget_deps};\n"
    f"\t\tname = CallMeWidget;\n"
    f"\t\tproductName = CallMeWidget;\n"
    f"\t\tproductReference = {widget_appex_ref};\n"
    f"\t\tproductType = com.apple.product-type.app-extension;\n"
    f"\t}};"
)

texts[widget_proxy] = (
    f"\t{widget_proxy} = {{\n"
    f"\t\tisa = PBXContainerItemProxy;\n"
    f"\t\tcontainerPortal = {project_group};\n"
    f"\t\tproxyType = 1;\n"
    f"\t\tremoteGlobalID = {widget_target};\n"
    f"\t\tremoteInfo = CallMeWidget;\n"
    f"\t}};"
)

texts[app_dep] = (
    f"\t{app_dep} = {{\n"
    f"\t\tisa = PBXTargetDependency;\n"
    f"\t\ttarget = {widget_target};\n"
    f"\t\ttargetProxy = {widget_proxy};\n"
    f"\t}};"
)

texts[callme_target] = (
    f"\t{callme_target} = {{\n"
    f"\t\tisa = PBXNativeTarget;\n"
    f"\t\tbuildConfigurationList = {app_cfg_list};\n"
    f"\t\tbuildPhases = ({app_src_phase}, {app_fw_phase}, {app_res_phase});\n"
    f"\t\tbuildRules = ();\n"
    f"\t\tdependencies = ({app_dep});\n"
    f"\t\tname = CallMe;\n"
    f"\t\tproductName = CallMe;\n"
    f"\t\tproductReference = {callme_app_ref};\n"
    f"\t\tproductType = com.apple.product-type.application;\n"
    f"\t}};"
)

# ── PBXProject (root object) ─────────────────────────────────────────────────
proj_obj_id = uid()
texts[proj_obj_id] = (
    f"\t{proj_obj_id} = {{\n"
    f"\t\tisa = PBXProject;\n"
    f"\t\tbuildConfigurationList = {proj_cfg_list};\n"
    f"\t\tbuildStyles = ();\n"
    f"\t\tbuildTypes = ();\n"
    f"\t\tcolumnBreaks = ();\n"
    f"\t\tcontainsScriptDuplicatesInBuildOrder = NO;\n"
    f"\t\tdefaultConfigurationIsVisible = 0;\n"
    f"\t\tdefaultConfigurationName = Debug;\n"
    f"\t\tdevelopmentTeam = ;\n"
    f"\t\thasScannedUserDefaults = 0;\n"
    f"\t\tknownRegions = (en);\n"
    f"\t\tmainGroup = {project_group};\n"
    f"\t\tproductModuleName = CallMe;\n"
    f"\t\tprojectDirPath = ;\n"
    f"\t\tprojectRoot = $SRCROOT;\n"
    f"\t\ttargets = ({callme_target}, {widget_target});\n"
    f"\t\tsourceTree = <group>;\n"
    f"\t}};"
)

# Order: PBXProject first, then everything else (grouped for readability)
ordered = [proj_obj_id]
ordered.extend([
    project_group, callme_group, widget_group,
    plist_app_ref, plist_widget_ref, ent_ref, audio_ref,
    callme_app_ref, widget_appex_ref, proj_cfg_list,
    app_cfg_list, app_debug_cfg, app_release_cfg,
    widget_cfg_list, widget_debug_cfg, widget_release_cfg,
    proj_debug_cfg, proj_release_cfg,
    app_src_phase, app_fw_phase, app_res_phase,
    widget_src_phase, widget_fw_phase, widget_res_phase,
    bf_plist_app, bf_plist_widget, bf_ent, bf_audio,
    *app_swift_bf.values(), *widget_swift_bf.values(),
    *app_swift_refs.values(), *widget_swift_refs.values(),
    widget_target, widget_proxy, app_dep, callme_target,
])

# ═══════════════════════════════════════════════════════════════════════════════
# Write pbxproj
# ═══════════════════════════════════════════════════════════════════════════════

XCODEDIR.mkdir(parents=True, exist_ok=True)
WORKSPACE.mkdir(parents=True, exist_ok=True)

lines = ["// !$*UTF8*$!", ""]
for uuid_val in ordered:
    lines.append(texts[uuid_val])
lines.append("")
PBXPROJ.write_text("\n".join(lines))

xcwork = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Workspace\n'
    '   version = "1.0">\n'
    '   <FileRef\n'
    '      location = "self:CallMe.xcodeproj">\n'
    '   </FileRef>\n'
    '</Workspace>'
)
(WORKSPACE / "contents.xcworkspacedata").write_text(xcwork)

print(f"✓ Generated {PBXPROJ}")
print(f"✓ Generated {WORKSPACE / 'contents.xcworkspacedata'}")
print(f"  App target 'CallMe' — {len(app_swift_refs)} Swift files + resources")
print(f"  Widget target 'CallMeWidget' — {len(widget_swift_refs)} Swift files")
print()
print("Next: open CallMe.xcodeproj in Xcode 26+ and build for iPhone simulator or device.")
print("      XcodeGen not required — project is hand-crafted and ready to open.")
