# Puppeteer MCP Server (Python Implementation)

## 🔧 Fork Changelog

This fork includes the following enhancements:

### Migration to UV Package Manager
- Replaced traditional pip/requirements.txt with modern UV package management
- Added `pyproject.toml` for better dependency management
- Faster and more reliable package installation with `uv.lock`

### Stealth Mode Implementation
- Added `playwright-stealth` integration for anti-bot detection
- Configured advanced browser arguments including `--disable-blink-features=AutomationControlled`
- Implemented persistent browser context with user data directory
- Enhanced page load detection for better compatibility with dynamic websites

⚠️ **WARNING: The stealth features in this fork are intended for personal testing and educational purposes only. Users are responsible for complying with all applicable laws and website terms of service.**

---

A Model Context Protocol server that provides browser automation capabilities using Playwright (Python's equivalent to Puppeteer). This server enables LLMs to interact with web pages, take screenshots, and execute JavaScript in a real browser environment.

## Overview
This Python implementation provides a stable alternative to the TypeScript version, offering the same capabilities with improved error handling and logging. It uses Playwright, which is the Python equivalent to Puppeteer, providing robust browser automation capabilities.

## Key Features
* Full browser automation
* Page navigation
* Screenshot capture (full page or elements)
* Form interaction (clicking and filling)
* JavaScript execution
* Console log monitoring
* Configurable timeouts
* Detailed error handling
* Comprehensive logging

## Prerequisites
* Python 3.10+
* uv (Fast Python package installer and resolver)

## Installation
1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install the required packages:
```bash
uv sync
```

3. Install Playwright browsers:
```bash
uv run playwright install
```

## Usage

### Starting the Server
Run the server directly:
```bash
uv run python puppeteer.py
```

### Claude Desktop Configuration
Add this to your Claude configuration file:
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "uv",
      "args": ["run", "python", "path/to/puppeteer.py"]
    }
  }
}
```

## Available Tools

### puppeteer_navigate
Navigate to any URL in the browser.
```json
{
  "name": "puppeteer_navigate",
  "arguments": {
    "url": "https://example.com",
    "timeout": 60000  // optional, defaults to 60000ms
  }
}
```

### puppeteer_screenshot
Capture screenshots of the entire page or specific elements.
```json
{
  "name": "puppeteer_screenshot",
  "arguments": {
    "name": "my_screenshot",
    "selector": "#specific-element",  // optional
    "width": 1280,  // optional, default: 1280
    "height": 720,  // optional, default: 720
    "timeout": 30000  // optional, defaults to 30000ms
  }
}
```

### puppeteer_click
Click elements on the page.
```json
{
  "name": "puppeteer_click",
  "arguments": {
    "selector": ".button-class",
    "timeout": 30000  // optional, defaults to 30000ms
  }
}
```

### puppeteer_fill
Fill out input fields.
```json
{
  "name": "puppeteer_fill",
  "arguments": {
    "selector": "#input-id",
    "value": "text to fill",
    "timeout": 30000  // optional, defaults to 30000ms
  }
}
```

### puppeteer_evaluate
Execute JavaScript in the browser console.
```json
{
  "name": "puppeteer_evaluate",
  "arguments": {
    "script": "document.title",
    "timeout": 30000  // optional, defaults to 30000ms
  }
}
```

## Error Handling
The server provides detailed error messages for common scenarios:
* Navigation failures
* Element not found
* Timeout errors
* JavaScript execution errors
* Screenshot failures

## Logging
Comprehensive logging is implemented with different levels:
* INFO: Standard operations
* ERROR: Operation failures
* DEBUG: Detailed execution information

## Notes
* Browser launches in non-headless mode for better debugging
* Default viewport size is 1280x720
* All timeouts are configurable
* Console logs are captured and stored
* Screenshots are stored in memory with base64 encoding

## Contributing
Contributions are welcome! Please read the repository's contributing guidelines before submitting pull requests.

## License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
