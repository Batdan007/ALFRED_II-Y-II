#!/usr/bin/env python3
"""
ALFRED Windows Installer Builder
=================================
Creates a professional Windows installer (.exe) for ALFRED.

Requirements:
    pip install pyinstaller
    Inno Setup 6 (https://jrsoftware.org/isdl.php)

Usage:
    python build_installer.py

Output:
    dist/ALFRED_Setup_3.0.0.exe

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configuration
APP_NAME = "ALFRED"
APP_VERSION = "3.0.0"
APP_PUBLISHER = "CAMDAN Enterprises LLC"
APP_AUTHOR = "Daniel J Rita (BATDAN)"
APP_URL = "https://github.com/Batdan007/ALFRED_II-Y-II"

# Paths
ROOT_DIR = Path(__file__).parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def check_requirements():
    """Check if build tools are available"""
    print_header("Checking Build Requirements")

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"  [OK] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  [MISSING] PyInstaller - Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Check Inno Setup
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
    ]
    inno_exe = None
    for path in inno_paths:
        if os.path.exists(path):
            inno_exe = path
            print(f"  [OK] Inno Setup found at {path}")
            break

    if not inno_exe:
        print("  [WARN] Inno Setup not found")
        print("         Download from: https://jrsoftware.org/isdl.php")
        print("         Will create standalone exe only (no installer)")

    return inno_exe


def build_exe():
    """Build standalone executable with PyInstaller"""
    print_header("Building Executable with PyInstaller")

    # PyInstaller spec
    pyinstaller_args = [
        "pyinstaller",
        "--name=alfred",
        "--onefile",
        "--console",
        f"--icon=assets/alfred_icon.ico" if (ROOT_DIR / "assets/alfred_icon.ico").exists() else "",
        "--add-data=requirements.txt;.",
        "--add-data=.env.example;." if (ROOT_DIR / ".env.example").exists() else "",
        "--hidden-import=anthropic",
        "--hidden-import=openai",
        "--hidden-import=groq",
        "--hidden-import=google.generativeai",
        "--hidden-import=faster_whisper",
        "--hidden-import=edge_tts",
        "--hidden-import=sounddevice",
        "--hidden-import=rich",
        "--hidden-import=pydantic",
        "--collect-all=anthropic",
        "--collect-all=faster_whisper",
        "--noconfirm",
        "alfred/__main__.py",
    ]

    # Remove empty args
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]

    print(f"  Running: {' '.join(pyinstaller_args[:5])}...")
    result = subprocess.run(pyinstaller_args, cwd=ROOT_DIR)

    if result.returncode != 0:
        print("  [FAIL] PyInstaller failed")
        return False

    # Rename to ALFRED.exe
    exe_path = DIST_DIR / "alfred.exe"
    if exe_path.exists():
        final_path = DIST_DIR / "ALFRED.exe"
        shutil.move(exe_path, final_path)
        print(f"  [OK] Created: {final_path}")
        return True

    return False


def create_inno_script():
    """Create Inno Setup script"""
    script = f'''
; ALFRED Windows Installer Script
; Created by build_installer.py

#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "{APP_PUBLISHER}"
#define MyAppURL "{APP_URL}"
#define MyAppExeName "ALFRED.exe"

[Setup]
AppId={{{{8F3E9A5B-4C2D-4E1F-9A8B-7C6D5E4F3A2B}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=ALFRED_Setup_{{#MyAppVersion}}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "addtopath"; Description: "Add ALFRED to system PATH"; GroupDescription: "System Integration"

[Files]
Source: "dist\\ALFRED.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{{app}}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{{app}}"; DestName: ".env.example"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion isreadme

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{#MyAppName}} Voice Mode"; Filename: "{{app}}\\{{#MyAppExeName}}"; Parameters: "--voice"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"; \\
    ValueType: expandsz; ValueName: "Path"; ValueData: "{{olddata}};{{app}}"; \\
    Tasks: addtopath; Check: NeedsAddPath('{{app}}')

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; \\
    Flags: nowait postinstall skipifsilent
Filename: "{{app}}\\{{#MyAppExeName}}"; Parameters: "--setup"; Description: "Run initial setup"; \\
    Flags: nowait postinstall skipifsilent unchecked

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKLM, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
     'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;
'''
    script_path = ROOT_DIR / "installer.iss"
    script_path.write_text(script)
    print(f"  [OK] Created: {script_path}")
    return script_path


def build_installer(inno_exe):
    """Build installer with Inno Setup"""
    print_header("Building Windows Installer")

    script_path = create_inno_script()

    if not inno_exe:
        print("  [SKIP] Inno Setup not available")
        print("         Standalone exe available at: dist/ALFRED.exe")
        return False

    print(f"  Running Inno Setup...")
    result = subprocess.run([inno_exe, str(script_path)], cwd=ROOT_DIR)

    if result.returncode == 0:
        installer_path = DIST_DIR / f"ALFRED_Setup_{APP_VERSION}.exe"
        print(f"  [OK] Created: {installer_path}")
        return True

    print("  [FAIL] Inno Setup failed")
    return False


def create_portable_zip():
    """Create portable ZIP distribution"""
    print_header("Creating Portable ZIP")

    import zipfile

    zip_name = DIST_DIR / f"ALFRED_Portable_{APP_VERSION}.zip"

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add exe
        exe_path = DIST_DIR / "ALFRED.exe"
        if exe_path.exists():
            zf.write(exe_path, "ALFRED.exe")

        # Add config files
        for filename in ["requirements.txt", ".env.example", "README.md"]:
            filepath = ROOT_DIR / filename
            if filepath.exists():
                zf.write(filepath, filename)

    print(f"  [OK] Created: {zip_name}")
    return True


def main():
    print(f"""
{'='*60}
  ALFRED Windows Installer Builder
  Version {APP_VERSION}
{'='*60}
""")

    # Check requirements
    inno_exe = check_requirements()

    # Build executable
    if not build_exe():
        print("\n[FAIL] Build failed")
        return 1

    # Build installer
    build_installer(inno_exe)

    # Create portable ZIP
    create_portable_zip()

    print_header("Build Complete!")
    print(f"""
  Output files in: {DIST_DIR}

  - ALFRED.exe              Standalone executable
  - ALFRED_Setup_{APP_VERSION}.exe   Windows installer
  - ALFRED_Portable_{APP_VERSION}.zip  Portable distribution

  To test: dist\\ALFRED.exe --help
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
