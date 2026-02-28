---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py google-drive`

# Google Drive

Lightweight Google Drive integration with standalone OAuth authentication. No MCP server required.

> **⚠️ Requires Google Workspace account.** Personal Gmail accounts are not supported.

## First-Time Setup

Authenticate with Google (opens browser):

```bash
python scripts/auth.py login
```

Check authentication status:

```bash
python scripts/auth.py status
```

Logout when needed:

```bash
python scripts/auth.py logout
```

## Commands

All operations via `scripts/drive.py`. Auto-authenticates on first use if not logged in.

```bash
# Search for files (full-text search)
python scripts/drive.py search "quarterly report"

# Search by title only
python scripts/drive.py search "title:budget"

# Search using Google Drive URL (extracts ID automatically)
python scripts/drive.py search "https://drive.google.com/drive/folders/1ABC123..."

# Search files shared with you
python scripts/drive.py search --shared-with-me

# Search with pagination
python scripts/drive.py search "report" --limit 5 --page-token "..."

# Find a folder by exact name
python scripts/drive.py find-folder "Project Documents"

# List files in root Drive
python scripts/drive.py list

# List files in a specific folder
python scripts/drive.py list 1ABC123xyz --limit 20

# Download a file
python scripts/drive.py download 1ABC123xyz ./downloads/report.pdf
```

## Search Query Formats

The search command supports multiple query formats:

| Format | Example | Description |
|--------|---------|-------------|
| Full-text | `"quarterly report"` | Searches file contents and names |
| Title | `"title:budget"` | Searches file names only |
| URL | `https://drive.google.com/...` | Extracts and uses file/folder ID |
| Folder ID | `1ABC123...` | Lists folder contents (25+ char IDs) |
| Native query | `mimeType='application/pdf'` | Pass-through Drive query syntax |

## File ID Format

Google Drive uses long IDs like `1ABC123xyz_-abc123`. Get IDs from:

- `search` results
- `find-folder` results
- `list` results
- Google Drive URLs

## Download Limitations

- Regular files (PDFs, images, etc.) download directly
- Google Docs/Sheets/Slides cannot be downloaded via this tool
- For Google Workspace files, use export or dedicated tools

## Token Management

Tokens stored securely using the system keyring:

- **macOS**: Keychain
- **Windows**: Windows Credential Locker
- **Linux**: Secret Service API (GNOME Keyring, KDE Wallet, etc.)

Service name: `google-drive-skill-oauth`

Automatically refreshes expired tokens using Google's cloud function.
