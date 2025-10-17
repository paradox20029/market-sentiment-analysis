# Setup script for Windows PowerShell
# Creates venv, activates, upgrades pip, and installs requirements
param(
    [string]$VenvPath = ".\venv"
)

python -m venv $VenvPath
Write-Host "Created venv at $VenvPath"

Write-Host "Setting Execution Policy for CurrentUser (allows Activate.ps1 to run)"
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

Write-Host "Activate the virtual environment with:`n$VenvPath\Scripts\Activate.ps1`
Then run:`npip install --upgrade pip; pip install -r requirements.txt"
