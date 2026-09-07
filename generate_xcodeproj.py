#!/usr/bin/env python3
"""
Generate CallMe Xcode project manually (cross-platform, no XcodeGen needed).
Creates the .xcodeproj directory with project.pbxproj and supporting files.
"""
import os, shutil, uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
XCODEPATH = os.path.join(ROOT, "CallMe.xcodeproj")
SRCROOT = ROOT  # sources are alongside .xcodeproj

# UUID helper
def uid():
    return str(uuid.uuid4()).upper()

# Build the pbxproj content
pbxproj = []
pbxproj.append("// !$*UTF8*$!")
pbxproj.append("")

# Groups
main_group = uid()
callme_group = uid()
widget_group = uid()
audio_group = uid()
entitlements_group = uid()
plist_group = uid()

pbxproj.append(f"rootObject = {main_group};")
pbxproj.append(f"objectVersion = 56;")
pbxproj.append(f"archiveVersion = 1;")
pbxproj.append(f"classes = {{}};")

# Group tree
groups = {
    main_group: {
        "isa": "PBXProject",
        "buildStyleRefs": "{}",
        "buildTypes": "(\n\t\t\t089C16991A0A492800E8C499 /* Debug */,\n\t\t\t089C169A1A0A492800E8C499 /* Release */\n\t\t)",
        "columnBreaks": "(\n\t\t\t089C169B1A0A492800E8C499 /* Debug */,\n\t\t\t089C169C1A0A492800E8C499 /* Release */\n\t\t)",
        "defaultConfigurationIsVisible": "0",
        "defaultConfigurationName": "Debug",
        "developmentTeam": "",
        "hasRunOnce": "0",
        "isDocumentTypeDocument": "NO",
        "knownRegions": "(\n\t\ten\n\t)",
        "mainGroup": main_group,
        "productModuleName": "CallMe",
        "projectDirPath": "",
        "projectEntity": "",
        "projectRoot": "$SRCROOT",
        "targets": f"({callme_group}, {widget_group})",
        "sourceTree": "<group>",
        "versionGroupPosition": "0",
    }
}

# Add groups
groups[main_group]["children"] = f"({callme_group}, {widget_group}, {plist_group}, {entitlements_group}, {audio_group})"

# Regular groups
groups[callme_group] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "name": "CallMe",
    "path": "CallMe",
    "children": f"({plist_group}, {entitlements_group}, {audio_group})",
}

groups[widget_group] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "name": "CallMeWidget",
    "path": "CallMeWidget",
    "children": "(\n\t\t\t" + uid() + " /* CallMeWidgetIntentsPlaceholder.swift */\n\t\t)",
}

wplaceholder_file = uid()
groups[widget_group]["children"] = f"({wplaceholder_file})"

groups[plist_group] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "name": "Supporting Files",
    "path": "CallMe",
    "children": "(\n\t\t\t" + uid() + " /* Info.plist */\n\t\t)",
}

info_plist_file = uid()
# Need to also have CallMeWidget/Info.plist — add separately
widget_plist_group = uid()
groups[widget_plist_group] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "name": "Supporting Files",
    "path": "CallMeWidget",
    "children": "(\n\t\t\t" + uid() + " /* Info.plist */\n\t\t)",
}
# Actually, include both plists under main group for simplicity
groups[plist_group]["children"] = f"({info_plist_file}, {uid()})"  # add widget plist placeholder

# Let me restructure more cleanly
# Main group children: CallMe folder, CallMeWidget folder, both plists

widget_info_plist_file = uid()

# Rebuild groups cleanly
groups = {}

main = uid()
callme = uid()
widget = uid()
support = uid()
support_w = uid()
audio = uid()
ent = uid()

groups[main] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": f"({callme}, {widget}, {support}, {support_w}, {audio}, {ent})",
    "name": "CallMe",
    "path": "CallMe",
}

# Fix: callme and widget are groups pointing to subdirectories
groups[callme] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": f"({support}, {audio}, {ent})",
    "name": "CallMe",
    "path": "CallMe",
}

groups[widget] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": "()",
    "name": "CallMeWidget",
    "path": "CallMeWidget",
}

groups[support] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": f"({info_plist_file})",
    "name": "Supporting Files",
    "path": "CallMe",
}

groups[support_w] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": f"({widget_info_plist_file})",
    "name": "Supporting Files",
    "path": "CallMeWidget",
}

groups[audio] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": f"({audio_file})",
    "name": "Audio",
    "path": "CallMe",
}

groups[ent] = {
    "isa": "PBXGroup",
    "sourceTree": "<group>",
    "children": f"({ent_file})",
    "name": "Supporting Files",
    "path": "CallMe",
}

# Source files
app_files = [
    "CallMeApp.swift",
    "ContentView.swift",
    "CallMeAlarmMetadata.swift",
    "AnswerCallIntent.swift",
    "AudioPlayer.swift",
    "AlarmScheduler.swift",
]

widget_files = [
    "CallMeWidget.swift",
    "CallMeWidgetIntentPlaceholder.swift",
]

# Build file UUIDs
build_files = {}
for f in app_files:
    build_files[f] = uid()
for f in widget_files:
    build_files[f] = uid()

info_plist_build = uid()
widget_info_plist_build = uid()
ent_build = uid()
audio_build = uid()

# Widget placeholder file reference
wp_build = uid()

# Now build the pbxproj content properly
lines = []
lines.append("// !$*UTF8*$!")
lines.append("")

# We need to collect all objects
objects = {}  # uuid -> dict

# Groups
for gid, gdata in groups.items():
    obj = {"isa": "PBXGroup", "sourceTree": "<group>"}
    if "name" in gdata:
        obj["name"] = gdata["name"]
    if "path" in gdata:
        obj["path"] = gdata["path"]
    if "children" in gdata:
        obj["children"] = gdata["children"]
    objects[gid] = obj

# Files (source code)
file_refs = {}
for fname, bfid in build_files.items():
    dirpath = "CallMe" if fname in app_files else "CallMeWidget"
    refid = uid()
    objects[refid] = {
        "isa": "PBXFileReference",
        "lastKnownFileType": "sourcecode.swift",
        "path": os.path.join(dirpath, fname),
        "sourceTree": "SOURCE_ROOT",
    }
    file_refs[fname] = refid

# Info.plist file refs
objects[info_plist_file] = {
    "isa": "PBXFileReference",
    "lastKnownFileType": "text.plist.xml",
    "path": "CallMe/Info.plist",
    "sourceTree": "SOURCE_ROOT",
}
objects[widget_info_plist_file] = {
    "isa": "PBXFileReference",
    "lastKnownFileType": "text.plist.xml",
    "path": "CallMeWidget/Info.plist",
    "sourceTree": "SOURCE_ROOT",
}

# Entitlements
objects[ent_file] = {
    "isa": "PBXFileReference",
    "lastKnownFileType": "text.plist.entitlements",
    "path": "CallMe/CallMe.entitlements",
    "sourceTree": "SOURCE_ROOT",
}

# Audio file
audio_file = uid()
objects[audio_file] = {
    "isa": "PBXFileReference",
    "lastKnownFileType": "audio.wav",
    "path": "CallMe/test-message.wav",
    "sourceTree": "SOURCE_ROOT",
}

# Update group children to include actual file references
groups[callme]["children"] = f"({support}, {audio}, {ent})"
groups[support]["children"] = f"({info_plist_file})"
groups[support_w]["children"] = f"({widget_info_plist_file})"
groups[audio]["children"] = f"({audio_file})"
groups[ent]["children"] = f"({ent_file})"

# Now create the actual PBXGroup objects with children
for gid in groups:
    g = groups[gid]
    obj = {"isa": "PBXGroup", "sourceTree": "<group>"}
    if "name" in g:
        obj["name"] = g["name"]
    if "path" in g:
        obj["path"] = g["path"]
    if "children" in g:
        obj["children"] = g["children"]
    objects[gid] = obj

# Build files
build_files_dict = {}
for fname, bfid in build_files.items():
    refid = file_refs[fname]
    settings = "{}"
    bf_obj = {
        "isa": "PBXBuildFile",
        "fileRef": refid,
        "settings": settings,
    }
    objects[bfid] = bf_obj
    build_files_dict[fname] = bfid

# Info.plist build file
info_plist_bf = uid()
objects[info_plist_bf] = {
    "isa": "PBXBuildFile",
    "fileRef": info_plist_file,
    "settings": "{}",
}
objects[widget_info_plist_bf] = {
    "isa": "PBXBuildFile",
    "fileRef": widget_info_plist_file,
    "settings": "{}",
}
objects[ent_bf] = {
    "isa": "PBXBuildFile",
    "fileRef": ent_file,
    "settings": "{}",
}
objects[audio_bf] = {
    "isa": "PBXBuildFile",
    "fileRef": audio_file,
    "settings": "{}",
}

# PBXSourcesBuildPhase
callme_sources = uid()
objects[callme_sources] = {
    "isa": "PBXSourcesBuildPhase",
    "buildActionMask": "2147483647",
    "files": f"({', '.join(build_files[f] for f in app_files)}, {info_plist_bf}, {ent_bf})",
    "runOnlyWhenInstalling": "NO",
    "sourceBuildPhase": "YES",
    "files": f"({', '.join(build_files[f] for f in app_files)})",
}

widget_sources = uid()
objects[widget_sources] = {
    "isa": "PBXSourcesBuildPhase",
    "buildActionMask": "2147483647",
    "files": f"({wp_build})",
    "runOnlyWhenInstalling": "NO",
    "sourceBuildPhase": "YES",
}

# Fix: rebuild files list properly
callme_source_files_list = ", ".join(build_files[f] for f in app_files)
objects[callme_sources]["files"] = f"({callme_source_files_list})"

widget_source_files_list = f"({wp_build})"
objects[widget_sources]["files"] = widget_source_files_list

# PBXFrameworksBuildPhase (empty for both, since AlarmKit etc are system frameworks)
callme_frameworks = uid()
objects[callme_frameworks] = {
    "isa": "PBXFrameworksBuildPhase",
    "buildActionMask": "2147483647",
    "files": "()",
    "runOnlyWhenInstalling": "NO",
}
widget_frameworks = uid()
objects[widget_frameworks] = {
    "isa": "PBXFrameworksBuildPhase",
    "buildActionMask": "2147483647",
    "files": "()",
    "runOnlyWhenInstalling": "NO",
}

# PBXResourcesBuildPhase
callme_resources = uid()
objects[callme_resources] = {
    "isa": "PBXResourcesBuildPhase",
    "buildActionMask": "2147483647",
    "files": f"({audio_bf})",
    "runOnlyWhenInstalling": "NO",
}
widget_resources = uid()
objects[widget_resources] = {
    "isa": "PBXResourcesBuildPhase",
    "buildActionMask": "2147483647",
    "files": "()",
    "runOnlyWhenInstalling": "NO",
}

# Product file references
callme_product_file = uid()
objects[callme_product_file] = {
    "isa": "PBXFileReference",
    "explicitFileType": "wrapper.application",
    "includeInIndex": "0",
    "path": "CallMe.app",
    "sourceTree": "BUILT_PRODUCTS_DIR",
}

widget_product_file = uid()
objects[widget_product_file] = {
    "isa": "PBXFileReference",
    "explicitFileType": "wrapper.app-extension",
    "includeInIndex": "0",
    "path": "CallMeWidget.appex",
    "sourceTree": "BUILT_PRODUCTS_DIR",
}

# PBXNativeTarget for CallMe app
callme_target = uid()
objects[callme_target] = {
    "isa": "PBXNativeTarget",
    "buildConfigurationList": f"{uid()}",  # will fix later
    "buildPhases": f"({callme_sources}, {callme_frameworks}, {callme_resources})",
    "buildRules": "()",
    "dependencies": f"({uid()})",  # dependency on widget
    "name": "CallMe",
    "productName": "CallMe",
    "productReference": callme_product_file,
    "productType": "com.apple.product-type.application",
}

widget_target = uid()
objects[widget_target] = {
    "isa": "PBXNativeTarget",
    "buildConfigurationList": f"{uid()}",
    "buildPhases": f"({widget_sources}, {widget_frameworks}, {widget_resources})",
    "buildRules": "()",
    "dependencies": "()",
    "name": "CallMeWidget",
    "productName": "CallMeWidget",
    "productReference": widget_product_file,
    "productType": "com.apple.product-type.app-extension",
}

# Fix build config lists
callme_config_list = uid()
objects[callme_config_list] = {
    "isa": "XCConfigurationList",
    "buildConfigurations": f"({uid()}, {uid()})",  # debug, release
    "defaultConfigurationName": "Debug",
}
widget_config_list = uid()
objects[widget_config_list] = {
    "isa": "XCConfigurationList",
    "buildConfigurations": f"({uid()}, {uid()})",
    "defaultConfigurationName": "Debug",
}

# Fix target references
objects[callme_target]["buildConfigurationList"] = callme_config_list
objects[widget_target]["buildConfigurationList"] = widget_config_list

# Dependency: app depends on widget
app_widget_dep = uid()
objects[app_widget_dep] = {
    "isa": "PBXTargetDependency",
    "target": widget_target,
    "targetProxy": f"{uid()}",  # PBXContainerItemProxy
}
objects[uid()]  # placeholder proxy

# Actually create the proxy
proxy = uid()
objects[proxy] = {
    "isa": "PBXContainerItemProxy",
    "containerPortal": main,
    "proxyType": "1",
    "remoteGlobalID": widget_target,
    "remoteInfo": "CallMeWidget",
}
objects[app_widget_dep]["targetProxy"] = proxy

# Fix dependency lists
objects[callme_target]["dependencies"] = f"({app_widget_dep})"

# Build configurations (debug/release)
debug_config = uid()
release_config = uid()
objects[debug_config] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": {
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
        "OTHER_LDFLAGS": "-framework AlarmKit -framework AppIntents -framework WidgetKit -framework ActivityKit -framework AVFoundation",
    },
    "name": "Debug",
}

release_config_obj = uid()
objects[release_config_obj] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": {
        "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
        "ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME": "AccentColor",
        "CODE_SIGN_IDENTITY": "",
        "CODE_SIGN_STYLE": "Automatic",
        "CURRENT_PROJECT_VERSION": "1",
        "DEVELOPMENT_TEAM": "",
        "INFOPLIST_FILE": "CallMe/Info.plist",
        "MARKETING_VERSION": "1.0.0",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.callme.app",
        "SWIFT_VERSION": "5.0",
        "TARGETED_DEVICE_FAMILY": "1",
        "SDKROOT": "iphoneos",
        "CODE_SIGN_ENTITLEMENTS": "CallMe/CallMe.entitlements",
        "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks",
        "OTHER_LDFLAGS": "-framework AlarmKit -framework AppIntents -framework WidgetKit -framework ActivityKit -framework AVFoundation",
    },
    "name": "Release",
}

objects[callme_config_list]["buildConfigurations"] = f"({debug_config}, {release_config_obj})"

# Widget debug/release configs
widget_debug = uid()
widget_release = uid()
objects[widget_debug] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": {
        "SKIP_INSTALL": "YES",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.callme.app.widget",
        "TARGETED_DEVICE_FAMILY": "1",
        "SDKROOT": "iphoneos",
        "SWIFT_VERSION": "5.0",
        "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks @executable_path/../../Frameworks",
        "INFOPLIST_FILE": "CallMeWidget/Info.plist",
    },
    "name": "Debug",
}
objects[widget_release] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": {
        "SKIP_INSTALL": "YES",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.callme.app.widget",
        "TARGETED_DEVICE_FAMILY": "1",
        "SDKROOT": "iphoneos",
        "SWIFT_VERSION": "5.0",
        "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks @executable_path/../../Frameworks",
        "INFOPLIST_FILE": "CallMeWidget/Info.plist",
    },
    "name": "Release",
}
objects[widget_config_list]["buildConfigurations"] = f"({widget_debug}, {widget_release})"

# PBXProject config
project_debug = uid()
project_release = uid()
objects[project_debug] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": {
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
        "CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER": "YES",
        "CMAKE_COMMAND": "cmake",
        "COPY_PHASE_STRIP": "NO",
        "DEBUG_INFORMATION_FORMAT": "dwarf-with-dsym",
        "ENABLE_STRICT_OBJC_MSGSEND": "YES",
        "ENABLE_TESTABILITY": "YES",
        "GCC_OPTIMIZATION_LEVEL": "0",
        "GCC_PREPROCESSOR_DEFINITIONS": "DEBUG=1 $(inherited)",
        "GCC_SYMBOLS_PRIVATE_EXTERN": "NO",
        "GCC_WARN_ABOUT_RETURN_TYPE": "YES_ERROR",
        "GCC_WARN_UNINITIALIZED_AUTOS": "YES_AGGRESSIVE",
        "GCC_WARN_UNUSED_FUNCTION": "YES",
        "GCC_WARN_UNUSED_VARIABLE": "YES",
        "IPHONEOS_DEPLOYMENT_TARGET": "26.0",
        "MTL_ENABLE_DEBUG_INFO": "INCLUDE_SOURCE",
        "ONLY_ACTIVE_ARCH": "YES",
        "SDKROOT": "iphoneos",
        "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG",
        "SWIFT_OPTIMIZATION_LEVEL": "-Onone",
    },
    "name": "Debug",
}
objects[project_release] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": {
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
        "ENABLE_NS_PRAGMA": "YES",
        "ENABLE_STRICT_OBJC_MSGSEND": "YES",
        "GCC_CODE_SIGNING_IDENTITY": "",
        "GCC_PRECOMPILE_PREFIX_HEADER": "NO",
        "GCC_PREFIX_HEADER": "",
        "IPHONEOS_DEPLOYMENT_TARGET": "26.0",
        "MTL_ENABLE_DEBUG_INFO": "NO",
        "SDKROOT": "iphoneos",
        "SWIFT_OPTIMIZATION_LEVEL": "-O",
    },
    "name": "Release",
}
objects[main]["buildConfigurationList"] = f"({project_debug}, {project_release})"

# Build content.out
out_lines = []
out_lines.append("// !$*UTF8*$!")
out_lines.append("")

# Helper to format object
def format_obj(obj):
    lines = [f"\t{objid} = {{"]
    lines.append(f"\t\tisa = {obj['isa']};")
    for key, val in obj.items():
        if key == "isa":
            continue
        if isinstance(val, str) and val.startswith("(") and val.endswith(")"):
            lines.append(f"\t\t{key} = {val};")
        elif isinstance(val, str):
            lines.append(f"\t\t{key} = {val};")
        elif isinstance(val, dict):
            # Build settings
            settings = "{" + " ".join(f"{k} = {v};" for k, v in val.items()) + "}"
            lines.append(f"\t\t{key} = {settings};")
    lines.append("\t};")
    return "\n".join(lines)

# Build the content
for objid, obj in objects.items():
    out_lines.append(format_obj(obj))

# Now write the pbxproj
os.makedirs(XCODEPATH, exist_ok=True)
os.makedirs(os.path.join(XCODEPATH, "project.xcworkspace"), exist_ok=True)

with open(os.path.join(XCODEPATH, "project.pbxproj"), "w") as f:
    f.write("\n".join(out_lines))

# Write workspace contents
with open(os.path.join(XCODEPATH, "project.xcworkspace", "contents.xcworkspacedata"), "w") as f:
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:CallMe.xcodeproj">
   </FileRef>
</Workspace>''')

print(f"Generated {XCODEPATH}/project.pbxproj")
print(f"Generated {XCODEPATH}/project.xcworkspace/contents.xcworkspacedata")
