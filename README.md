# Local AI Chat - Build System

This build system is designed to package the Local AI Chat application into a standalone executable distribution that doesn't require Python to be installed on the end user's machine.

## Features

- Packages the entire application into a standalone executable
- Creates proper installers for Windows (using Inno Setup)
- Maintains direct file system access to key directories (models, conversations)
- Works in both development mode and as a packaged application
- Simple user experience with automatic browser opening

## Requirements for Building

- Python 3.8 or higher
- PyInstaller (`pip install pyinstaller`)
- For Windows installers: [Inno Setup 6](https://jrsoftware.org/isdl.php)

## Directory Structure

The packaged application exposes the following directories:

- `ai_models/` - Store your AI model files (.gguf format)
- `conversations/` - Your saved conversations
- `logs/` - Application logs

## How to Build

### Quick Build (everything)

To build the application and create an installer:

```bash
python build_all.py
```

This script will:

1. Check all requirements
2. Build the application using PyInstaller
3. Create an installer (Windows) or zip package (other platforms)

### Build Options

- Skip installer creation:

  ```bash
  python build_all.py --no-installer
  ```

- Skip application rebuild (use existing build):
  ```bash
  python build_all.py --no-app-build
  ```

### Step-by-Step Build

If you prefer to run each step manually:

1. Build just the application:

   ```bash
   python build.py
   ```

2. Build with clean directories:

   ```bash
   python build.py --clean
   ```

3. Create Windows installer (after building the application):
   ```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
   ```

## Development Mode

During development, you can still run the application normally with:

```bash
python local-ai-chat-app.py
```

The code automatically detects whether it's running in development or packaged mode and adjusts paths accordingly.

## Building with CUDA Support

Phase 1 of this build system doesn't yet include CUDA detection and utilization. That will be implemented in Phase 2.

## Output Locations

- Built application: `dist/LocalAIChat/`
- Windows installer: `Output/LocalAIChat_Setup.exe`
- Zip package (non-Windows): `dist/LocalAIChat.zip`

## Troubleshooting

- If the build fails with missing dependencies, run:

  ```bash
  pip install -r requirements.txt
  ```

- If paths are incorrect in the packaged app, check the `is_packaged()` function in `local-ai-chat-app.py`.

- Log files are stored in the `logs` directory and can help diagnose issues.
