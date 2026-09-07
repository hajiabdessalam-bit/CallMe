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

# ── helpers ─────────────────────────────────────────────────────────────────
def file_ref(name, path, type_hint="sourcecode.swift"):
    ref = uid()
    return (
        f"\t{ref} = {{\n"
        f"\t\tisa = PBXFileReference;\n"
        f"\t\tlastKnownFileType = {type_hint};\n"
        f"\t\tpath = {path};\n"
        f"\t\tsourceTree = SOURCE_ROOT;\n"
        f"\t}};",
        ref,
    )
    ref
        ref,
    )

def source_build_file(fref, settings=""):
    bf = uid()
    s = f"\n\t\tsettings = {settings};" if settings else ""
    return (bf,
        f"\t{bf} = {{\n"
        f"\t\tisa = PBXBuildFile;\n"
        f"\t\tfileRef = {fref};{s}\n"
        f"\t}};",
        bf,
    )

def group_obj(name, path, children=None):
    g = uid()
    children_str = f"({children})" if children else "()"
    return (g,
        f"\t{g} = {{\n"
        f"\t\tisa = PBXGroup;\n"
        f"\t\tname = {name};\n"
        f"\t\tpath = {path};\n"
        f"\t\tchildren = {children_str};\n"
        f"\t\tsourceTree = <group>;\n"
        f"\t}};",
        g,
    )

def config_list_obj(debug_cfg, release_cfg):
    cl = uid()
    return (cl,
        f"\t{cl} = {{\n"
        f"\t\tisa = XCConfigurationList;\n"
        f"\t\tbuildConfigurations = ({debug_cfg}, {release_cfg});\n"
        f"\t\tdefaultConfigurationName = Debug;\n"
        f"\t}};",
        cl,
    )

def build_config_obj(settings_dict, name):
    cfg = uid()
    settings = " ".join(f"{k} = {v};" for k, v in settings_dict.items())
    return (cfg,
        f"\t{cfg} = {{\n"
        f"\t\tisa = XCBuildConfiguration;\n"
        f"\t\tbuildSettings = {{{settings}}}\n"
        f"\t\tname = {name};\n"
        f"\t}};",
        cfg,
    )

# ── locate pre-written files ────────────────────────────────────────────────
callme_swift_names = [
    "CallMeApp.swift",
    "ContentView.swift",
    "CallMeAlarmMetadata.swift",
    "AnswerCallIntent.swift",
    "AudioPlayer.swift",
    "AlarmScheduler.swift",
]
widget_swift_names = [
    "CallMeWidget.swift",
    "CallMeWidgetIntentPlaceholder.swift",
]

app_swift_refs = []
for name in callme_swift_names:
    p = ROOT / "CallMe" / name
    if not p.is_file():
        print(f"  [!] Missing: {p}")
        continue
    ref, _ = file_ref(name, f"CallMe/{name}", "sourcecode.swift")
    app_swift_refs.append(ref)

widget_swift_refs = []
for name in widget_swift_names:
    p = ROOT / "CallMeWidget" / name
    if not p.is_file():
        print(f"  [!] Missing: {p}")
        continue
    ref, _ = file_ref(name, f"CallMeWidget/{name}", "sourcecode.swift")
    widget_swift_refs.append(ref)

# Info.plist, entitlements, audio
plist_app_ref, _ = file_ref("Info.plist", "CallMe/Info.plist", "text.plist.xml")
plist_widget_ref, _ = file_ref("Info.plist", "CallMeWidget/Info.plist", "text.plist.xml")
ent_ref, _ = file_ref("CallMe.entitlements", "CallMe/CallMe.entitlements", "text.plist.entitlements")
audio_ref, _ = file_ref("test-message.wav", "CallMe/test-message.wav", "audio.wav")

# Build files
app_swift_bf = []
for ref in app_swift_refs:
    bf, _ = source_build_file(ref)
    app_swift_bf.append(bf)

widget_swift_bf = []
for ref in widget_swift_refs:
    bf, _ = source_build_file(ref)
    widget_swift_bf.append(bf)

bf_plist_app, _ = source_build_file(plist_app_ref)
bf_plist_widget, _ = source_build_file(plist_widget_ref)
bf_ent, _ = source_build_file(ent_ref)
bf_audio, _ = source_build_file(audio_ref)

# Build phases
app_src_phase, app_src_phase_uid = None, uid()
objects_src = []

def pbx(obj_type, uid_val, lines):
    txt = f"\t{uid_val} = {{\n" \
          f"\t\tisa = {obj_type};\n" \
          + "".join(lines) + \
          f"\t}};"
    return (uid_val, txt)

# We'll collect (uuid, text) pairs
all_objects = []

def add(uuid_val, text):
    all_objects.append((uuid_val, text))

def add_obj(uuid_val, isa, **kwargs):
    lines = []
    for key, val in kwargs.items():
        if isinstance(val, list):
            val = "(" + ", ".join(val) + ")"
        lines.append(f"\t\t{key} = {val};")
    txt = f"\t{uuid_val} = {{\n" \
          f"\t\tisa = {isa};\n" + \
          "".join(lines) + \
          f"\t}};"
    all_objects.append((uuid_val, txt))

# ── Build all objects ────────────────────────────────────────────────────────

# File references
add(plist_app_ref, "", )
add_plist_app = all_objects[-1][1]
all_objects[-1] = (plist_app_ref, 
    f"\t{plist_app_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\tlastKnownFileType = text.plist.xml;\n"
    f"\t\tpath = CallMe/Info.plist;\n"
    f"\t\tsourceTree = SOURCE_ROOT;\n"
    f"\t}};")

add(plist_widget_ref, "")
all_objects[-1] = (plist_widget_ref,
    f"\t{plist_widget_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\tlastKnownFileType = text.plist.xml;\n"
    f"\t\tpath = CallMeWidget/Info.plist;\n"
    f"\t\tsourceTree = SOURCE_ROOT;\n"
    f"\t}};")

add(ent_ref, "")
all_objects[-1] = (ent_ref,
    f"\t{ent_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\tlastKnownFileType = text.plist.entitlements;\n"
    f"\t\tpath = CallMe/CallMe.entitlements;\n"
    f"\t\tsourceTree = SOURCE_ROOT;\n"
    f"\t}};")

add(audio_ref, "")
all_objects[-1] = (audio_ref,
    f"\t{audio_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\tlastKnownFileType = audio.wav;\n"
    f"\t\tpath = CallMe/test-message.wav;\n"
    f"\t\tsourceTree = SOURCE_ROOT;\n"
    f"\t}};")

for name, ref in zip(callme_swift_names, app_swift_refs):
    add(ref, "")
    all_objects[-1] = (ref,
        f"\t{ref} = {{\n"
        f"\t\tisa = PBXFileReference;\n"
        f"\t\tlastKnownFileType = sourcecode.swift;\n"
        f"\t\tpath = CallMe/{name};\n"
        f"\t\tsourceTree = SOURCE_ROOT;\n"
        f"\t}};")
for name, ref in zip(widget_swift_names, widget_swift_refs):
    add(ref, "")
    all_objects[-1] = (ref,
        f"\t{ref} = {{\n"
        f"\t\tisa = PBXFileReference;\n"
        f"\t\tlastKnownFileType = sourcecode.swift;\n"
        f"\t\tpath = CallMeWidget/{name};\n"
        f"\t\tsourceTree = SOURCE_ROOT;\n"
        f"\t}};")

# Build files (app)
for ref in app_swift_refs:
    bf = uid()
    add(bf, "")
    all_objects[-1] = (bf,
        f"\t{bf} = {{\n"
        f"\t\tisa = PBXBuildFile;\n"
        f"\t\tfileRef = {ref};\n"
        f"\t}};")
    app_swift_bf.append(bf)

for ref in widget_swift_refs:
    bf = uid()
    add(bf, "")
    all_objects[-1] = (bf,
        f"\t{bf} = {{\n"
        f"\t\tisa = PBXBuildFile;\n"
        f"\t\tfileRef = {ref};\n"
        f"\t}};")
    widget_swift_bf.append(bf)

add(bf_plist_app, "")
all_objects[-1] = (bf_plist_app,
    f"\t{bf_plist_app} = {{\n"
    f"\t\tisa = PBXBuildFile;\n"
    f"\t\tfileRef = {plist_app_ref};\n"
    f"\t}};")

add(bf_plist_widget, "")
all_objects[-1] = (bf_plist_widget,
    f"\t{bf_plist_widget} = {{\n"
    f"\t\tisa = PBXBuildFile;\n"
    f"\t\tfileRef = {plist_widget_ref};\n"
    f"\t}};")

add(bf_ent, "")
all_objects[-1] = (bf_ent,
    f"\t{bf_ent} = {{\n"
    f"\t\tisa = PBXBuildFile;\n"
    f"\t\tfileRef = {ent_ref};\n"
    f"\t}};")

add(bf_audio, "")
all_objects[-1] = (bf_audio,
    f"\t{bf_audio} = {{\n"
    f"\t\tisa = PBXBuildFile;\n"
    f"\t\tfileRef = {audio_ref};\n"
    f"\t}};")

# Build phases: CallMe app
add(app_src_phase_uid, "")
src_list = ", ".join(app_swift_bf)
all_objects[-1] = (app_src_phase_uid,
    f"\t{app_src_phase_uid} = {{\n"
    f"\t\tisa = PBXSourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({src_list});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t\tsourceBuildPhase = YES;\n"
    f"\t}};")

app_fw_phase = uid()
add(app_fw_phase, "")
all_objects[-1] = (app_fw_phase,
    f"\t{app_fw_phase} = {{\n"
    f"\t\tisa = PBXFrameworksBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ();\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};")

app_res_phase = uid()
add(app_res_phase, "")
all_objects[-1] = (app_res_phase,
    f"\t{app_res_phase} = {{\n"
    f"\t\tisa = PBXResourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({bf_audio});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};")

# Build phases: Widget extension
widget_src_phase = uid()
add(widget_src_phase, "")
widget_src_list = ", ".join(widget_swift_bf) + f", {bf_plist_widget}"
all_objects[-1] = (widget_src_phase,
    f"\t{widget_src_phase} = {{\n"
    f"\t\tisa = PBXSourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({widget_src_list});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t\tsourceBuildPhase = YES;\n"
    f"\t}};")
# Add plist build file to widget sources too
widget_src_list = ", ".join(widget_swift_bf) + f", {bf_plist_widget}"
all_objects[-1] = (widget_src_phase,
    f"\t{widget_src_phase} = {{\n"
    f"\t\tisa = PBXSourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ({widget_src_list});\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t\tsourceBuildPhase = YES;\n"
    f"\t}};")

widget_fw_phase = uid()
add(widget_fw_phase, "")
all_objects[-1] = (widget_fw_phase,
    f"\t{widget_fw_phase} = {{\n"
    f"\t\tisa = PBXFrameworksBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ();\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};")

widget_res_phase = uid()
add(widget_res_phase, "")
all_objects[-1] = (widget_res_phase,
    f"\t{widget_res_phase} = {{\n"
    f"\t\tisa = PBXResourcesBuildPhase;\n"
    f"\t\tbuildActionMask = 2147483647;\n"
    f"\t\tfiles = ();\n"
    f"\t\trunOnlyWhenInstalling = NO;\n"
    f"\t}};")

# Product references
callme_app_ref = uid()
add(callme_app_ref, "")
all_objects[-1] = (callme_app_ref,
    f"\t{callme_app_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\texplicitFileType = wrapper.application;\n"
    f"\t\tincludeInIndex = 0;\n"
    f"\t\tpath = CallMe.app;\n"
    f"\t\tsourceTree = BUILT_PRODUCTS_DIR;\n"
    f"\t}};")

widget_appex_ref = uid()
add(widget_appex_ref, "")
all_objects[-1] = (widget_appex_ref,
    f"\t{widget_appex_ref} = {{\n"
    f"\t\tisa = PBXFileReference;\n"
    f"\t\texplicitFileType = wrapper.app-extension;\n"
    f"\t\tincludeInIndex = 0;\n"
    f"\t\tpath = CallMeWidget.appex;\n"
    f"\t\tsourceTree = BUILT_PRODUCTS_DIR;\n"
    f"\t}};")

# Groups
project_group = uid()
add_args = [
    (plist_app_ref, plist_widget_ref, ent_ref, audio_ref,
     callme_app_ref, widget_appex_ref)
]
proj_children = ", ".join(str(x) for x in add_args[0])
add(project_group, "")
all_objects[-1] = (project_group,
    f"\t{project_group} = {{\n"
    f"\t\tisa = PBXGroup;\n"
    f"\t\tchildren = ({proj_children});\n"
    f"\t\tname = CallMe;\n"
    f"\t\tsourceTree = <group>;\n"
    f"\t}};")

callme_group = uid()
add(callme_group, "")
all_objects[-1] = (callme_group,
    f"\t{callme_group} = {{\n"
    f"\t\tisa = PBXGroup;\n"
    f"\t\tname = CallMe;\n"
    f"\t\tpath = CallMe;\n"
    f"\t\tchildren = ({plist_app_ref}, {ent_ref}, {audio_ref});\n"
    f"\t\tsourceTree = <group>;\n"
    f"\t}};")

widget_group = uid()
add(widget_group, "")
all_objects[-1] = (widget_group,
    f"\t{widget_group} = {{\n"
    f"\t\tisa = PBXGroup;\n"
    f"\t\tname = CallMeWidget;\n"
    f"\t\tpath = CallMeWidget;\n"
    f"\t\tchildren = ({plist_widget_ref});\n"
    f"\t\tsourceTree = <group>;\n"
    f"\t}};")

# Build configurations — App
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

app_debug_cfg = uid()
add(app_debug_cfg, "")
all_objects[-1] = (app_debug_cfg,
    f"\t{app_debug_cfg} = {{\n"
    f"\t\tisa = XCBuildConfiguration;\n"
    f"\t\tbuildSettings = {{{' '.join(f'{k} = {v};' for k,v in app_debug_settings.items())}}}\n"
    f"\t\tname = Debug;\n"
    f"\t}};")

app_release_cfg = uid()
add(app_release_cfg, "")
all_objects[-1] = (app_release_cfg,
    f"\t{app_release_cfg} = {{\n"
    f"\t\tisa = XCBuildConfiguration;\n"
    f"\t\tbuildSettings = {{{' '.join(f'{k} = {v};' for k,v in app_release_settings.items())}}}\n"
    f"\t\tname = Release;\n"
    f"\t}};")

app_cfg_list = uid()
add(app_cfg_list, "")
all_objects[-1] = (app_cfg_list,
    f"\t{app_cfg_list} = {{\n"
    f"\t\tisa = XCConfigurationList;\n"
    f"\t\tbuildConfigurations = ({app_debug_cfg}, {app_release_cfg});\n"
    f"\t\tdefaultConfigurationName = Debug;\n"
    f"\t}};")

# Build configurations — Widget
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

widget_debug_cfg = uid()
add(widget_debug_cfg, "")
all_objects[-1] = (widget_debug_cfg,
    f"\t{widget_debug_cfg} = {{\n"
    f"\t\tisa = XCBuildConfiguration;\n"
    f"\t\tbuildSettings = {{{' '.join(f'{k} = {v};' for k,v in widget_debug_settings.items())}}}\n"
    f"\t\tname = Debug;\n"
    f"\t}};")

widget_release_cfg = uid()
add(widget_release_cfg, "")
all_objects[-1] = (widget_release_cfg,
    f"\t{widget_release_cfg} = {{\n"
    f"\t\tisa = XCBuildConfiguration;\n"
    f"\t\tbuildSettings = {{{' '.join(f'{k} = {v};' for k,v in widget_release_settings.items())}}}\n"
    f"\t\tname = Release;\n"
    f"\t}};")

widget_cfg_list = uid()
add(widget_cfg_list, "")
all_objects[-1] = (widget_cfg_list,
    f"\t{widget_cfg_list} = {{\n"
    f"\t\tisa = XCConfigurationList;\n"
    f"\t\tbuildConfigurations = ({widget_debug_cfg}, {widget_release_cfg});\n"
    f"\t\tdefaultConfigurationName = Debug;\n"
    f"\t}};")

# Project-level configs
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

proj_debug_cfg = uid()
add(proj_debug_cfg, "")
all_objects[-1] = (proj_debug_cfg,
    f"\t{proj_debug_cfg} = {{\n"
    f"\t\tisa = XCBuildConfiguration;\n"
    f"\t\tbuildSettings = {{{' '.join(f'{k} = {v};' for k,v in proj_debug_settings.items())}}}\n"
    f"\t\tname = Debug;\n"
    f"\t}};")

proj_release_cfg = uid()
add(proj_release_cfg, "")
all_objects[-1] = (proj_release_cfg,
    f"\t{proj_release_cfg} = {{\n"
    f"\t\tisa = XCBuildConfiguration;\n"
    f"\t\tbuildSettings = {{{' '.join(f'{k} = {v};' for k,v in proj_release_settings.items())}}}\n"
    f"\t\tname = Release;\n"
    f"\t}};")

proj_cfg_list = uid()
add(proj_cfg_list, "")
all_objects[-1] = (proj_cfg_list,
    f"\t{proj_cfg_list} = {{\n"
    f"\t\tisa = XCConfigurationList;\n"
    f"\t\tbuildConfigurations = ({proj_debug_cfg}, {proj_release_cfg});\n"
    f"\t\tdefaultConfigurationName = Debug;\n"
    f"\t}};")

# ── Targets ──────────────────────────────────────────────────────────────────

# Widget target first (so app target can depend on it)
widget_target = uid()
add(widget_target, "")
widget_deps = "()"
all_objects[-1] = (widget_target,
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
    f"\t}};")

# App target depends on widget → need container proxy + target dependency
widget_proxy = uid()
add(widget_proxy, "")
all_objects[-1] = (widget_proxy,
    f"\t{widget_proxy} = {{\n"
    f"\t\tisa = PBXContainerItemProxy;\n"
    f"\t\tcontainerPortal = {project_group};\n"
    f"\t\tproxyType = 1;\n"
    f"\t\tremoteGlobalID = {widget_target};\n"
    f"\t\tremoteInfo = CallMeWidget;\n"
    f"\t}};")

app_dep = uid()
add(app_dep, "")
all_objects[-1] = (app_dep,
    f"\t{app_dep} = {{\n"
    f"\t\tisa = PBXTargetDependency;\n"
    f"\t\ttarget = {widget_target};\n"
    f"\t\ttargetProxy = {widget_proxy};\n"
    f"\t}};")

callme_target = uid()
add(callme_target, "")
all_objects[-1] = (callme_target,
    f"\t{callme_target} = {{\n"
    f"\t\tisa = PBXNativeTarget;\n"
    f"\t\tbuildConfigurationList = {app_cfg_list};\n"
    f"\t\tbuildPhases = ({app_src_phase_uid}, {app_fw_phase}, {app_res_phase});\n"
    f"\t\tbuildRules = ();\n"
    f"\t\tdependencies = ({app_dep});\n"
    f"\t\tname = CallMe;\n"
    f"\t\tproductName = CallMe;\n"
    f"\t\tproductReference = {callme_app_ref};\n"
    f"\t\tproductType = com.apple.product-type.application;\n"
    f"\t}};")

# ── PBXProject (root object) ────────────────────────────────────────────────
# Must be inserted first
proj_obj_id = uid()
proj_children_all = ", ".join(str(x) for x in [
    callme_group, widget_group, plist_app_ref, plist_widget_ref,
    ent_ref, audio_ref, callme_app_ref, widget_appex_ref, proj_cfg_list
])
all_objects.insert(0, (proj_obj_id, ""))
all_objects[0] = (proj_obj_id,
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
    f"\t}};")

# ── Write pbxproj ───────────────────────────────────────────────────────────
XCODEDIR.mkdir(parents=True, exist_ok=True)
WORKSPACE.mkdir(parents=True, exist_ok=True)

lines = ["// !$*UTF8*$!", ""]
for _, txt in all_objects:
    lines.append(txt)
lines.append("")
PBXPROJ.write_text("\n".join(lines))

xcwork = '''<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:CallMe.xcodeproj">
   </FileRef>
</Workspace>'''
(WORKSPACE / "contents.xcworkspacedata").write_text(xcwork)

print(f"✓ Generated {PBXPROJ}")
print(f"✓ Generated {WORKSPACE / 'contents.xcworkspacedata'}")
print(f"  App target 'CallMe' — {len(app_swift_refs)} Swift files + resources")
print(f"  Widget target 'CallMeWidget' — {len(widget_swift_refs)} Swift files")
print()
print("Next: open CallMe.xcodeproj in Xcode 26+ and build for iPhone simulator or device.")
print("      XcodeGen not required — project is hand-crafted and ready to open.")
