#!/usr/bin/env python3

import logging
import base64
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("puppeteer-server")

# Constants
DEFAULT_TIMEOUT = 30000  # 30 seconds
DEFAULT_NAVIGATION_TIMEOUT = 60000  # 60 seconds

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.console_logs = []
        self.screenshots = {}

    async def ensure_browser(self):
        if not self.browser:
            logger.info("Starting new browser instance...")
            self.playwright = await async_playwright().start()
            
            # Create user data directory
            user_data_dir = Path.home() / ".mcp-puppeteer" / "user_data"
            user_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Launch browser with persistent context
            context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                args=[
                    '--start-maximized',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certificate-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-web-security',
                    '--disable-site-isolation-trials'
                ],
                viewport={"width": 1280, "height": 720},
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation', 'notifications'],
                color_scheme='light',
                accept_downloads=True
            )
            
            self.browser = context
            self.page = await context.new_page()
            
            # Apply stealth mode to avoid detection
            stealth_config = Stealth(
                navigator_languages=True,
                navigator_permissions=True,
                navigator_plugins=True,
                navigator_webdriver=True,
                navigator_user_agent=True,
                navigator_vendor=True,
                chrome_runtime=True,
                webgl_vendor=True,
                navigator_hardware_concurrency=True,
                media_codecs=True
            )
            await stealth_config.apply_stealth_async(self.page)
            logger.info("Stealth mode applied to browser page")
            
            async def handle_console(msg):
                log_entry = f"[{msg.type}] {msg.text}"
                self.console_logs.append(log_entry)
                logger.info(f"Browser console: {log_entry}")
            
            self.page.on("console", handle_console)
            logger.info("Browser instance started successfully")
        return self.page

    async def check_page_loaded(self, page, max_wait=5000):
        """Check if page has loaded successfully within timeout period"""
        try:
            # Wait for any element to appear
            await page.wait_for_selector('body *', timeout=max_wait)
            return True
        except PlaywrightTimeout:
            return False
        except Exception as e:
            logger.error(f"Error checking page load: {e}")
            return False

browser_manager = BrowserManager()
app = Server("puppeteer-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="puppeteer_navigate",
            description="Navigate to a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "timeout": {"type": "number", "description": "Navigation timeout in milliseconds"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="puppeteer_screenshot",
            description="Take a screenshot of the current page or a specific element",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the screenshot"},
                    "selector": {"type": "string", "description": "CSS selector for element to screenshot"},
                    "width": {"type": "number", "description": "Width in pixels (default: 1280)"},
                    "height": {"type": "number", "description": "Height in pixels (default: 720)"},
                    "timeout": {"type": "number", "description": "Timeout in milliseconds for finding elements"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="puppeteer_click",
            description="Click an element on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for element to click"},
                    "timeout": {"type": "number", "description": "Timeout in milliseconds"}
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="puppeteer_fill",
            description="Fill out an input field",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for input field"},
                    "value": {"type": "string", "description": "Value to fill"},
                    "timeout": {"type": "number", "description": "Timeout in milliseconds"}
                },
                "required": ["selector", "value"]
            }
        ),
        Tool(
            name="puppeteer_evaluate",
            description="Execute JavaScript in the browser console",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript code to execute"},
                    "timeout": {"type": "number", "description": "Timeout in milliseconds"}
                },
                "required": ["script"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        page = await browser_manager.ensure_browser()
        timeout = arguments.get("timeout", DEFAULT_TIMEOUT)
        
        if name == "puppeteer_navigate":
            url = arguments["url"]
            logger.info(f"Attempting to navigate to {url}")
            nav_timeout = arguments.get("timeout", DEFAULT_NAVIGATION_TIMEOUT)
            
            try:
                # Navigate with wait_until options for better compatibility
                response = await page.goto(url, timeout=nav_timeout, wait_until="domcontentloaded")
                
                # Additional wait for network to be idle (helps with dynamic content)
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    # Network idle timeout is not critical
                    pass
                
                # Check response status
                if response and response.status >= 400:
                    return [TextContent(
                        type="text",
                        text=f"Navigation completed but server returned error {response.status} for {url}"
                    )]
                
                return [TextContent(
                    type="text",
                    text=f"Successfully navigated to {url}"
                )]
            except PlaywrightTimeout:
                return [TextContent(
                    type="text",
                    text=f"Navigation timeout ({nav_timeout}ms) exceeded for {url}. The page might be loading too slowly."
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Failed to navigate to {url}: {str(e)}"
                )]

        elif name == "puppeteer_screenshot":
            try:
                width = arguments.get("width", 1280)
                height = arguments.get("height", 720)
                await page.set_viewport_size({"width": width, "height": height})
                
                screenshot = None
                if "selector" in arguments:
                    logger.info(f"Taking screenshot of element: {arguments['selector']}")
                    element = await page.wait_for_selector(arguments["selector"], timeout=timeout)
                    if element:
                        screenshot = await element.screenshot()
                else:
                    logger.info("Taking full page screenshot")
                    screenshot = await page.screenshot()
                    
                if screenshot:
                    browser_manager.screenshots[arguments["name"]] = screenshot
                    screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                    return [
                        TextContent(
                            type="text",
                            text=f"Screenshot '{arguments['name']}' taken at {width}x{height}"
                        ),
                        ImageContent(
                            type="image",
                            data=screenshot_b64,
                            mimeType="image/png"
                        )
                    ]
            except PlaywrightTimeout:
                return [TextContent(
                    type="text",
                    text=f"Screenshot timeout ({timeout}ms) exceeded"
                )]

        elif name == "puppeteer_click":
            try:
                logger.info(f"Clicking element: {arguments['selector']}")
                await page.click(arguments["selector"], timeout=timeout)
                return [TextContent(
                    type="text",
                    text=f"Clicked: {arguments['selector']}"
                )]
            except PlaywrightTimeout:
                return [TextContent(
                    type="text",
                    text=f"Click timeout ({timeout}ms) exceeded for selector: {arguments['selector']}"
                )]

        elif name == "puppeteer_fill":
            try:
                logger.info(f"Filling element: {arguments['selector']}")
                await page.fill(arguments["selector"], arguments["value"], timeout=timeout)
                return [TextContent(
                    type="text",
                    text=f"Filled {arguments['selector']} with: {arguments['value']}"
                )]
            except PlaywrightTimeout:
                return [TextContent(
                    type="text",
                    text=f"Fill timeout ({timeout}ms) exceeded for selector: {arguments['selector']}"
                )]

        elif name == "puppeteer_evaluate":
            try:
                logger.info("Evaluating JavaScript")
                result = await page.evaluate(arguments["script"])
                return [TextContent(
                    type="text",
                    text=f"Execution result:\n{result}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"JavaScript evaluation error: {str(e)}"
                )]

    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
