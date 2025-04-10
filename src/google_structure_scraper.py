#!/usr/bin/env python3
"""
Google Reviews Scraper with Structure Support

This module scrapes reviews from Google Maps using the structure files for dynamic selectors
and anti-bot patterns. It builds on the original Google scraper but uses the new
structure management system for increased resilience to website changes.
"""

import os
import logging
import asyncio
import json
import yaml
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Import utility modules
from src.utils import (
    create_browser_session, 
    close_browser_session, 
    take_screenshot, 
    save_html,
    parse_date, 
    standardize_date_format,
    apply_stealth_measures,
    delay_between_actions, 
    async_delay_between_actions,
    simulate_human_typing
)

# Import structure manager
from src.utils.structure_analyzer import StructureManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleStructureScraper:
    """Scraper for Google Reviews using structure files."""
    
    def __init__(self, config_path: str = "config.yaml", config_dict: Dict = None):
        """Initialize the Google structure-based review scraper.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                Defaults to "config.yaml".
            config_dict (Dict, optional): Configuration dictionary.
                If provided, overrides loading from config_path.
        """
        # Load configuration
        if config_dict:
            self.config = config_dict
        else:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            
        # Initialize browser session variables
        self.browser = None
        self.page = None
        self.stealth_enhancer = None
        
        # Get scraping parameters
        self.url = self.config.get("google_url", "")
        self.restaurant_name = self.config.get("restaurant_name", "")
        self.date_range = self.config.get("date_range", {})
        self.max_reviews = self.config.get("max_reviews_per_platform", 100)
        self.timeout = self.config.get("timeout_seconds", 60)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        
        # Set up anti-bot measures
        self.anti_bot_settings = self.config.get("anti_bot_settings", {})
        self.use_delays = self.anti_bot_settings.get("enable_random_delays", True)
        self.use_stealth = self.anti_bot_settings.get("enable_stealth_plugins", True)
        self.headless = self.anti_bot_settings.get("headless_mode", False)
        self.simulate_human = self.anti_bot_settings.get("simulate_human_behavior", True)
        
        # Initialize structure manager
        self.structure_manager = StructureManager()
        
        # Load structure data
        self.structure_loaded = self.structure_manager.load_structure("google")
        
        # Check if structure needs update
        self.structure_needs_update = (
            not self.structure_loaded or
            self.structure_manager.structure_needs_update("google")
        )
        
        # Output settings
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
        logger.info(f"Initialized Google structure scraper for {self.restaurant_name}")
        if self.structure_loaded:
            logger.info("Google structure loaded successfully")
        else:
            logger.warning("Google structure not loaded, using fallback selectors")
    
    async def init_browser(self) -> None:
        """Initialize the browser session with Puppeteer."""
        logger.info("Initializing browser session for Google scraping")
        
        try:
            # Configure browser options
            browser_options = {
                "headless": self.headless,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1280,800"
                ]
            }
            
            # Add any platform-specific options from structure file
            if self.structure_loaded:
                platform_specific = self.structure_manager.structures["google"].get("platform_specific", {}).get("google", {})
                if platform_specific:
                    if platform_specific.get("random_viewport_size", False):
                        import random
                        width = random.randint(1024, 1920)
                        height = random.randint(768, 1080)
                        browser_options["args"].append(f"--window-size={width},{height}")
            
            # Create browser session
            self.browser, self.page = create_browser_session(browser_options)
            
            # Apply stealth measures if enabled
            if self.use_stealth:
                self.stealth_enhancer = await apply_stealth_measures(self.page, "google")
                
                # Apply additional fingerprinting from structure file if available
                if self.structure_loaded:
                    await self._apply_structure_fingerprinting()
            
            # Set page timeout
            await self.page.setDefaultTimeout(self.timeout * 1000)  # Convert to milliseconds
            
            logger.info("Browser session initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing browser: {e}", exc_info=True)
            if self.browser:
                await close_browser_session(self.browser)
                self.browser = None
                self.page = None
            raise
    
    async def _apply_structure_fingerprinting(self) -> None:
        """Apply fingerprinting settings from structure file."""
        try:
            # Get fingerprinting settings
            fingerprinting = self.structure_manager.structures["google"].get("fingerprinting", {})
            
            if not fingerprinting:
                return
                
            # Apply WebGL vendor and renderer
            webgl_vendors = fingerprinting.get("webgl_vendors", [])
            webgl_renderers = fingerprinting.get("webgl_renderers", [])
            
            if webgl_vendors and webgl_renderers:
                import random
                webgl_vendor = random.choice(webgl_vendors)
                webgl_renderer = random.choice(webgl_renderers)
                
                await self.page.evaluateOnNewDocument(f"""
                    () => {{
                        const getParameter = WebGLRenderingContext.prototype.getParameter;
                        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                            // UNMASKED_VENDOR_WEBGL
                            if (parameter === 37445) {{
                                return '{webgl_vendor}';
                            }}
                            // UNMASKED_RENDERER_WEBGL
                            if (parameter === 37446) {{
                                return '{webgl_renderer}';
                            }}
                            return getParameter.apply(this, arguments);
                        }};
                    }}
                """)
            
            # Apply navigator overrides
            navigator_overrides = fingerprinting.get("navigator_overrides", {})
            if navigator_overrides:
                languages = navigator_overrides.get("languages", ["en-US", "en"])
                plugins_length = navigator_overrides.get("plugins_length", 3)
                vendor = navigator_overrides.get("vendor", "Google Inc.")
                
                # Handle hardware concurrency
                hw_concurrency = "undefined"
                hw_concurrency_config = navigator_overrides.get("hardwareConcurrency", {})
                if hw_concurrency_config:
                    min_val = hw_concurrency_config.get("min", 4)
                    max_val = hw_concurrency_config.get("max", 16)
                    hw_concurrency = random.randint(min_val, max_val)
                
                # Handle device memory
                device_memory = "undefined"
                device_memory_config = navigator_overrides.get("deviceMemory", {})
                if device_memory_config:
                    options = device_memory_config.get("options", [4, 8, 16])
                    if options:
                        device_memory = random.choice(options)
                
                await self.page.evaluateOnNewDocument(f"""
                    () => {{
                        // Override languages
                        Object.defineProperty(navigator, 'languages', {{
                            get: () => {json.dumps(languages)}
                        }});
                        
                        // Override plugins length
                        if (navigator.plugins) {{
                            Object.defineProperty(navigator, 'plugins', {{
                                get: () => {{
                                    return {{ length: {plugins_length} }};
                                }}
                            }});
                        }}
                        
                        // Override vendor
                        Object.defineProperty(navigator, 'vendor', {{
                            get: () => '{vendor}'
                        }});
                        
                        // Override hardwareConcurrency if specified
                        if ({hw_concurrency} !== undefined) {{
                            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                                get: () => {hw_concurrency}
                            }});
                        }}
                        
                        // Override deviceMemory if specified
                        if ({device_memory} !== undefined) {{
                            Object.defineProperty(navigator, 'deviceMemory', {{
                                get: () => {device_memory}
                            }});
                        }}
                    }}
                """)
            
            # Apply special properties
            special_properties = fingerprinting.get("special_properties", {})
            if special_properties:
                webdriver = "false" if not special_properties.get("webdriver", False) else "true"
                chrome_automation = "false" if not special_properties.get("chrome_automation", False) else "true"
                
                # Handle permission overrides
                permission_overrides = special_properties.get("permission_overrides", {})
                permission_json = json.dumps(permission_overrides)
                
                await self.page.evaluateOnNewDocument(f"""
                    () => {{
                        // Override webdriver
                        Object.defineProperty(navigator, 'webdriver', {{
                            get: () => {webdriver}
                        }});
                        
                        // Override automation
                        Object.defineProperty(window, 'chrome', {{
                            get: () => {{
                                if (!{chrome_automation} && window.chrome) {{
                                    // Remove automation properties
                                    if (window.chrome.runtime) {{
                                        window.chrome.runtime.getManifest = undefined;
                                    }}
                                }}
                                return window.chrome;
                            }}
                        }});
                        
                        // Override permission API if available
                        if (navigator.permissions) {{
                            const originalQuery = navigator.permissions.query;
                            navigator.permissions.query = function(parameters) {{
                                const permissionOverrides = {permission_json};
                                if (parameters.name in permissionOverrides) {{
                                    return Promise.resolve({{ state: permissionOverrides[parameters.name] }});
                                }}
                                return originalQuery.call(this, parameters);
                            }};
                        }}
                    }}
                """)
                
            # Apply connection properties if specified
            connection_properties = fingerprinting.get("connection_properties", {})
            if connection_properties and connection_properties.get("enabled", False):
                effective_type = connection_properties.get("effective_type", "4g")
                
                # Handle downlink and RTT ranges
                downlink_range = connection_properties.get("downlink_range", [10, 25])
                rtt_range = connection_properties.get("rtt_range", [30, 80])
                
                downlink = random.uniform(downlink_range[0], downlink_range[1])
                rtt = random.randint(rtt_range[0], rtt_range[1])
                
                await self.page.evaluateOnNewDocument(f"""
                    () => {{
                        // Override connection information
                        if (navigator.connection) {{
                            Object.defineProperties(navigator.connection, {{
                                'effectiveType': {{
                                    get: () => '{effective_type}'
                                }},
                                'downlink': {{
                                    get: () => {downlink}
                                }},
                                'rtt': {{
                                    get: () => {rtt}
                                }}
                            }});
                        }}
                    }}
                """)
                
            # Apply screen properties if specified
            screen_properties = fingerprinting.get("screen_properties", {})
            if screen_properties and screen_properties.get("randomize", False):
                width_range = screen_properties.get("width_range", [1280, 1920])
                height_range = screen_properties.get("height_range", [800, 1080])
                color_depth = screen_properties.get("color_depth", 24)
                pixel_ratio_range = screen_properties.get("pixel_ratio", [1, 2])
                
                width = random.randint(width_range[0], width_range[1])
                height = random.randint(height_range[0], height_range[1])
                pixel_ratio = random.choice([1, 1.5, 2]) if pixel_ratio_range else 1
                
                await self.page.evaluateOnNewDocument(f"""
                    () => {{
                        // Override screen properties
                        Object.defineProperties(screen, {{
                            'width': {{ get: () => {width} }},
                            'height': {{ get: () => {height} }},
                            'availWidth': {{ get: () => {width} }},
                            'availHeight': {{ get: () => {height - 40} }},
                            'colorDepth': {{ get: () => {color_depth} }},
                            'pixelDepth': {{ get: () => {color_depth} }}
                        }});
                        
                        // Override devicePixelRatio
                        Object.defineProperty(window, 'devicePixelRatio', {{
                            get: () => {pixel_ratio}
                        }});
                    }}
                """)
                
            # Apply Google Maps specific evasion if enabled
            platform_specific = self.structure_manager.structures["google"].get("platform_specific", {}).get("google", {})
            if platform_specific and platform_specific.get("maps_api_detection_evasion", False):
                await self.page.evaluateOnNewDocument("""
                    () => {
                        // Override maps-related detection mechanisms
                        if (window.google && window.google.maps) {
                            const originalLoad = window.google.maps.Load;
                            window.google.maps.Load = function() {
                                // Add a small random delay to simulate real user
                                setTimeout(() => {
                                    originalLoad.apply(this, arguments);
                                }, Math.floor(Math.random() * 100) + 50);
                            };
                        }
                        
                        // Randomize unique identifiers that Maps might use
                        const randomId = Math.random().toString(36).substring(2, 15);
                        localStorage.setItem('google_maps_pref', randomId);
                    }
                """)
                
            logger.info("Applied fingerprinting settings from structure file")
                
        except Exception as e:
            logger.warning(f"Error applying structure fingerprinting: {e}")
    
    async def scrape_reviews(self) -> List[Dict[str, Any]]:
        """Scrape reviews from Google Maps using structure-based selectors.
        
        Returns:
            List[Dict[str, Any]]: List of scraped reviews.
        """
        logger.info(f"Starting to scrape Google reviews for {self.restaurant_name}")
        reviews = []
        
        try:
            # Check if structure file is loaded
            if not self.structure_loaded and self.structure_needs_update:
                logger.warning("Google structure not loaded or needs update")
                logger.info("Using default selectors")
            
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Navigate to the Google Maps page
            logger.info(f"Navigating to {self.url}")
            await self.page.goto(self.url, {"waitUntil": "networkidle0"})
            
            # Apply human-like behavior if enabled
            if self.simulate_human and self.stealth_enhancer:
                await self._simulate_human_behavior()
            
            # Wait for reviews to load
            await async_delay_between_actions("waiting")
            
            # Handle cookie consent if present
            await self._handle_cookie_consent()
            
            # Find reviews section
            reviews_section = await self._find_reviews_section()
            if not reviews_section:
                logger.warning("Reviews section not found, looking for reviews tab to click")
                
                # Try to click on the reviews tab
                if not await self._click_reviews_tab():
                    logger.warning("Could not find reviews tab")
                    
                    # Take a screenshot for debugging
                    await take_screenshot(self.page, "google_reviews_tab_not_found.png")
                    
                    # One more attempt to find reviews after a longer wait
                    await asyncio.sleep(5)
                    reviews_section = await self._find_reviews_section()
                    
                    if not reviews_section:
                        logger.error("Could not find reviews section after multiple attempts")
                        return []
            
            # Check if reviews need to be expanded
            await self._expand_review_texts()
            
            # Scroll to load more reviews
            await self._scroll_to_load_reviews()
            
            # Extract reviews
            page_reviews = await self._extract_reviews_from_page()
            if page_reviews:
                reviews.extend(page_reviews)
                logger.info(f"Extracted {len(page_reviews)} reviews")
            
            # Filter reviews by date if date range is specified
            if self.date_range:
                reviews = self._filter_reviews_by_date(reviews)
            
            # Save to CSV
            self._save_to_csv(reviews)
            
            logger.info(f"Successfully scraped {len(reviews)} Google reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Google reviews: {e}", exc_info=True)
            # Take a screenshot to help with debugging
            if self.page:
                await take_screenshot(self.page, "google_scraper_error.png")
            return []
            
        finally:
            # Close browser
            if self.browser:
                await close_browser_session(self.browser)
                self.browser = None
                self.page = None
    
    async def _simulate_human_behavior(self) -> None:
        """Simulate human-like behavior based on structure patterns."""
        try:
            # Basic behavior from stealth enhancer
            if self.stealth_enhancer:
                await self.stealth_enhancer.simulate_human_behavior(self.page)
            
            # Additional behaviors from structure file if available
            if self.structure_loaded:
                behavior_patterns = self.structure_manager.structures["google"].get("behavior_patterns", {})
                
                if behavior_patterns:
                    # Initial wait
                    initial_wait = behavior_patterns.get("initial_wait", {})
                    if initial_wait:
                        base_time = initial_wait.get("base_time", 2500) / 1000
                        variance = initial_wait.get("variance", 700) / 1000
                        
                        import random
                        wait_time = base_time + random.uniform(-variance, variance)
                        await asyncio.sleep(max(0.5, wait_time))
                    
                    # Scroll pattern
                    scroll_pattern = behavior_patterns.get("scroll_pattern", {})
                    if scroll_pattern:
                        # Initial scroll
                        initial_scroll = scroll_pattern.get("initial_scroll", {})
                        if initial_scroll:
                            pixels = initial_scroll.get("pixels", 250)
                            variance = initial_scroll.get("variance", 50)
                            
                            scroll_pixels = pixels + random.randint(-variance, variance)
                            await self.page.evaluate(f"window.scrollBy(0, {scroll_pixels})")
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Occasional up scroll
                        up_scroll = scroll_pattern.get("occasional_up_scroll", {})
                        if up_scroll and random.random() < up_scroll.get("probability", 0.15):
                            pixels = up_scroll.get("pixels", 60)
                            variance = up_scroll.get("variance", 30)
                            
                            scroll_pixels = pixels + random.randint(-variance, variance)
                            await self.page.evaluate(f"window.scrollBy(0, -{scroll_pixels})")
                            await asyncio.sleep(random.uniform(0.3, 0.8))
                        
                        # Pause after scrolling
                        pause_after = scroll_pattern.get("pause_after_scroll", {})
                        if pause_after:
                            base_time = pause_after.get("base_time", 1000) / 1000
                            variance = pause_after.get("variance", 400) / 1000
                            
                            pause_time = base_time + random.uniform(-variance, variance)
                            await asyncio.sleep(max(0.3, pause_time))
                    
                    # Hover behaviors
                    hover_behaviors = behavior_patterns.get("hover_behaviors", {})
                    
                    # Photo hover
                    photo_hover = hover_behaviors.get("photo_hover", {})
                    if photo_hover and random.random() < photo_hover.get("probability", 0.3):
                        selectors = photo_hover.get("selectors", [])
                        if selectors:
                            # Try to hover over a photo
                            for selector in selectors:
                                try:
                                    elements = await self.page.querySelectorAll(selector)
                                    if elements and len(elements) > 0:
                                        # Choose a random element
                                        element = elements[random.randint(0, len(elements) - 1)]
                                        await element.hover()
                                        
                                        # Wait for hover duration
                                        duration = photo_hover.get("duration", {})
                                        base_time = duration.get("base_time", 1200) / 1000
                                        variance = duration.get("variance", 400) / 1000
                                        
                                        hover_time = base_time + random.uniform(-variance, variance)
                                        await asyncio.sleep(max(0.3, hover_time))
                                        break
                                except Exception:
                                    continue
                    
                    # Reviewer hover
                    reviewer_hover = hover_behaviors.get("reviewer_hover", {})
                    if reviewer_hover and random.random() < reviewer_hover.get("probability", 0.25):
                        selectors = reviewer_hover.get("selectors", [])
                        if selectors:
                            # Try to hover over a reviewer name
                            for selector in selectors:
                                try:
                                    elements = await self.page.querySelectorAll(selector)
                                    if elements and len(elements) > 0:
                                        # Choose a random element
                                        element = elements[random.randint(0, len(elements) - 1)]
                                        await element.hover()
                                        
                                        # Wait for hover duration
                                        duration = reviewer_hover.get("duration", {})
                                        base_time = duration.get("base_time", 900) / 1000
                                        variance = duration.get("variance", 300) / 1000
                                        
                                        hover_time = base_time + random.uniform(-variance, variance)
                                        await asyncio.sleep(max(0.3, hover_time))
                                        break
                                except Exception:
                                    continue
                    
                    # Page interaction behaviors
                    page_interaction = behavior_patterns.get("page_interaction", {})
                    if page_interaction:
                        # Random clicks on neutral areas
                        random_clicks = page_interaction.get("random_clicks", {})
                        if random_clicks and random_clicks.get("enabled", True) and random.random() < random_clicks.get("probability", 0.1):
                            neutral_areas = random_clicks.get("neutral_areas", [])
                            if neutral_areas:
                                for selector in neutral_areas:
                                    try:
                                        elements = await self.page.querySelectorAll(selector)
                                        if elements and len(elements) > 0:
                                            # Choose a random element
                                            element = elements[random.randint(0, len(elements) - 1)]
                                            
                                            # Get element dimensions
                                            dimensions = await self.page.evaluate("""
                                                (element) => {
                                                    const rect = element.getBoundingClientRect();
                                                    return {
                                                        left: rect.left,
                                                        top: rect.top,
                                                        width: rect.width,
                                                        height: rect.height
                                                    };
                                                }
                                            """, element)
                                            
                                            # Click at a random position within the element
                                            if dimensions and dimensions["width"] > 0 and dimensions["height"] > 0:
                                                x = dimensions["left"] + random.uniform(10, dimensions["width"] - 10)
                                                y = dimensions["top"] + random.uniform(10, dimensions["height"] - 10)
                                                
                                                await self.page.mouse.click(x, y)
                                                await asyncio.sleep(random.uniform(0.3, 0.8))
                                                break
                                    except Exception:
                                        continue
                                        
                    # Google Maps specific behaviors
                    platform_specific = self.structure_manager.structures["google"].get("platform_specific", {}).get("google", {})
                    if platform_specific and platform_specific.get("simulate_map_interaction", False) and random.random() < 0.3:
                        try:
                            # Try to interact with the map
                            zoom_levels = platform_specific.get("zoom_levels", [15, 16, 17, 18])
                            if zoom_levels and random.random() < 0.2:
                                # Simulate zooming
                                zoom_level = random.choice(zoom_levels)
                                await self.page.evaluate(f"""
                                    () => {{
                                        if (window.google && window.google.maps) {{
                                            const map = document.querySelector('[role="application"]');
                                            if (map) {{
                                                // Simulate zoom button click
                                                const zoomIn = document.querySelector('button[jsaction*="zoom.in"]');
                                                const zoomOut = document.querySelector('button[jsaction*="zoom.out"]');
                                                
                                                if (Math.random() < 0.5 && zoomIn) {{
                                                    zoomIn.click();
                                                }} else if (zoomOut) {{
                                                    zoomOut.click();
                                                }}
                                            }}
                                        }}
                                    }}
                                """)
                                await asyncio.sleep(random.uniform(0.5, 1.5))
                            
                            # Simulate panning
                            if random.random() < platform_specific.get("pan_probabilities", 0.2):
                                await self.page.evaluate("""
                                    () => {
                                        const map = document.querySelector('[role="application"]');
                                        if (map) {
                                            // Get map dimensions
                                            const rect = map.getBoundingClientRect();
                                            const centerX = rect.left + rect.width / 2;
                                            const centerY = rect.top + rect.height / 2;
                                            
                                            // Simulate mouse events for dragging
                                            const event = new MouseEvent('mousedown', {
                                                bubbles: true,
                                                cancelable: true,
                                                clientX: centerX,
                                                clientY: centerY
                                            });
                                            map.dispatchEvent(event);
                                        }
                                    }
                                """)
                                
                                # Small delay
                                await asyncio.sleep(0.1)
                                
                                # Move mouse slightly to simulate drag
                                await self.page.mouse.move(
                                    random.randint(-50, 50), 
                                    random.randint(-50, 50), 
                                    {"steps": 5}
                                )
                                
                                # Mouse up to end the drag
                                await self.page.mouse.up()
                                await asyncio.sleep(random.uniform(0.5, 1.0))
                        except Exception as e:
                            logger.debug(f"Error simulating map interaction: {e}")
                            
            
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    async def _handle_cookie_consent(self) -> None:
        """Handle cookie consent dialog if present."""
        try:
            # Get selectors from structure file if available
            selectors = []
            
            if self.structure_loaded:
                cookie_consent = self.structure_manager.get_anti_bot_pattern(
                    "google", "cookie_consent", {}
                )
                
                if cookie_consent and "selectors" in cookie_consent:
                    selectors = cookie_consent["selectors"]
                    wait_after = cookie_consent.get("wait_after", 1500) / 1000
                else:
                    # Fallback to default selectors
                    selectors = [
                        'button#L2AGLb',
                        'div.VDity button',
                        'button[aria-label="Accept all"]',
                        'button.tHlp8d'
                    ]
                    wait_after = 1.5
            else:
                # Fallback to default selectors
                selectors = [
                    'button#L2AGLb',
                    'div.VDity button',
                    'button[aria-label="Accept all"]',
                    'button.tHlp8d'
                ]
                wait_after = 1.5
            
            for selector in selectors:
                try:
                    is_visible = await self.page.evaluate(f"""
                        () => {{
                            const element = document.querySelector('{selector}');
                            if (element) {{
                                const style = window.getComputedStyle(element);
                                return style.display !== 'none' && style.visibility !== 'hidden';
                            }}
                            return false;
                        }}
                    """)
                    
                    if is_visible:
                        logger.info(f"Clicking cookie consent button: {selector}")
                        await self.page.click(selector)
                        await asyncio.sleep(wait_after)
                        return
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error handling cookie consent: {e}")
    
    async def _handle_popups(self) -> None:
        """Handle any popups that appear during scraping."""
        try:
            # Get selectors from structure file if available
            selectors = []
            
            if self.structure_loaded:
                popups = self.structure_manager.get_anti_bot_pattern(
                    "google", "popups", {}
                )
                
                if popups and "selectors" in popups:
                    selectors = popups["selectors"]
                    wait_after = popups.get("wait_after", 1000) / 1000
                else:
                    # Fallback to default selectors
                    selectors = [
                        'button[aria-label="Close"]',
                        '.close-button',
                        '.dismissButton',
                        '.overlay-close-button'
                    ]
                    wait_after = 1.0
            else:
                # Fallback to default selectors
                selectors = [
                    'button[aria-label="Close"]',
                    '.close-button',
                    '.dismissButton',
                    '.overlay-close-button'
                ]
                wait_after = 1.0
            
            for selector in selectors:
                try:
                    is_visible = await self.page.evaluate(f"""
                        () => {{
                            const element = document.querySelector('{selector}');
                            if (element) {{
                                const style = window.getComputedStyle(element);
                                return style.display !== 'none' && style.visibility !== 'hidden';
                            }}
                            return false;
                        }}
                    """)
                    
                    if is_visible:
                        logger.info(f"Closing popup: {selector}")
                        await self.page.click(selector)
                        await asyncio.sleep(wait_after)
                        return
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error handling popups: {e}")
    
    async def _find_reviews_section(self) -> Optional[Any]:
        """Find the reviews section on the page.
        
        Returns:
            Optional[Any]: The reviews section element or None if not found.
        """
        try:
            # Get selectors from structure file if available
            review_container_selectors = []
            
            if self.structure_loaded:
                review_container_selectors = self.structure_manager.get_selector(
                    "google", "reviewContainer", []
                )
                if isinstance(review_container_selectors, str):
                    review_container_selectors = [review_container_selectors]
            
            # Fallback to default selectors if needed
            if not review_container_selectors:
                review_container_selectors = [
                    'div[data-review-id]',
                    'div[role="listitem"]',
                    '.gws-localreviews__google-review'
                ]
            
            # Try each selector
            for selector in review_container_selectors:
                try:
                    elements = await self.page.querySelectorAll(selector)
                    if elements and len(elements) > 0:
                        logger.info(f"Found reviews section with selector: {selector}, found {len(elements)} reviews")
                        # Return the first element as a sample
                        return elements[0]
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding reviews section: {e}")
            return None
    
    async def _click_reviews_tab(self) -> bool:
        """Click on the reviews tab to show reviews.
        
        Returns:
            bool: True if clicked successfully, False otherwise.
        """
        try:
            # Get selectors from structure file if available
            reviews_tab_selectors = []
            
            if self.structure_loaded:
                reviews_tab_selectors = self.structure_manager.get_selector(
                    "google", "reviewsTab", []
                )
                if isinstance(reviews_tab_selectors, str):
                    reviews_tab_selectors = [reviews_tab_selectors]
            
            # Fallback to default selectors if needed
            if not reviews_tab_selectors:
                reviews_tab_selectors = [
                    'button[jsaction*="pane.rating.moreReviews"]',
                    'a[href*="#lrd="]',
                    'div[data-tab="reviews"]',
                    'button[aria-label*="reviews"]'
                ]
            
            # Try each selector
            for selector in reviews_tab_selectors:
                try:
                    element = await self.page.querySelector(selector)
                    if element:
                        logger.info(f"Clicking reviews tab with selector: {selector}")
                        await element.click()
                        await asyncio.sleep(3)  # Wait for reviews to load
                        return True
                except Exception:
                    continue
            
            # Try clicking on the rating stars as a fallback
            try:
                rating_selector = 'span[role="img"][aria-label*="star"]'
                rating_element = await self.page.querySelector(rating_selector)
                if rating_element:
                    logger.info("Clicking on rating stars as fallback")
                    await rating_element.click()
                    await asyncio.sleep(3)
                    return True
            except Exception:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Error clicking reviews tab: {e}")
            return False
    
    async def _check_for_captcha(self) -> bool:
        """Check if a CAPTCHA is present on the page.
        
        Returns:
            bool: True if CAPTCHA is detected, False otherwise.
        """
        try:
            # Get CAPTCHA indicators from structure file if available
            indicators = {"selectors": [], "text_patterns": []}
            
            if self.structure_loaded:
                captcha_indicators = self.structure_manager.get_anti_bot_pattern(
                    "google", "captcha_indicators", {}
                )
                
                if captcha_indicators:
                    indicators = captcha_indicators
            else:
                # Fallback to default indicators
                indicators = {
                    "selectors": [
                        "iframe[src*=\"recaptcha\"]",
                        "div.g-recaptcha",
                        "form#captcha-form",
                        "div#captcha",
                        "input[name=\"g-recaptcha-response\"]"
                    ],
                    "text_patterns": [
                        "verify you're a human",
                        "confirm you're not a robot",
                        "security check",
                        "unusual traffic"
                    ]
                }
            
            # Check selectors
            for selector in indicators["selectors"]:
                try:
                    element = await self.page.querySelector(selector)
                    if element:
                        logger.warning(f"CAPTCHA detected: {selector}")
                        return True
                except Exception:
                    continue
            
            # Check text patterns
            page_text = await self.page.evaluate("() => document.body.innerText.toLowerCase()")
            for pattern in indicators["text_patterns"]:
                if pattern.lower() in page_text:
                    logger.warning(f"CAPTCHA detected: text contains '{pattern}'")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for CAPTCHA: {e}")
            return False
    
    async def _check_for_rate_limiting(self) -> bool:
        """Check if rate limiting is in effect.
        
        Returns:
            bool: True if rate limiting is detected, False otherwise.
        """
        try:
            # Get rate limiting indicators from structure file if available
            indicators = {"selectors": [], "text_patterns": []}
            
            if self.structure_loaded:
                rate_limiting = self.structure_manager.get_anti_bot_pattern(
                    "google", "rate_limiting", {}
                )
                
                if rate_limiting:
                    indicators = rate_limiting
            else:
                # Fallback to default indicators
                indicators = {
                    "selectors": [
                        ".error-code-widget",
                        "div[jscontroller=\"R9Ulx\"]",
                        "div[jsaction*=\"errorPage\"]"
                    ],
                    "text_patterns": [
                        "too many requests",
                        "unusual traffic from your computer network",
                        "your computer or network may be sending automated queries",
                        "try again later"
                    ]
                }
            
            # Check selectors
            for selector in indicators["selectors"]:
                try:
                    element = await self.page.querySelector(selector)
                    if element:
                        logger.warning(f"Rate limiting detected: {selector}")
                        return True
                except Exception:
                    continue
            
            # Check text patterns
            page_text = await self.page.evaluate("() => document.body.innerText.toLowerCase()")
            for pattern in indicators["text_patterns"]:
                if pattern.lower() in page_text:
                    logger.warning(f"Rate limiting detected: text contains '{pattern}'")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for rate limiting: {e}")
            return False
    
    async def _clear_cookies(self) -> None:
        """Clear cookies to bypass rate limiting or CAPTCHA."""
        try:
            cookies = await self.page.cookies()
            if cookies:
                await self.page.deleteCookie(*cookies)
                logger.info(f"Cleared {len(cookies)} cookies")
        except Exception as e:
            logger.warning(f"Error clearing cookies: {e}")
    
    async def _expand_review_texts(self) -> None:
        """Expand truncated review texts by clicking 'More' buttons."""
        try:
            # Get selectors from structure file if available
            expand_button_selectors = []
            batch_size = 3
            delay_between = {"base_time": 1300, "variance": 400}
            
            if self.structure_loaded:
                expand_button = self.structure_manager.get_selector("google", "expandButton", [])
                if isinstance(expand_button, list) and expand_button:
                    expand_button_selectors = expand_button
                elif isinstance(expand_button, str):
                    expand_button_selectors = [expand_button]
                
                # Get behavior pattern for expand reviews
                expand_reviews = self.structure_manager.get_behavior_pattern(
                    "google", "expand_reviews", {}
                )
                
                if expand_reviews:
                    batch_size = expand_reviews.get("batch_size", 3)
                    delay_between = expand_reviews.get("delay_between", {
                        "base_time": 1300,
                        "variance": 400
                    })
            
            if not expand_button_selectors:
                # Fallback to default selectors
                expand_button_selectors = [
                    '.w8nwRe button',
                    'button[jsaction*="pane.review.expandReview"]',
                    '.review-more-link',
                    'span[jsaction*="pane.review.expandReview"]'
                ]
            
            # Process each selector
            for selector in expand_button_selectors:
                try:
                    buttons = await self.page.querySelectorAll(selector)
                    if buttons and len(buttons) > 0:
                        logger.info(f"Found {len(buttons)} expand buttons with selector: {selector}")
                        
                        # Process in batches
                        import random
                        for i in range(0, len(buttons), batch_size):
                            batch = buttons[i:i+batch_size]
                            
                            for button in batch:
                                try:
                                    # Check if the button is still in the DOM and visible
                                    is_visible = await self.page.evaluate("""
                                        (element) => {
                                            if (!element.isConnected) return false;
                                            const style = window.getComputedStyle(element);
                                            return style.display !== 'none' && style.visibility !== 'hidden';
                                        }
                                    """, button)
                                    
                                    if is_visible:
                                        await button.click()
                                        
                                        # Wait after click with random delay
                                        base_time = delay_between.get("base_time", 1300) / 1000 / 2  # Shorter delay for individual clicks
                                        variance = delay_between.get("variance", 400) / 1000 / 2
                                        await asyncio.sleep(max(0.2, base_time + random.uniform(-variance, variance)))
                                except Exception:
                                    continue
                            
                            # Wait between batches
                            await async_delay_between_actions("waiting")
                        
                        # Success with this selector, no need to try others
                        return
                except Exception:
                    continue
                        
        except Exception as e:
            logger.warning(f"Error expanding review texts: {e}")
    
    async def _scroll_to_load_reviews(self) -> None:
        """Scroll through reviews to load more."""
        try:
            # Get scroll settings from structure file if available
            max_scrolls = 15
            scroll_increment = 300
            wait_after_scroll = {"base_time": 1500, "variance": 500}
            detect_changes = None
            
            if self.structure_loaded:
                scroll_pattern = self.structure_manager.get_behavior_pattern(
                    "google", "scroll_pattern", {}
                )
                if scroll_pattern:
                    max_scrolls = scroll_pattern.get("max_scrolls", 15)
                
                infinite_scroll = self.structure_manager.get_behavior_pattern(
                    "google", "infinite_scroll_handling", {}
                )
                if infinite_scroll and infinite_scroll.get("enabled", True):
                    scroll_increment = infinite_scroll.get("scroll_increment", 300)
                    wait_after_scroll = infinite_scroll.get("wait_after_scroll", {
                        "base_time": 1500,
                        "variance": 500
                    })
                    detect_changes = infinite_scroll.get("detect_changes", None)
            
            # Get scroll container selectors from structure file if available
            scroll_container_selectors = []
            if self.structure_loaded:
                scroll_container_selectors = self.structure_manager.get_selector(
                    "google", "reviewScrollContainer", []
                )
                if isinstance(scroll_container_selectors, str):
                    scroll_container_selectors = [scroll_container_selectors]
            
            # Fallback to default selectors
            if not scroll_container_selectors:
                scroll_container_selectors = [
                    'div[role="feed"]',
                    '.review-dialog-list',
                    '.section-scrollbox'
                ]
            
            # Initialize tracking variables
            previous_review_count = 0
            unchanged_scrolls = 0
            
            import random
            
            # Start scrolling
            logger.info(f"Starting to scroll for reviews (max {max_scrolls} scrolls)")
            for i in range(max_scrolls):
                # Try to scroll the review container
                scroll_success = False
                
                for selector in scroll_container_selectors:
                    scroll_success = await self.page.evaluate(f"""
                        () => {{
                            const container = document.querySelector('{selector}');
                            if (container) {{
                                container.scrollTop += {scroll_increment};
                                return true;
                            }}
                            return false;
                        }}
                    """)
                    
                    if scroll_success:
                        break
                
                # Fallback to window scroll if container scroll failed
                if not scroll_success:
                    await self.page.evaluate(f"window.scrollBy(0, {scroll_increment})")
                    scroll_success = True
                
                # Wait after scroll
                base_time = wait_after_scroll.get("base_time", 1500) / 1000
                variance = wait_after_scroll.get("variance", 500) / 1000
                await asyncio.sleep(max(0.5, base_time + random.uniform(-variance, variance)))
                
                # Check for CAPTCHA after scroll
                if await self._check_for_captcha() or await self._check_for_rate_limiting():
                    logger.warning("Detected CAPTCHA or rate limiting during scrolling, stopping")
                    
                    # Try to apply evasion techniques if enabled
                    if self.structure_loaded:
                        platform_specific = self.structure_manager.structures["google"].get("platform_specific", {}).get("google", {})
                        if platform_specific:
                            avoidance_techniques = platform_specific.get("avoidance_techniques", [])
                            
                            if "reset_cookies_on_captcha" in avoidance_techniques:
                                logger.info("Attempting to clear cookies")
                                await self._clear_cookies()
                    
                    break
                
                # Check if we're making progress in loading new reviews
                if detect_changes:
                    detector_selector = detect_changes.get("selector", "div[role=\"listitem\"]")
                    elements = await self.page.querySelectorAll(detector_selector)
                    current_count = len(elements)
                    
                    if current_count == previous_review_count:
                        unchanged_scrolls += 1
                        if unchanged_scrolls >= detect_changes.get("max_unchanged_scrolls", 5):
                            logger.info(f"No new reviews loaded after {unchanged_scrolls} scrolls, stopping")
                            break
                    else:
                        unchanged_scrolls = 0
                        previous_review_count = current_count
                        logger.info(f"Found {current_count} reviews after {i+1} scrolls")
                
                # Apply human-like behavior occasionally
                if self.simulate_human and random.random() < 0.3:
                    await self._simulate_human_behavior()
            
            logger.info(f"Completed scrolling for reviews")
                
        except Exception as e:
            logger.warning(f"Error scrolling to load reviews: {e}")
    
    async def _extract_reviews_from_page(self) -> List[Dict[str, Any]]:
        """Extract reviews from the current page.
        
        Returns:
            List[Dict[str, Any]]: List of reviews from the current page.
        """
        page_reviews = []
        
        try:
            logger.info("Extracting reviews from current page")
            
            # Get selectors from structure file if available
            review_container = []
            reviewer_name = []
            rating = []
            date = []
            review_text = []
            rating_extractor = None
            date_cleanup_patterns = []
            
            if self.structure_loaded:
                review_container = self.structure_manager.get_selector("google", "reviewContainer", [])
                if isinstance(review_container, str):
                    review_container = [review_container]
                
                reviewer_name = self.structure_manager.get_selector("google", "reviewerName", [])
                if isinstance(reviewer_name, str):
                    reviewer_name = [reviewer_name]
                
                rating = self.structure_manager.get_selector("google", "rating", [])
                if isinstance(rating, str):
                    rating = [rating]
                
                rating_extractor = self.structure_manager.get_selector("google", "ratingExtractor", None)
                
                date = self.structure_manager.get_selector("google", "date", [])
                if isinstance(date, str):
                    date = [date]
                
                date_cleanup_patterns = self.structure_manager.get_selector("google", "dateCleanupPatterns", [])
                
                review_text = self.structure_manager.get_selector("google", "reviewText", [])
                if isinstance(review_text, str):
                    review_text = [review_text]
            
            # Fallback to default selectors if needed
            if not review_container:
                review_container = [
                    'div[data-review-id]',
                    'div[role="listitem"]',
                    '.gws-localreviews__google-review'
                ]
            
            if not reviewer_name:
                reviewer_name = [
                    '.d4r55',
                    '.y3Ibjb span',
                    '.DHIhE',
                    '.PiDzfc'
                ]
            
            if not rating:
                rating = [
                    'span[role="img"]',
                    'div[aria-label*="star"]',
                    'g-review-stars',
                    '.pw5pyd'
                ]
            
            if not rating_extractor:
                rating_extractor = {
                    "type": "ariaLabel",
                    "pattern": "(\\d+)",
                    "attribute": "aria-label"
                }
            
            if not date:
                date = [
                    '.rsqaWe',
                    '.y3Ibjb',
                    '.DU9Pgb',
                    '.dehysf'
                ]
            
            if not date_cleanup_patterns:
                date_cleanup_patterns = [
                    {"pattern": "^Reviewed\\s+", "replacement": ""},
                    {"pattern": "a\\s+\\w+\\s+ago", "replacement": ""}
                ]
            
            if not review_text:
                review_text = [
                    '.wiI7pd',
                    '.MyEned',
                    '.w8nwRe',
                    '.review-full-text'
                ]
            
            # Build JavaScript for extracting reviews
            js_code = f"""
                () => {{
                    const reviews = [];
                    
                    // Review container selectors
                    const reviewContainerSelectors = {json.dumps(review_container)};
                    let reviewElements = [];
                    
                    // Try each selector until we find reviews
                    for (const selector of reviewContainerSelectors) {{
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {{
                            reviewElements = elements;
                            console.log(`Found ${{elements.length}} reviews with selector: ${{selector}}`);
                            break;
                        }}
                    }}
                    
                    // Reviewer name selectors
                    const reviewerNameSelectors = {json.dumps(reviewer_name)};
                    
                    // Rating selectors
                    const ratingSelectors = {json.dumps(rating)};
                    
                    // Date selectors
                    const dateSelectors = {json.dumps(date)};
                    
                    // Review text selectors
                    const reviewTextSelectors = {json.dumps(review_text)};
                    
                    // Rating extractor
                    const ratingExtractor = {json.dumps(rating_extractor)};
                    
                    // Date cleanup patterns
                    const dateCleanupPatterns = {json.dumps(date_cleanup_patterns)};
                    
                    // Process each review
                    for (let i = 0; i < reviewElements.length; i++) {{
                        const review = reviewElements[i];
                        try {{
                            // Get reviewer name
                            let reviewerName = '';
                            for (const selector of reviewerNameSelectors) {{
                                try {{
                                    const nameElement = review.querySelector(selector);
                                    if (nameElement) {{
                                        reviewerName = nameElement.textContent.trim();
                                        break;
                                    }}
                                }} catch (e) {{
                                    // Continue to next selector
                                }}
                            }}
                            
                            // Get rating
                            let rating = 0;
                            for (const selector of ratingSelectors) {{
                                try {{
                                    const ratingElement = review.querySelector(selector);
                                    if (ratingElement) {{
                                        if (ratingExtractor.type === "ariaLabel") {{
                                            const ariaLabel = ratingElement.getAttribute(ratingExtractor.attribute || 'aria-label');
                                            if (ariaLabel) {{
                                                const ratingMatch = ariaLabel.match(new RegExp(ratingExtractor.pattern));
                                                if (ratingMatch) {{
                                                    rating = parseFloat(ratingMatch[1]);
                                                    break;
                                                }}
                                            }}
                                        }}
                                    }}
                                }} catch (e) {{
                                    // Continue to next selector
                                }}
                            }}
                            
                            // Get date
                            let dateText = '';
                            for (const selector of dateSelectors) {{
                                try {{
                                    const dateElement = review.querySelector(selector);
                                    if (dateElement) {{
                                        dateText = dateElement.textContent.trim();
                                        break;
                                    }}
                                }} catch (e) {{
                                    // Continue to next selector
                                }}
                            }}
                            
                            // Clean up date text using patterns
                            for (const pattern of dateCleanupPatterns) {{
                                dateText = dateText.replace(new RegExp(pattern.pattern), pattern.replacement);
                            }}
                            
                            // Get review text
                            let reviewText = '';
                            for (const selector of reviewTextSelectors) {{
                                try {{
                                    const textElement = review.querySelector(selector);
                                    if (textElement) {{
                                        reviewText = textElement.textContent.trim();
                                        break;
                                    }}
                                }} catch (e) {{
                                    // Continue to next selector
                                }}
                            }}
                            
                            // Add to reviews array if we have at least some data
                            if (reviewerName || rating || dateText || reviewText) {{
                                reviews.push({{
                                    reviewer_name: reviewerName,
                                    rating: rating,
                                    date: dateText,
                                    text: reviewText
                                }});
                            }}
                            
                        }} catch (e) {{
                            console.error(`Error extracting review ${{i}}: ${{e}}`);
                        }}
                    }}
                    
                    return reviews;
                }}
            """
            
            # Execute the extraction script
            reviews_data = await self.page.evaluate(js_code)
            
            # Process the reviews
            for review_data in reviews_data:
                # Create review object
                review = {
                    "platform": "Google",
                    "restaurant_name": self.restaurant_name,
                    "reviewer_name": review_data.get("reviewer_name", ""),
                    "rating": review_data.get("rating", 0),
                    "date": review_data.get("date", ""),
                    "text": review_data.get("text", ""),
                    # Additional fields that will be populated later
                    "standardized_date": "",
                    "category": "",
                    "sentiment": ""
                }
                
                # Standardize date
                date_obj = parse_date(review["date"])
                if date_obj:
                    review["standardized_date"] = standardize_date_format(date_obj)
                
                # Add to reviews list
                page_reviews.append(review)
            
            logger.info(f"Extracted {len(page_reviews)} reviews from current page")
            
        except Exception as e:
            logger.error(f"Error extracting reviews from page: {e}", exc_info=True)
        
        return page_reviews
    
    def _filter_reviews_by_date(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter reviews by date range.
        
        Args:
            reviews (List[Dict[str, Any]]): List of reviews.
            
        Returns:
            List[Dict[str, Any]]: Filtered reviews.
        """
        filtered_reviews = []
        
        # Get date range from config
        start_date_str = self.date_range.get("start", "")
        end_date_str = self.date_range.get("end", "")
        
        # Parse date range
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        
        # Apply filter
        for review in reviews:
            review_date_str = review.get("standardized_date", "")
            if not review_date_str:
                continue
                
            review_date = parse_date(review_date_str)
            if not review_date:
                continue
                
            # Check if within date range
            if start_date and review_date < start_date:
                continue
            if end_date and review_date > end_date:
                continue
                
            filtered_reviews.append(review)
        
        logger.info(f"Filtered reviews by date range: {len(filtered_reviews)} remaining")
        return filtered_reviews
    
    def _save_to_csv(self, reviews: List[Dict[str, Any]]) -> None:
        """Save reviews to a CSV file.
        
        Args:
            reviews (List[Dict[str, Any]]): List of reviews to save.
        """
        if not reviews:
            logger.warning("No reviews to save")
            return
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.csv_path)), exist_ok=True)
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(self.csv_path)
        
        # Define field names
        fieldnames = [
            "platform", "restaurant_name", "reviewer_name", 
            "rating", "date", "standardized_date", 
            "text", "category", "sentiment"
        ]
        
        # Write to CSV
        try:
            with open(self.csv_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Write headers if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                
                # Write reviews
                writer.writerows(reviews)
                
            logger.info(f"Successfully saved {len(reviews)} reviews to {self.csv_path}")
            
        except Exception as e:
            logger.error(f"Error saving reviews to CSV: {e}", exc_info=True)


def run_scraper():
    """Run the Google structure-based review scraper."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    
    try:
        # Create scraper
        scraper = GoogleStructureScraper()
        
        # Run scraper
        reviews = loop.run_until_complete(scraper.scrape_reviews())
        
        print(f"Successfully scraped {len(reviews)} Google reviews")
        return reviews
        
    except Exception as e:
        logger.error(f"Error running Google structure scraper: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    run_scraper()
