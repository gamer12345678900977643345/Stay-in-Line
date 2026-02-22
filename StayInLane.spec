# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('audio.py', '.'), ('road.png', '.'), ('motor.png', '.'), ('auto_baluw.png', '.'), ('auto_groen.png', '.'), ('auto_paars.png', '.'), ('auto_rood.png', '.'), ('truck_blauw.png', '.'), ('truck_groen.png', '.'), ('truck_paars.png', '.'), ('truck_rood.png', '.'), ('logo.png', '.'), ('game over.png', '.'), ('trofee.png', '.'), ('mute.png', '.'), ('unmute.png', '.'), ('soundtrack.ogg', '.'), ('engine.ogg', '.'), ('crash.ogg', '.'), ('designed, braam, synth, braams, brahm, resonant chorus bass (c) 01.wav', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='StayInLane',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
