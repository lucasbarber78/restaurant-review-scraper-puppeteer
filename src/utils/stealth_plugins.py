#!/usr/bin/env python3
"""
Stealth Plugins Module

This module provides classes and functions for applying stealth measures to the browser
to avoid bot detection when scraping websites.
"""

import random
import logging
import asyncio
import json
import os
from typing import Optional, Dict, List, Any, Union, Tuple

logger = logging.getLogger(__name__)

# Collection of user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
]

# WebGL Vendors and Renderers
WEBGL_VENDORS = [
    'Google Inc. (NVIDIA)',
    'Google Inc. (Intel)',
    'Google Inc. (AMD)',
    'Google Inc.',
    'Intel Inc.',
    'NVIDIA Corporation',
    'Apple Inc.',
]

WEBGL_RENDERERS = [
    'ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics 640 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (Apple M1)',
    'ANGLE (Apple M2)',
    'ANGLE (Intel, Intel(R) HD Graphics 400 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0)',
    'Metal (Apple M1)',
]


class StealthEnhancer:
    """Class for applying stealth enhancements to the browser."""
    
    def __init__(self, platform: str = "general"):
        """Initialize the stealth enhancer.
        
        Args:
            platform (str, optional): The platform to optimize for. Defaults to "general".
                Options: "general", "tripadvisor", "google", "yelp"
        """
        self.platform = platform.lower()
        self.user_agent = random.choice(USER_AGENTS)
        self.webgl_vendor = random.choice(WEBGL_VENDORS)
        self.webgl_renderer = random.choice(WEBGL_RENDERERS)
        
        logger.info(f"Initialized stealth enhancer for platform: {platform}")
        
    async def enhance_browser(self, page):
        """Apply stealth enhancements to the browser page.
        
        Args:
            page: Puppeteer page object.
        """
        logger.info("Applying stealth measures to browser...")
        
        # 1. Set a consistent user agent
        await page.setUserAgent(self.user_agent)
        
        # 2. Apply evasion scripts depending on platform
        await self._apply_general_evasion(page)
        
        if self.platform == "tripadvisor":
            await self._apply_tripadvisor_evasion(page)
        elif self.platform == "google":
            await self._apply_google_evasion(page)
        elif self.platform == "yelp":
            await self._apply_yelp_evasion(page)
            
        # 3. Implement plugins
        await self._apply_webgl_vendor_override(page)
        await self._apply_navigator_hardware_override(page)
        await self._apply_chrome_runtime_override(page)
        await self._apply_permissions_override(page)
        
        logger.info("Stealth measures applied successfully")
        
    async def simulate_human_behavior(self, page):
        """Simulate human-like behavior on the page.
        
        Args:
            page: Puppeteer page object.
        """
        try:
            # 1. Random mouse movements
            await self._simulate_mouse_movements(page)
            
            # 2. Scroll a bit
            await self._simulate_initial_scroll(page)
            
            # 3. Platform-specific human behavior
            if self.platform == "tripadvisor":
                await self._simulate_tripadvisor_browsing(page)
            elif self.platform == "google":
                await self._simulate_google_browsing(page)
            elif self.platform == "yelp":
                await self._simulate_yelp_browsing(page)
                
            logger.debug("Simulated human-like behavior on page")
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    async def detect_and_handle_captcha(self, page):
        """Detect and attempt to handle CAPTCHAs.
        
        Args:
            page: Puppeteer page object.
            
        Returns:
            bool: True if CAPTCHA was detected, False otherwise.
        """
        captcha_detected = False
        
        try:
            # Common CAPTCHA indicators
            captcha_indicators = [
                'captcha',
                'recaptcha',
                'hcaptcha',
                'security check',
                'verify you are human',
                'bot check',
                'captcha-container',
                'g-recaptcha',
                'h-captcha'
            ]
            
            # Check for CAPTCHA in page content
            page_text = await page.evaluate("() => document.body.innerText")
            page_html = await page.evaluate("() => document.body.innerHTML")
            
            # Check text content
            for indicator in captcha_indicators:
                if indicator.lower() in page_text.lower() or indicator.lower() in page_html.lower():
                    captcha_detected = True
                    logger.warning(f"CAPTCHA detected ({indicator})")
                    break
            
            # Check for CAPTCHA elements
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="captcha"]',
                'div.g-recaptcha',
                'div[class*="captcha"]',
                'form[action*="captcha"]',
                'div[data-sitekey]',
                'div#captcha',
                'div.captcha',
                'iframe[title*="recaptcha"]',
                'iframe[title*="security check"]'
            ]
            
            for selector in captcha_selectors:
                element = await page.querySelector(selector)
                if element:
                    captcha_detected = True
                    logger.warning(f"CAPTCHA element detected ({selector})")
                    break
            
            # If CAPTCHA detected, take screenshot and try to handle
            if captcha_detected:
                # Take screenshot for analysis
                screenshots_dir = os.path.join(os.getcwd(), "captcha_screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                
                timestamp = int(asyncio.get_event_loop().time())
                screenshot_path = os.path.join(screenshots_dir, f"captcha_{self.platform}_{timestamp}.png")
                await page.screenshot({'path': screenshot_path, 'fullPage': False})
                logger.info(f"CAPTCHA screenshot saved to: {screenshot_path}")
                
                # Currently we can't solve CAPTCHAs automatically
                # Just log the detection and return
                logger.warning("CAPTCHA detected but automatic solving is not implemented")
            
            return captcha_detected
            
        except Exception as e:
            logger.error(f"Error in CAPTCHA detection: {e}")
            return False
    
    async def _apply_general_evasion(self, page):
        """Apply general evasion scripts to the browser.
        
        Args:
            page: Puppeteer page object.
        """
        await page.evaluateOnNewDocument("""
            () => {
                // Overwrite the navigator properties
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                
                // Overwrite plugins length
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return {
                            length: 3,
                            item: function (index) {
                                return this[index] || null;
                            },
                            refresh: function() {},
                            [0]: {
                                description: "PDF Viewer",
                                filename: "internal-pdf-viewer",
                                name: "Chrome PDF Viewer"
                            },
                            [1]: {
                                description: "Chrome PDF Viewer",
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                name: "Chrome PDF Plugin"
                            },
                            [2]: {
                                description: "Native Client",
                                filename: "internal-nacl-plugin",
                                name: "Native Client"
                            }
                        };
                    }
                });
                
                // Add languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override property descriptor
                const oldCall = Function.prototype.call;
                function call() {
                    return oldCall.apply(this, arguments);
                }
                Function.prototype.call = call;
                
                const nativeToStringFunctionString = Error.toString().replace(/Error/g, "toString");
                const oldToString = Function.prototype.toString;
                
                function functionToString() {
                    if (this === window.navigator.permissions.query) {
                        return "function query() { [native code] }";
                    }
                    if (this === Function.prototype.toString) {
                        return nativeToStringFunctionString;
                    }
                    return oldCall.call(oldToString, this);
                }
                Function.prototype.toString = functionToString;
            }
        """)
    
    async def _apply_tripadvisor_evasion(self, page):
        """Apply TripAdvisor-specific evasion measures.
        
        Args:
            page: Puppeteer page object.
        """
        await page.evaluateOnNewDocument("""
            () => {
                // TripAdvisor-specific evasions
                
                // Define window.innerWidth/innerHeight dynamically
                const oldHeight = window.innerHeight;
                const oldWidth = window.innerWidth;
                Object.defineProperty(window, 'innerWidth', {
                    get: function() {
                        return oldWidth;
                    }
                });
                Object.defineProperty(window, 'innerHeight', {
                    get: function() {
                        return oldHeight;
                    }
                });
                
                // Override Modernizr which TripAdvisor sometimes uses for detection
                window.Modernizr = {
                    cssanimations: true,
                    csstransforms: true,
                    csstransforms3d: true,
                    csstransitions: true,
                    applicationcache: true,
                    canvas: true,
                    canvastext: true,
                    geolocation: true
                };
                
                // Override user agent detection
                window.navigator.appName = 'Netscape';
                window.navigator.appVersion = '5.0';
            }
        """)
    
    async def _apply_google_evasion(self, page):
        """Apply Google-specific evasion measures.
        
        Args:
            page: Puppeteer page object.
        """
        await page.evaluateOnNewDocument("""
            () => {
                // Google-specific evasions
                
                // Override reCAPTCHA detection
                // Intercept Google's detection methods
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({state: Notification.permission});
                    }
                    return originalQuery(parameters);
                };
                
                // Fix Google Chrome properties
                Object.defineProperty(navigator, 'vendor', {
                    get: () => "Google Inc."
                });
                
                // Add extra detection elements for Google
                Object.defineProperty(navigator, 'connection', {
                    get: () => {
                        return {
                            effectiveType: "4g",
                            downlink: 10,
                            rtt: 50
                        };
                    }
                });
            }
        """)
    
    async def _apply_yelp_evasion(self, page):
        """Apply Yelp-specific evasion measures.
        
        Args:
            page: Puppeteer page object.
        """
        await page.evaluateOnNewDocument("""
            () => {
                // Yelp-specific evasions
                
                // Overwrite console.debug to prevent some Yelp debug checks
                const originalDebug = console.debug;
                console.debug = function() {
                    // Intercept specific debug calls that might be used for bot detection
                    if (arguments.length > 0 && 
                        (arguments[0].includes('bot') || arguments[0].includes('automation'))) {
                        return;
                    }
                    return originalDebug.apply(this, arguments);
                };
                
                // Override notification permission for Yelp
                Object.defineProperty(Notification, 'permission', {
                    get: () => 'default'
                });
                
                // Add touch support that Yelp may check for
                window.ontouchstart = true;
                
                // Fix missing properties that Yelp sometimes checks
                if (!window.screenX) window.screenX = 0;
                if (!window.screenY) window.screenY = 0;
                if (!window.outerWidth) window.outerWidth = window.innerWidth;
                if (!window.outerHeight) window.outerHeight = window.innerHeight;
            }
        """)
    
    async def _apply_webgl_vendor_override(self, page):
        """Apply WebGL vendor and renderer override.
        
        Args:
            page: Puppeteer page object.
        """
        # Apply consistent WebGL vendor and renderer info to avoid fingerprinting
        script = f"""
            () => {{
                // Override WebGL vendor and renderer
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // UNMASKED_VENDOR_WEBGL
                    if (parameter === 37445) {{
                        return '{self.webgl_vendor}';
                    }}
                    // UNMASKED_RENDERER_WEBGL
                    if (parameter === 37446) {{
                        return '{self.webgl_renderer}';
                    }}
                    return getParameter.apply(this, arguments);
                }};
            }}
        """
        await page.evaluateOnNewDocument(script)
    
    async def _apply_navigator_hardware_override(self, page):
        """Apply navigator hardware concurrency and memory override.
        
        Args:
            page: Puppeteer page object.
        """
        # Generate reasonable values
        hardware_concurrency = random.randint(4, 16)
        device_memory = random.choice([4, 8, 16])
        
        script = f"""
            () => {{
                // Override hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {hardware_concurrency}
                }});
                
                // Override device memory
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {device_memory}
                }});
            }}
        """
        await page.evaluateOnNewDocument(script)
    
    async def _apply_chrome_runtime_override(self, page):
        """Apply Chrome runtime override.
        
        Args:
            page: Puppeteer page object.
        """
        await page.evaluateOnNewDocument("""
            () => {
                // Add chrome object if it doesn't exist
                if (!window.chrome) {
                    window.chrome = {};
                }
                
                // Add runtime if it doesn't exist
                if (!window.chrome.runtime) {
                    window.chrome.runtime = {};
                    
                    // Add sendMessage function
                    window.chrome.runtime.sendMessage = function() {
                        return {
                            then: function() {
                                return {
                                    catch: function() {}
                                };
                            }
                        };
                    };
                }
            }
        """)
    
    async def _apply_permissions_override(self, page):
        """Apply Permissions API override.
        
        Args:
            page: Puppeteer page object.
        """
        await page.evaluateOnNewDocument("""
            () => {
                // Override permissions API
                if (window.Permissions && window.Permissions.prototype.query) {
                    const originalQuery = window.Permissions.prototype.query;
                    window.Permissions.prototype.query = function(parameters) {
                        return Promise.resolve({
                            state: "granted",
                            onchange: null
                        });
                    };
                }
            }
        """)
    
    async def _simulate_mouse_movements(self, page):
        """Simulate realistic mouse movements on the page.
        
        Args:
            page: Puppeteer page object.
        """
        # Get page dimensions
        dimensions = await page.evaluate("""
            () => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                };
            }
        """)
        
        width = dimensions['width']
        height = dimensions['height']
        
        # Generate a random number of mouse movements (3-7)
        num_movements = random.randint(3, 7)
        
        for _ in range(num_movements):
            # Generate random coordinates
            x = random.randint(0, width)
            y = random.randint(0, height)
            
            # Move mouse with random duration
            await page.mouse.move(x, y, {'steps': random.randint(10, 25)})
            
            # Random pause between movements
            await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def _simulate_initial_scroll(self, page):
        """Simulate initial scrolling behavior.
        
        Args:
            page: Puppeteer page object.
        """
        # Scroll down a bit
        scroll_amount = random.randint(100, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Maybe scroll back up slightly
        if random.random() < 0.3:  # 30% chance
            up_amount = random.randint(50, 150)
            await page.evaluate(f"window.scrollBy(0, -{up_amount})")
            await asyncio.sleep(random.uniform(0.2, 0.7))
    
    async def _simulate_tripadvisor_browsing(self, page):
        """Simulate TripAdvisor-specific browsing behavior.
        
        Args:
            page: Puppeteer page object.
        """
        # Check if there are photos to hover over
        photo_count = await page.evaluate("""
            () => {
                const photos = document.querySelectorAll('.ppr_priv_resp_photo_carousel img');
                return photos.length;
            }
        """)
        
        if photo_count > 0:
            # Hover over a random photo
            photo_index = random.randint(0, photo_count - 1)
            photo_selector = f'.ppr_priv_resp_photo_carousel img:nth-child({photo_index + 1})'
            
            try:
                await page.hover(photo_selector)
                await asyncio.sleep(random.uniform(0.5, 1.5))
            except Exception:
                pass
    
    async def _simulate_google_browsing(self, page):
        """Simulate Google-specific browsing behavior.
        
        Args:
            page: Puppeteer page object.
        """
        # Maybe click on a category tab in Google Maps
        category_count = await page.evaluate("""
            () => {
                const categories = document.querySelectorAll('div[role="tablist"] button');
                return categories.length;
            }
        """)
        
        if category_count > 0 and random.random() < 0.3:  # 30% chance
            category_index = random.randint(0, category_count - 1)
            await page.evaluate(f"""
                () => {{
                    const categories = document.querySelectorAll('div[role="tablist"] button');
                    if (categories[{category_index}]) {{
                        categories[{category_index}].click();
                    }}
                }}
            """)
            await asyncio.sleep(random.uniform(1.0, 2.0))
    
    async def _simulate_yelp_browsing(self, page):
        """Simulate Yelp-specific browsing behavior.
        
        Args:
            page: Puppeteer page object.
        """
        # Maybe hover over a rating or business photo
        elements_to_hover = await page.evaluate("""
            () => {
                const ratings = document.querySelectorAll('.i-stars');
                const photos = document.querySelectorAll('.photo-box img');
                return ratings.length + photos.length;
            }
        """)
        
        if elements_to_hover > 0 and random.random() < 0.5:  # 50% chance
            # Try to hover over a rating
            try:
                await page.hover('.i-stars')
                await asyncio.sleep(random.uniform(0.5, 1.0))
            except Exception:
                # Try to hover over a photo instead
                try:
                    await page.hover('.photo-box img')
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                except Exception:
                    pass


async def apply_stealth_measures(page, platform="general"):
    """Apply stealth measures to a page to avoid bot detection.
    
    Args:
        page: Puppeteer page object.
        platform (str, optional): The platform to optimize for. Defaults to "general".
            Options: "general", "tripadvisor", "google", "yelp"
    """
    enhancer = StealthEnhancer(platform)
    await enhancer.enhance_browser(page)
    return enhancer
