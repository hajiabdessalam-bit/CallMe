#!/usr/bin/env python3
"""
Minimal valid Xcode project generator for CallMe.
Creates a .xcodeproj with a single pbxproj containing:
- CallMe app target (SwiftUI + AlarmKit + AVFoundation)
- CallMeWidget extension target (WidgetKit live activity)
- Both Info.plist and entitlements are pre-written files
- test-message.wav bundled as a resource
"""
import os, uuid, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
XCODEDIR = ROOT / "CallMe.xcodeproj"
WORKSPACE = XCODEDIR / "project.xcworkspace"
PBXPROJ = XCODEDIR / "project.pbxproj"

def uid():
    return str(uuid.uuid4()).upper()

# ── helpers ────────────────────────────────────────────────────────────────
def file_ref(name, path, type_hint="sourcecode.swift"):
    ref = uid()
    return (ref,
        f"\t{ref} = {{\n"
        f"\t\tisa = PBXFileReference;\n"
        f"\t\tlastKnownFileType = {type_hint};\n"
        f"\t\tpath = {path};\n"
        f"\t\tsourceTree = SOURCE_ROOT;\n"
        f"\t}};"
    )

def source_build_file(fref, settings=""):
    bf = uid()
    s = f'\n\t\tsettings = {settings};' if settings else ""
    return (bf,
        f"\t{bf} = {{\n"
        f"\t\tisa = PBXBuildFile;\n"
        f"\t\tfileRef = {fref};{s}\n"
        f"\t}};"
    )

def group(name, path, children):
    g = uid()
    return (g,
        f"\t{g} = {{\n"
        f"\t\tisa = PBXGroup;\n"
        f"\t\tname = {name};\n"
        f"\t\tpath = {path};\n"
        f"\t\tchildren = {children};\n"
        f"\t\tsourceTree = <group>;\n"
        f"\t}};"
    )

def config_list(debug_cfg, release_cfg, name="Debug"):
    cl = uid()
    return (cl,
        f"\t{cl} = {{\n"
        f"\t\tisa = XCConfigurationList;\n"
        f"\t\tbuildConfigurations = ({debug_cfg}, {release_cfg});\n"
        f"\t\tdefaultConfigurationName = {name};\n"
        f"\t}};"
    )

def build_config(settings_dict, name):
    cfg = uid()
    settings = " ".join(f"{k} = {v};" for k, v in settings_dict.items())
    txt = f"\t{cfg} = {{\n" \
          f"\t\tisa = XCBuildConfiguration;\n" \
          f"\t\tbuildSettings = {{{settings}}}\n" \
          f"\t\tname = {name};\n" \
          f"\t}};"
    return (cfg, txt)

def target_native(name, product_type, product_ref, sources_phase, frameworks_phase,
                  resources_phase, dependencies, config_list_ref, extra=""):
    t = uid()
    deps = dependencies if dependencies else "()"
    return (t,
        f"\t{t} = {{\n"
        f"\t\tisa = PBXNativeTarget;\n"
        f"\t\tbuildConfigurationList = {config_list_ref};\n"
        f"\t\tbuildPhases = ({sources_phase}, {frameworks_phase}, {resources_phase});\n"
        f"\t\tbuildRules = ();\n"
        f"\t\tdependencies = {deps};\n"
        f"\t\tname = {name};\n"
        f"\t\tproductName = {name};\n"
        f"\t\tproductReference = {product_ref};\n"
        f"\t\tproductType = {product_type};\n{extra}"
        f"\t}};"
    )

def target_dependency(target_id, proxy_id):
    d = uid()
    return (d,
        f"\t{d} = {{\n"
        f"\t\tisa = PBXTargetDependency;\n"
        f"\t\ttarget = {target_id};\n"
        f"\t\ttargetProxy = {proxy_id};\n"
        f"\t}};"
    )

def container_proxy(remote_global_id, remote_info, portal):
    p = uid()
    return (p,
        f"\t{p} = {{\n"
        f"\t\tisa = PBXContainerItemProxy;\n"
        f"\t\tcontainerPortal = {portal};\n"
        f"\t\tproxyType = 1;\n"
        f"\t\tremoteGlobalID = {remote_global_id};\n"
        f"\t\tremoteInfo = {remote_info};\n"
        f"\t}};"
    )

# ── locate files ───────────────────────────────────────────────────────────
def find_files(subdir, names):
    found = {}
    for n in names:
        p = ROOT / subdir / n
        if p.is_file():
            found[n] = p
    return found

callme_swift = find_files("CallMe", [
    "CallMeApp.swift",
    "ContentView.swift",
    "CallMeAlarmMetadata.swift",
    "AnswerCallIntent.swift",
    "AudioPlayer.swift",
    "AlarmScheduler.swift",
])

widget_swift = find_files("CallMeWidget", [
    "CallMeWidget.swift",
    "CallMeWidgetIntentPlaceholder.swift",
])

callme_plist = ROOT / "CallMe" / "Info.plist"
widget_plist = ROOT / "CallMeWidget" / "Info.plist"
callme_entitlements = ROOT / "CallMe" / "CallMe.entitlements"
audio_file = ROOT / "CallMe" / "test-message.wav"

# ── build object list ──────────────────────────────────────────────────────
objects = []  # (uuid, text)

# File references
app_files = []
for sname, spath in callme_swift.items():
    ref, ref_text = file_ref(
        sname,
        str(spath.relative_to(ROOT)).replace("\\", "/"),
        "sourcecode.swift")
    objects.append((ref, ref_text))
    app_files.append(ref)

widget_files = []
for sname, spath in widget_swift.items():
    ref, ref_text = file_ref(
        sname,
        str(spath.relative_to(ROOT)).replace("\\", "/"),
        "sourcecode.swift")
    objects.append((ref, ref_text))
    widget_files.append(ref)

(plist_app_ref, plist_app_text) = file_ref("Info.plist",
    "CallMe/Info.plist", "text.plist.xml")
objects.append((plist_app_ref, plist_app_text))

(plist_widget_ref, plist_widget_text) = file_ref("Info.plist",
    "CallMeWidget/Info.plist", "text.plist.xml")
objects.append((plist_widget_ref, plist_widget_text))

(ent_ref, ent_text) = file_ref("CallMe.entitlements",
    "CallMe/CallMe.entitlements", "text.plist.entitlements")
objects.append((ent_ref, ent_text))

(audio_ref, audio_text) = file_ref("test-message.wav",
    "CallMe/test-message.wav", "audio.wav")
objects.append((audio_ref, audio_text))

# Source build files (CallMe app)
app_build_files = []
for ref in app_files:
    bf, bf_text = source_build_file(ref)
    objects.append((bf, bf_text))
    app_build_files.append(bf)

# Widget build files
widget_build_files = []
for ref in widget_files:
    bf, bf_text = source_build_file(ref)
    objects.append((bf, bf_text))
    widget_build_files.append(bf)

# Info.plist build files
bf_plist_app, bf_plist_app_text = source_build_file(plist_app_ref)
objects.append((bf_plist_app, bf_plist_app_text))

bf_plist_widget, bf_plist_widget_text = source_build_file(plist_widget_ref)
objects.append((bf_plist_widget, bf_plist_widget_text))

bf_ent, bf_ent_text = source_build_file(ent_ref)
objects.append((bf_ent, bf_ent_text))

bf_audio, bf_audio_text = source_build_file(audio_ref)
objects.append((bf_audio, bf_audio_text))

# Build phases — CallMe app
app_sources_phase = uid()
objects.append((app_sources_phase,
    f"\t{app_sources_phase} = {{\n"
    f"\t\tisa = PBXSourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({', '.join(app_build_files)});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t\tsourceBuildPhase = YES;\n"
    f"\t}};"))

app_frameworks_phase = uid()
# Link system frameworks
frameworks_refs = []
for fw in ["AlarmKit.framework", "AppIntents.framework", "WidgetKit.framework",
           "ActivityKit.framework", "AVFoundation.framework"]:
    fri, _ = file_ref(fw, f"System/Library/Frameworks/{fw}", "framework")
    frameworks_refs.append(fri)
# We add them as file refs + build files but in practice the linker flags handle them
# Simpler: rely on OTHER_LDFLAGS and don't add explicit framework build files
objects.append((app_frameworks_phase,
    f"\t{app_frameworks_phase} = {{\n"
    f"\t\tisa = PBXFrameworksBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ();\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};"))

app_resources_phase = uid()
objects.append((app_resources_phase,
    f"\t{app_resources_phase} = {{\n"
    f"\t\tisa = PBXResourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({bf_audio});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};"))

# Build phases — Widget extension
widget_sources_phase = uid()
objects.append((widget_sources_phase,
    f"\t{widget_sources_phase} = {{\n"
    f"\t\tisa = PBXSourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({', '.join(widget_build_files)});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t\tsourceBuildPhase = YES;\n"
    f"\t}};"))

widget_frameworks_phase = uid()
objects.append((widget_frameworks_phase,
    f"\t{widget_frameworks_phase} = {{\n"
    f"\t\tisa = PBXFrameworksBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ();\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};"))

widget_resources_phase = uid()
objects.append((widget_resources_phase,
    f"\t{widget_resources_phase} = {{\n"
    f"\t\tisa = PBXResourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ();\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};"))

# Product references
callme_product_ref, callme_product_text = file_ref("CallMe.app",
    "CallMe.app", "wrapper.application")
objects.append((callme_product_ref, callme_product_text))

widget_product_ref, widget_product_text = file_ref("CallMeWidget.appex",
    "CallMeWidget.appex", "wrapper.app-extension")
objects.append((widget_product_ref, widget_product_text))

# PBXProject (root)
project_group = uid()
objects.append((project_group,
    f"\t{project_group} = {{\n"
    f"\t\tisa = PBXGroup;\n"
    f"\t\tchildren = ({plist_app_ref}, {plist_widget_ref}, {ent_ref}, {audio_ref}, {callme_product_ref}, {widget_product_ref}, {project_config_group});\n"
    f"\t\tname = CallMe;\n"
    f"\t\tsourceTree = <group>;\n"
    f"\t}};"))

# Groups structure
callme_group, callme_group_text = group("CallMe", "CallMe",
    f"({plist_app_ref}, {ent_ref}, {audio_ref})")
objects.append((callme_group, callme_group_text))

widget_group, widget_group_text = group("CallMeWidget", "CallMeWidget",
    f"({plist_widget_ref})")
objects.append((widget_group, widget_group_text))

# Build configurations
# App debug/release
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
    "SWIFT_COMPILATION_MODE": "wholemodule",
    "GENERATE_INFOPLIST_FILE": "NO",
}

app_release_settings = dict(app_debug_settings)
app_release_settings["SWIFT_OPTIMIZATION_LEVEL"] = "-O"
app_release_settings["DEBUG_INFORMATION_FORMAT"] = "dwarf-with-dsym"
del app_release_settings["ENABLE_PREVIEWS"]

app_debug_cfg, app_debug_text = build_config(app_debug_settings, "Debug")
objects.append((app_debug_cfg, app_debug_text))
app_release_cfg, app_release_text = build_config(app_release_settings, "Release")
objects.append((app_release_cfg, app_release_text))

app_config_list, app_config_list_text = config_list(app_debug_cfg, app_release_cfg)
objects.append((app_config_list, app_config_list_text))

# Widget debug/release
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
    "SWIFT_COMPILATION_MODE": "wholemodule",
}

widget_release_settings = dict(widget_debug_settings)
widget_release_settings["DEBUG_INFORMATION_FORMAT"] = "dwarf-with-dsym"

widget_debug_cfg, widget_debug_text = build_config(widget_debug_settings, "Debug")
objects.append((widget_debug_cfg, widget_debug_text))
widget_release_cfg, widget_release_text = build_config(widget_release_settings, "Release")
objects.append((widget_release_cfg, widget_release_text))

widget_config_list, widget_config_list_text = config_list(widget_debug_cfg, widget_release_cfg)
objects.append((widget_config_list, widget_config_list_text))

# Project-level debug/release configs
proj_debug_settings = {
    "ALWAYS_SEARCH_USER_PATHS": "NO",
    "CLANG_ANALYZER_NONNULL": "YES",
    "CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION": "YES_AGGRESSIVE",
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

proj_debug_cfg, proj_debug_text = build_config(proj_debug_settings, "Debug")
objects.append((proj_debug_cfg, proj_debug_text))
proj_release_cfg, proj_release_text = build_config(proj_release_settings, "Release")
objects.append((proj_release_cfg, proj_release_text))

proj_config_list, proj_config_list_text = config_list(proj_debug_cfg, proj_release_cfg)
objects.append((proj_config_list, proj_config_list_text))

# Targets
# CallMe app target
app_target_dep = None
widget_proxy = None
widget_target_dep = None

widget_target = uid()
objects.append((widget_target,
    f"\t{widget_target} = {{\n"
    f"\t\tisa = PBXNativeTarget;\n"
    f"\t\tbuildConfigurationList = {widget_config_list};\n"
    f"\t\tbuildPhases = ({widget_sources_phase}, {widget_frameworks_phase}, {widget_resources_phase});\n"
    f"\t\tbuildRules = ();\n"
    f"\t\tdependencies = ();\n"
    f"\t\tname = CallMeWidget;\n"
    f"\t\tproductName = CallMeWidget;\n"
    f"\t\tproductReference = {widget_product_ref};\n"
    f"\t\tproductType = com.apple.product-type.app-extension;\n"
    f"\t}};"))

widget_proxy_id = uid()
objects.append((widget_proxy_id,
    f"\t{widget_proxy_id} = {{\n"
    f"\t\tisa = PBXContainerItemProxy;\n"
    f"\t\tcontainerPortal = {project_group};\n"
    f"\t\tproxyType = 1;\n"
    f"\t\tremoteGlobalID = {widget_target};\n"
    f"\t\tremoteInfo = CallMeWidget;\n"
    f"\t}};"))

app_target_dep_id = uid()
objects.append((app_target_dep_id,
    f"\t{app_target_dep_id} = {{\n"
    f"\t\tisa = PBXTargetDependency;\n"
    f"\t\ttarget = {widget_target};\n"
    f"\t\ttargetProxy = {widget_proxy_id};\n"
    f"\t}};"))

callme_target = uid()
objects.append((callme_target,
    f"\t{callme_target} = {{\n"
    f"\t\tisa = PBXNativeTarget;\n"
    f"\t\tbuildConfigurationList = {app_config_list};\n"
    f"\t\tbuildPhases = ({app_sources_phase}, {app_frameworks_phase}, {app_resources_phase});\n"
    f"\t\tbuildRules = ();\n"
    f"\t\tdependencies = ({app_target_dep_id});\n"
    f"\t\tname = CallMe;\n"
    f"\t\tproductName = CallMe;\n"
    f"\t\tproductReference = {callme_product_ref};\n"
    f"\t\tproductType = com.apple.product-type.application;\n"
    f"\t}};"))

# Project object
objects.insert(0, (project_group,
    f"\t{project_group} = {{\n"
    f"\t\tisa = PBXProject;\n"
    f"\t\tbuildConfigurationList = {proj_config_list};\n"
    f"\t\tbuildStyles = ();\n"
    f"\t\tbuildTypes = ();\n"
    f"\t\tcolumnBreaks = ();\n"
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
    f"\t}};"))

# ── write pbxproj ──────────────────────────────────────────────────────────
XCODEDIR.mkdir(parents=True, exist_ok=True)
WORKSPACE.mkdir(parents=True, exist_ok=True)

content = ["// !$*UTF8*$!", ""]
for _, txt in objects:
    content.append(txt)
content.append("")

PBXPROJ.write_text("\n".join(content))

# Workspace contents
xcworkspace_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Workspace version="1.0">\n'
    '   <FileRef location="self:CallMe.xcodeproj">\n'
    '   </FileRef>\n'
    '</Workspace>\n'
)
(WORKSPACE / "contents.xcworkspacedata").write_text(xcworkspace_xml)

print(f"✓ Generated {PBXPROJ}")
print(f"✓ Generated {WORKSPACE / 'contents.xcworkspacedata'}")
print(f"  App target: CallMe  ({len(app_files)} Swift files + resources)")
print(f"  Widget: CallMeWidget ({len(widget_files)} Swift files)")
