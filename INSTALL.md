# Local AI Chat - Installation Guide

This guide provides instructions for installing and running the Local AI Chat application on your computer.

## System Requirements

- Windows 10 or Windows 11 (64-bit)
- 8GB RAM minimum (16GB recommended)
- At least 2GB of free disk space (plus space for AI models)
- Modern CPU with AVX2 support (for CPU-based inference)

## Installation Instructions

### Windows Installation

1. Download the `LocalAIChat_Setup.exe` installer.
2. Double-click the installer and follow the on-screen instructions.
3. By default, the application will be installed to:
   ```
   C:\Program Files\Local AI Chat
   ```
4. The installer will create a desktop shortcut and start menu entry.

### Portable Installation (All Platforms)

1. Download the `LocalAIChat.zip` file.
2. Extract the zip file to any location on your computer.
3. Run the application by double-clicking the `Launch_LocalAIChat` file.

## Post-Installation Setup

### Adding AI Models

The application requires GGUF-format AI models to function. To add a model:

1. Obtain a GGUF model file (e.g., `llama-3-8b.Q5_K_M.gguf`).
2. Place the model file in the `ai_models` folder within the application directory.
3. Start the application. The model will be automatically detected.

Popular models can be downloaded from:

- [Hugging Face](https://huggingface.co/models?sort=downloads&search=gguf)
- [TheBloke's Models](https://huggingface.co/TheBloke)

### First Run

1. Launch the application using the desktop shortcut or start menu entry.
2. A browser window will automatically open to `http://localhost:5000`.
3. Select your model from the dropdown in the top-right corner.
4. Start chatting with the AI!

## Folder Structure

After installation, you'll find the following key folders:

- `ai_models/` - Place your AI model files (.gguf) here
- `conversations/` - Your saved conversation history
- `logs/` - Application logs for troubleshooting

## Troubleshooting

### Common Issues

1. **Application doesn't start:**

   - Check the logs folder for error messages
   - Ensure you have at least 8GB of RAM available

2. **Models not appearing in dropdown:**

   - Ensure the model file is in the `ai_models` folder
   - Check that the model file name starts with a recognizable name
   - Verify the file has a `.gguf` extension

3. **Slow performance:**

   - Use a smaller or more optimized model
   - Try a quantized model (e.g., Q4_K_M instead of F16)
   - Close other resource-intensive applications

4. **Browser doesn't open automatically:**
   - Manually navigate to `http://localhost:5000` in your web browser

### Getting Help

If you encounter issues not covered in this guide:

1. Check the application logs in the `logs` folder
2. Refer to the README.md file for additional information
3. File an issue on the project's GitHub repository

## Uninstallation

### Windows

1. Go to "Add or Remove Programs" in Windows Settings
2. Find "Local AI Chat" in the list and click "Uninstall"
3. Follow the on-screen instructions

### Portable Installation

Simply delete the folder containing the extracted application files.
