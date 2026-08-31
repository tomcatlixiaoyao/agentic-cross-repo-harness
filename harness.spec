# Build with: pyinstaller --clean --noconfirm harness.spec

from pathlib import Path


project_root = Path.cwd()

analysis = Analysis(
    [str(project_root / "scripts" / "harness_cli.py")],
    pathex=[str(project_root / "scripts")],
    binaries=[],
    datas=[
        (str(project_root / "templates"), "templates"),
        (str(project_root / "scripts" / "check_harness.py"), "scripts"),
        (str(project_root / "scripts" / "doctor_harness.py"), "scripts"),
        (str(project_root / "scripts" / "harness_lib.py"), "scripts"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="harness",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
