# setup.py
"""Configuration pour packaging et distribution"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="bestiaire-roguelite",
    version="1.0.0",
    author="Studio Écorces",
    author_email="contact@bestiaire-game.com",
    description="Bestiaire: Écorces & Échos - Roguelite deckbuilding avec attrition permanente",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/studio-ecorces/bestiaire",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pygame>=2.5.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "hypothesis>=6.0.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "cx_Freeze>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "bestiaire=bestiaire.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bestiaire": [
            "assets/cards/*.json",
            "assets/images/*.png",
            "assets/sounds/*.ogg",
            "assets/fonts/*.ttf",
        ],
    },
)

# Dockerfile
"""
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the game
CMD ["python", "main.py"]
"""

# .github/workflows/ci.yml
"""
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [created]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Run tests
      run: |
        pytest --cov=bestiaire --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[build]

    - name: Build executable
      run: |
        python build.py ${{ matrix.os }}

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: bestiaire-${{ matrix.os }}
        path: dist/

  release:
    needs: build
    if: github.event_name == 'release'
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Download artifacts
      uses: actions/download-artifact@v3

    - name: Create release assets
      run: |
        zip -r bestiaire-windows.zip bestiaire-windows-latest/
        zip -r bestiaire-macos.zip bestiaire-macos-latest/
        tar -czf bestiaire-linux.tar.gz bestiaire-ubuntu-latest/

    - name: Upload to release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          bestiaire-windows.zip
          bestiaire-macos.zip
          bestiaire-linux.tar.gz
"""