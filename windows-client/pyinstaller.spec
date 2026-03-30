# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for NIRIX Diagnostics Windows Client

block_cipher = None

a = Analysis(
    ['nirix_win/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Test_Programs', 'Test_Programs'),
    ],
    hiddenimports=[
        'nirix_win.ui.login_window',
        'nirix_win.ui.dashboard_window',
        'nirix_win.ui.tests_window',
        'nirix_win.api_client.auth_client',
        'nirix_win.api_client.vehicles_client',
        'nirix_win.api_client.tests_client',
        'nirix_win.api_client.bundle_client',
        'nirix_win.api_client.version_client',
        'nirix_win.api_client.logs_client',
        'nirix_win.can_interface.pcan',
        'nirix_win.can_interface.kvaser',
        'nirix_win.can_interface.vector',
        'nirix_win.tests_runtime.loader',
        'nirix_win.tests_runtime.executor',
        'nirix_win.tests_runtime.env_check',
        'nirix_win.storage.paths',
        'nirix_win.storage.version_store',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Nirix',
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
    icon='nirix_win/assets/icon.ico',
    version='version_info.txt',
)
