
# build.py
"""Script de build pour créer les exécutables"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path


def build_windows():
    """Build pour Windows"""
    PyInstaller.__main__.run([
        'main.py',
        '--name=Bestiaire',
        '--onefile',
        '--windowed',
        '--icon=assets/icon.ico',
        '--add-data=assets;assets',
        '--add-data=data;data',
        '--hidden-import=pygame',
        '--hidden-import=numpy',
        '--hidden-import=pydantic',
        '--distpath=dist/windows',
        '--workpath=build/windows',
        '--specpath=build/windows',
    ])

    # Copier les assets nécessaires
    shutil.copytree('assets', 'dist/windows/assets', dirs_exist_ok=True)
    shutil.copytree('data', 'dist/windows/data', dirs_exist_ok=True)


def build_macos():
    """Build pour macOS"""
    PyInstaller.__main__.run([
        'main.py',
        '--name=Bestiaire',
        '--onefile',
        '--windowed',
        '--icon=assets/icon.icns',
        '--add-data=assets:assets',
        '--add-data=data:data',
        '--osx-bundle-identifier=com.studioecorces.bestiaire',
        '--distpath=dist/macos',
        '--workpath=build/macos',
        '--specpath=build/macos',
    ])

    # Créer le .app bundle
    app_path = Path('dist/macos/Bestiaire.app')
    if app_path.exists():
        shutil.copytree('assets', app_path / 'Contents/Resources/assets', dirs_exist_ok=True)
        shutil.copytree('data', app_path / 'Contents/Resources/data', dirs_exist_ok=True)


def build_linux():
    """Build pour Linux"""
    PyInstaller.__main__.run([
        'main.py',
        '--name=bestiaire',
        '--onefile',
        '--add-data=assets:assets',
        '--add-data=data:data',
        '--distpath=dist/linux',
        '--workpath=build/linux',
        '--specpath=build/linux',
    ])

    # Créer l'AppImage
    shutil.copytree('assets', 'dist/linux/assets', dirs_exist_ok=True)
    shutil.copytree('data', 'dist/linux/data', dirs_exist_ok=True)

    # Créer le .desktop file
    desktop_content = """[Desktop Entry]
Name=Bestiaire
Comment=Roguelite deckbuilding avec attrition permanente
Exec=bestiaire
Icon=bestiaire
Type=Application
Categories=Game;CardGame;
"""

    with open('dist/linux/bestiaire.desktop', 'w') as f:
        f.write(desktop_content)


def build_all():
    """Build pour toutes les plateformes"""
    print("Building for Windows...")
    build_windows()

    print("Building for macOS...")
    build_macos()

    print("Building for Linux...")
    build_linux()

    print("Build complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        if platform == 'windows':
            build_windows()
        elif platform == 'macos':
            build_macos()
        elif platform == 'linux':
            build_linux()
        elif platform == 'all':
            build_all()
        else:
            print(f"Unknown platform: {platform}")
            print("Usage: python build.py [windows|macos|linux|all]")
    else:
        build_all()
