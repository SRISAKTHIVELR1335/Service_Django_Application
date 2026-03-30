param(
    [string]$Configuration = "Release"
)

Write-Host "[NIRIX] Creating virtual environment for Windows client..."
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r windows-client\requirements.txt

Write-Host "[NIRIX] Building Windows EXE with PyInstaller..."
pyinstaller windows-client\pyinstaller.spec

Write-Host "[NIRIX] Build completed. Check the dist/ folder."
