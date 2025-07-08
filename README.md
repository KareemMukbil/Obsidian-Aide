# Obsidian AI Assistant (Mistral Edition)

Fully offline AI assistant for your Obsidian vault using local Mistral 7B model. Now with folder-aware retrieval!

## Features
- 100% private - never leaves your computer
- Answers questions using your vault content
- Focus searches within specific folders
- Simple Templater integration
- Windows-optimized setup
- Faster & smarter responses with Mistral 7B

## Installation

### 1. System Requirements
- Windows 10/11 (64-bit)
- NVIDIA GPU (8GB+ VRAM recommended)
- 16GB+ RAM
- Python 3.10+

### 2. Install Dependencies
```powershell
# Run in PowerShell
irm get.scoop.sh | iex
scoop install git python
pip install virtualenv
```

### 3. Configure Vault Path
**Before running**, edit `ingest.py`:
```python
# Near bottom of ingest.py
VAULT_PATH = r"D:\PATH\TO\YOUR\VAULT"  # ← UPDATE THIS PATH
```

### 4. Setup Environment
```powershell
# Run setup script
.\setup.ps1
```

### 5. Install Mistral Model
```powershell
ollama pull mistral:instruct
```

## Usage

### 1. Index Your Vault
```powershell
python ingest.py
```
> **First run takes 1-60 mins** depending on vault size

### 2. Start AI Server
```powershell
python server.py
```
> Keep this running in background

### 3. Configure Templater Snippet
1. Create new template in Obsidian Templater
2. Paste the code in templater-snippet.md

### 4. Use in Obsidian
1. Create new note
2. Insert template via Templater
3. Ask questions about your vault!

## Updating Your Vault
Re-run when notes change:
```powershell
python ingest.py
python server.py
```

## Troubleshooting
**Q: Vault path not found?**
- Use full path in `ingest.py` (e.g., `C:\Users\Name\Obsidian Vault`)
- Escape backslashes: `r"C:\\Path\\To\\Vault"`

**Q: Server not responding?**
- Check Ollama is running: `ollama list`
- Verify port 5000 is free

**Q: Poor responses?**
- Try different folders
- Increase context in prompt:
```python
# In server.py
"num_predict": 2048  # Generate longer responses
```

## Advanced Configuration
| File | Key Configuration |
|------|-------------------|
| `ingest.py` | `VAULT_PATH`, chunk size (500 tokens) |
| `server.py` | Model (`mistral:instruct`), temperature (0.2) |
| Templater | `folder = "YourFolder"` |

> **Pro Tip**: Create multiple templates for different folders (e.g., `AI-Career.md`, `AI-Health.md`)
```
