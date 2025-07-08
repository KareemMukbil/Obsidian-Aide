<# OBSIDIAN AI ASSISTANT SETUP SCRIPT #>
$ErrorActionPreference = "Stop"

Write-Host "`n=== OBSIDIAN AI ASSISTANT SETUP ===" -ForegroundColor Cyan
Write-Host "This will set up your local AI assistant`n" -ForegroundColor Yellow

# 1. Verify Ollama installation
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama not found. Please install from:" -ForegroundColor Red
    Write-Host "https://ollama.com/download" -ForegroundColor Blue
    exit 1
}

# 2. Ensure llama2:7b model
Write-Host "`nChecking Ollama models..." -ForegroundColor Yellow
if (-not (ollama list | Select-String "llama2:7b")) {
    Write-Host "Downloading llama2:7b model (3.8GB)..." -ForegroundColor Yellow
    ollama pull llama2:7b
}

# 3. Create Python environment
Write-Host "`nCreating Python environment..." -ForegroundColor Yellow
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
Write-Host "`nInstalling Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt

# 5. Build index
Write-Host "`nBuilding knowledge index (this may take 10+ minutes)..." -ForegroundColor Yellow
python ingest.py

Write-Host "`n=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host "Start the server with: .\.venv\Scripts\Activate.ps1; python server.py" -ForegroundColor Cyan
Write-Host "Keep this running, then use the Templater snippet in Obsidian`n" -ForegroundColor Yellow