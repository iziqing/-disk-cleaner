# Claude Disk Cleaner

🧹 **Human-AI Collaborative Disk Cleanup Tool**

Leverage **WizTree's fast scanning** + **AI intelligent analysis** to efficiently clean up disk space.

[中文文档](../README.md)

## Features

- ⚡ **Fast Scanning**: Uses WizTree's MFT scanning technology
- 🤖 **AI Analysis**: Intelligently identifies cleanable directories
- 🎯 **Priority Classification**: High/Medium/Low priority cleanup suggestions
- 🔒 **Safe Cleanup**: Never deletes system files or user data
- 🤝 **Human-AI Collaboration**: Two modes for different user preferences

## Two Modes

### Mode 1: Standard Permission CLI

```
👤 Human: Scan + Export data
🤖 AI: Analyze + Generate cleanup script
👤 Human: Execute cleanup script
```

Best for: Users who prioritize security

### Mode 2: Admin Permission CLI (Recommended)

```
👤 Human: Just say "clean my disk"
🤖 AI: Auto scan + Analyze + Execute cleanup
```

Best for: Users who prioritize efficiency

## Quick Start

### Prerequisites

- [WizTree](https://diskanalyzer.com/) - Free disk space analyzer
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) - Anthropic's CLI tool
- Python 3.x

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/iziqing/-disk-cleaner.git
   cd -disk-cleaner
   ```

2. Place WizTree in the `WizTree/` directory (or update path in config)

3. Copy command to your project:
   ```bash
   cp -r .claude/commands/clean-c-drive.md YOUR_PROJECT/.claude/commands/
   cp -r skills/clean-c-drive YOUR_PROJECT/skills/
   ```

### Usage

**With Admin Permission (Recommended):**

```powershell
# Open terminal as Administrator
claude

# Then type:
/clean-c-drive
```

**Without Admin Permission:**

1. Run WizTree as Administrator, scan and export CSV
2. Save to `skills/clean-c-drive/data/`
3. Run `/clean-c-drive` in Claude Code

## What Gets Cleaned

### High Priority (Safe to Clean)
| Category | Description |
|----------|-------------|
| Windows Update Cache | `SoftwareDistribution\Download` |
| NVIDIA Update Cache | `ota-artifacts` |
| Browser IndexedDB | Video streaming cache |
| pip/npm/yarn Cache | Package manager cache |
| Temp Files | Temporary files |

### Medium Priority (Clean with Caution)
| Category | Description |
|----------|-------------|
| App Cache | Various application caches |
| Log Files | Application logs |
| GPU Cache | Shader cache |

### Low Priority (Confirm Before Clean)
| Category | Description |
|----------|-------------|
| Gradle Cache | Build cache |
| Cargo Cache | Rust package cache |
| Go Modules | Go package cache |

## Project Structure

```
-disk-cleaner/
├── .claude/
│   └── commands/
│       └── clean-c-drive.md    # Slash command definition
├── skills/
│   └── clean-c-drive/
│       ├── scan.ps1            # Scan script
│       ├── analyze.py          # Analysis script
│       ├── skill.md            # Skill definition
│       ├── GUIDE.md            # Usage guide
│       └── data/               # Scan data directory
├── WizTree/                    # WizTree executable (not included)
├── LICENSE
└── README.md
```

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Workflow                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  WizTree    │───▶│  AI Agent   │───▶│   Cleanup   │     │
│  │  Fast Scan  │    │  Analysis   │    │   Execute   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│        │                  │                  │              │
│        ▼                  ▼                  ▼              │
│   MFT Scanning      Smart Pattern      Safe Deletion        │
│   (seconds)         Recognition        with Confirm         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Custom Cleanup Patterns

Edit `skills/clean-c-drive/analyze.py`:

```python
CLEANABLE_PATTERNS = {
    "high": {
        "patterns": [
            {"pattern": "your_pattern", "name": "Description", "safe": True},
        ]
    }
}
```

### WizTree Path

Update path in `skills/clean-c-drive/scan.ps1`:

```powershell
param(
    [string]$WizTreePath = "YOUR_PATH\WizTree64.exe",
    ...
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- [WizTree](https://diskanalyzer.com/) - The fastest disk space analyzer
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - AI-powered CLI tool

## Disclaimer

⚠️ **Use at your own risk.** Always review the cleanup report before confirming deletion. The authors are not responsible for any data loss.
