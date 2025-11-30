# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cafeteria_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config_db.json', '.'),
        ('icon.ico', '.')  # Remova esta linha se não tiver ícone
    ],
    hiddenimports=[
        'tkcalendar', 'mysql.connector', 'mysql.connector.abstracts',
        'mysql.connector.authentication', 'mysql.connector.charsets',
        'mysql.connector.connection', 'mysql.connector.constants',
        'mysql.connector.converter', 'mysql.connector.cursor',
        'mysql.connector.dbapi', 'mysql.connector.errorcode',
        'mysql.connector.errors', 'mysql.connector.locales',
        'mysql.connector.network', 'mysql.connector.opentelemetry',
        'mysql.connector.pooling', 'mysql.connector.protocol',
        'mysql.connector.types', 'mysql.connector.utils',
        'mysql.connector.version'
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
    name='CafeteriaPDV',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False para não mostrar console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Remova esta linha se não tiver ícone
)
