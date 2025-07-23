# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation of a Model Context Protocol (MCP) server that provides browser automation capabilities using Playwright. It enables LLMs to interact with web pages through browser automation.

## Key Commands

### Installation
```bash
# Install dependencies using UV
uv sync

# Install Playwright browsers (required for browser automation)
uv run playwright install
```

### Running the Server
```bash
# Run the server directly with UV
uv run python puppeteer.py
```

### Development Setup
```bash
# Install with dev dependencies
uv sync --dev

# Run linting
uv run ruff check .
uv run black --check .

# Format code
uv run black .
uv run ruff check --fix .
```

## Architecture

### Core Components

1. **puppeteer.py** - Main server implementation
   - `BrowserManager` class handles browser lifecycle and page management
   - MCP server setup with tool implementations
   - Browser launches in non-headless mode for debugging
   - Default viewport: 1280x720

2. **Available MCP Tools**:
   - `puppeteer_navigate` - Navigate to URLs with configurable timeout
   - `puppeteer_screenshot` - Capture screenshots (full page or specific elements)
   - `puppeteer_click` - Click elements on the page
   - `puppeteer_fill` - Fill input fields
   - `puppeteer_evaluate` - Execute JavaScript in browser context

### Key Technical Details

- Uses Playwright async API for browser automation
- Console logs are captured and stored
- Screenshots are base64 encoded and stored in memory
- All operations have configurable timeouts (default 30s, navigation 60s)
- Error handling includes specific cases for navigation failures, element not found, and timeout errors

### Dependencies

- `mcp` - Model Context Protocol implementation
- `playwright>=1.40.0` - Browser automation library
- Python 3.10+ required (due to mcp dependency)

### Package Management

This project uses UV for fast, reliable Python package management. All dependencies are locked in `uv.lock` for reproducible builds.