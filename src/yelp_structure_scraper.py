#!/usr/bin/env python3
"""
Yelp Reviews Scraper with Structure Support

This module scrapes reviews from Yelp using the structure files for dynamic selectors
and anti-bot patterns. It builds on the original Yelp scraper but uses the new
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

class YelpStructureScraper:
    """Scraper for Yelp reviews using structure files."""
    
    def __init__(self, config_path: str = "config.yaml", config_dict: Dict = None):
        """Initialize the Yelp structure-based review scraper.
        
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
        self.url = self.config.get("yelp_url", "")
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
        self.structure_loaded = self.structure_manager.load_structure("yelp")
        
        # Check if structure needs update
        self.structure_needs_update = (
            not self.structure_loaded or
            self.structure_manager.structure_needs_update("yelp")
        )
        
        # Output settings
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
        logger.info(f"Initialized Yelp structure scraper for {self.restaurant_name}")
        if self.structure_loaded:
            logger.info("Yelp structure loaded successfully")
        else:
            logger.warning("Yelp structure not loaded, using fallback selectors")
    
    async def init_browser(self) -> None:
        """Initialize the browser session with Puppeteer."""
        logger.info("Initializing browser session for Yelp scraping")
        
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
                platform_specific = self.structure_manager.structures["yelp"].get("platform_specific", {}).get("yelp", {})
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
                self.stealth_enhancer = await apply_stealth_measures(self.page, "yelp")
                
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
            fingerprinting = self.structure_manager.structures["yelp"].get("fingerprinting", {})
            
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
                    }}
                """)
                
            # Apply connection properties if specified
            connection_properties = fingerprinting.get("connection_properties", {})
            if connection_properties and connection_properties.get("enabled", False):
                effective_type = connection_properties.get("effective_type", "4g")
                
                # Handle downlink and RTT ranges
                downlink_range = connection_properties.get("downlink_range", [8, 20])
                rtt_range = connection_properties.get("rtt_range", [40, 100])
                
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
                
            logger.info("Applied fingerprinting settings from structure file")
                
        except Exception as e:
            logger.warning(f"Error applying structure fingerprinting: {e}")
    
    async def scrape_reviews(self) -> List[Dict[str, Any]]:
        """Scrape reviews from Yelp using structure-based selectors.
        
        Returns:
            List[Dict[str, Any]]: List of scraped reviews.
        """
        logger.info(f"Starting to scrape Yelp reviews for {self.restaurant_name}")
        reviews = []
        
        try:
            # Check if structure file is loaded
            if not self.structure_loaded and self.structure_needs_update:
                logger.warning("Yelp structure not loaded or needs update")
                logger.info("Using default selectors")
            
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Navigate to the Yelp page
            logger.info(f"Navigating to {self.url}")
            await self.page.goto(self.url, {"waitUntil": "networkidle0"})
            
            # Apply human-like behavior if enabled
            if self.simulate_human and self.stealth_enhancer:
                await self._simulate_human_behavior()
            
            # Wait for reviews to load
            await async_delay_between_actions("waiting")
            
            # Handle cookie consent if present
            await self._handle_cookie_consent()
            
            # Apply IP rotation evasion techniques if specified in structure file
            if self.structure_loaded:
                platform_specific = self.structure_manager.structures["yelp"].get("platform_specific", {}).get("yelp", {})
                avoidance_techniques = platform_specific.get("avoidance_techniques", [])
                
                if "ip_rotation_on_block" in avoidance_techniques:
                    logger.info("IP rotation on block detection enabled")
            
            # Collect reviews
            page_num = 0
            retry_count = 0
            
            while len(reviews) < self.max_reviews and retry_count < self.retry_attempts:
                try:
                    # Get reviews from current page
                    page_reviews = await self._extract_reviews_from_page()
                    
                    if page_reviews:
                        reviews.extend(page_reviews)
                        retry_count = 0  # Reset retry count
                        
                        # Log progress
                        logger.info(f"Collected {len(reviews)} reviews so far")
                        
                        # Stop if we've collected enough reviews
                        if len(reviews) >= self.max_reviews:
                            break
                        
                        # Apply human-like behavior between pages
                        if self.simulate_human and self.stealth_enhancer:
                            await self._simulate_human_behavior()
                        
                        # Navigate to next page
                        has_next_page = await self._go_to_next_page()
                        if not has_next_page:
                            logger.info("No more pages available")
                            break
                        
                        page_num += 1
                        logger.info(f"Navigated to page {page_num + 1}")
                        
                        # Apply delay between page navigations
                        await async_delay_between_actions("navigation")
                        
                    else:
                        # No reviews on this page
                        retry_count += 1
                        logger.warning(f"No reviews found on page {page_num + 1}, retry {retry_count}/{self.retry_attempts}")
                        
                        if retry_count >= self.retry_attempts:
                            logger.warning(f"Max retry attempts ({self.retry_attempts}) reached. Stopping.")
                            break
                        
                        # Wait a bit longer before retrying
                        await async_delay_between_actions("waiting")
                
                except Exception as e:
                    # Check for CAPTCHA or rate limiting
                    if await self._check_for_captcha() or await self._check_for_rate_limiting():
                        logger.warning("Anti-bot measures detected, stopping scraping")
                        if self.structure_loaded:
                            platform_specific = self.structure_manager.structures["yelp"].get("platform_specific", {}).get("yelp", {})
                            avoidance_techniques = platform_specific.get("avoidance_techniques", [])
                            
                            if "reset_cookies_on_captcha" in avoidance_techniques:
                                logger.info("Attempting to reset cookies and retry")
                                await self._clear_cookies()
                                # Wait longer before retrying
                                await asyncio.sleep(30)
                                retry_count += 1
                                continue
                        break
                    else:
                        # Regular error, log and continue
                        logger.error(f"Error scraping page: {e}")
                        retry_count += 1
                        continue
            
            # Filter reviews by date if date range is specified
            if self.date_range:
                reviews = self._filter_reviews_by_date(reviews)
            
            # Save to CSV
            self._save_to_csv(reviews)
            
            logger.info(f"Successfully scraped {len(reviews)} Yelp reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Yelp reviews: {e}", exc_info=True)
            # Take a screenshot to help with debugging
            if self.page:
                await take_screenshot(self.page, "yelp_scraper_error.png")
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
                behavior_patterns = self.structure_manager.structures["yelp"].get("behavior_patterns", {})
                
                if behavior_patterns:
                    # Initial wait
                    initial_wait = behavior_patterns.get("initial_wait", {})
                    if initial_wait:
                        base_time = initial_wait.get("base_time", 3000) / 1000
                        variance = initial_wait.get("variance", 800) / 1000
                        
                        import random
                        wait_time = base_time + random.uniform(-variance, variance)
                        await asyncio.sleep(max(0.1, wait_time))
                    
                    # Scroll pattern
                    scroll_pattern = behavior_patterns.get("scroll_pattern", {})
                    if scroll_pattern:
                        # Initial scroll
                        initial_scroll = scroll_pattern.get("initial_scroll", {})
                        if initial_scroll:
                            pixels = initial_scroll.get("pixels", 300)
                            variance = initial_scroll.get("variance", 100)
                            
                            scroll_pixels = pixels + random.randint(-variance, variance)
                            await self.page.evaluate(f"window.scrollBy(0, {scroll_pixels})")
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Review scroll
                        review_scroll = scroll_pattern.get("review_scroll", {})
                        if review_scroll and random.random() < review_scroll.get("probability", 0.85):
                            pixels = review_scroll.get("pixels", 250)
                            variance = review_scroll.get("variance", 80)
                            
                            scroll_pixels = pixels + random.randint(-variance, variance)
                            await self.page.evaluate(f"window.scrollBy(0, {scroll_pixels})")
                            await asyncio.sleep(random.uniform(0.5, 1.2))
                        
                        # Occasional up scroll
                        up_scroll = scroll_pattern.get("occasional_up_scroll", {})
                        if up_scroll and random.random() < up_scroll.get("probability", 0.25):
                            pixels = up_scroll.get("pixels", 80)
                            variance = up_scroll.get("variance", 40)
                            
                            scroll_pixels = pixels + random.randint(-variance, variance)
                            await self.page.evaluate(f"window.scrollBy(0, -{scroll_pixels})")
                            await asyncio.sleep(random.uniform(0.3, 0.8))
                        
                        # Pause after scrolling
                        pause_after = scroll_pattern.get("pause_after_scroll", {})
                        if pause_after:
                            base_time = pause_after.get("base_time", 1200) / 1000
                            variance = pause_after.get("variance", 500) / 1000
                            
                            pause_time = base_time + random.uniform(-variance, variance)
                            await asyncio.sleep(max(0.1, pause_time))
                    
                    # Hover behaviors
                    hover_behaviors = behavior_patterns.get("hover_behaviors", {})
                    
                    # Photo hover
                    photo_hover = hover_behaviors.get("photo_hover", {})
                    if photo_hover and random.random() < photo_hover.get("probability", 0.4):
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
                                        base_time = duration.get("base_time", 1500) / 1000
                                        variance = duration.get("variance", 500) / 1000
                                        
                                        hover_time = base_time + random.uniform(-variance, variance)
                                        await asyncio.sleep(max(0.1, hover_time))
                                        break
                                except Exception:
                                    continue
                    
                    # Rating hover
                    rating_hover = hover_behaviors.get("rating_hover", {})
                    if rating_hover and random.random() < rating_hover.get("probability", 0.3):
                        selectors = rating_hover.get("selectors", [])
                        if selectors:
                            # Try to hover over a rating
                            for selector in selectors:
                                try:
                                    elements = await self.page.querySelectorAll(selector)
                                    if elements and len(elements) > 0:
                                        # Choose a random element
                                        element = elements[random.randint(0, len(elements) - 1)]
                                        await element.hover()
                                        
                                        # Wait for hover duration
                                        duration = rating_hover.get("duration", {})
                                        base_time = duration.get("base_time", 800) / 1000
                                        variance = duration.get("variance", 300) / 1000
                                        
                                        hover_time = base_time + random.uniform(-variance, variance)
                                        await asyncio.sleep(max(0.1, hover_time))
                                        break
                                except Exception:
                                    continue
                    
                    # Reviewer hover
                    reviewer_hover = hover_behaviors.get("reviewer_hover", {})
                    if reviewer_hover and random.random() < reviewer_hover.get("probability", 0.2):
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
                                        base_time = duration.get("base_time", 1000) / 1000
                                        variance = duration.get("variance", 400) / 1000
                                        
                                        hover_time = base_time + random.uniform(-variance, variance)
                                        await asyncio.sleep(max(0.1, hover_time))
                                        break
                                except Exception:
                                    continue
                    
                    # Page interaction behaviors
                    page_interaction = behavior_patterns.get("page_interaction", {})
                    if page_interaction:
                        # Read time simulation
                        read_time = page_interaction.get("read_time", {})
                        if read_time:
                            base_time = read_time.get("base_time", 8000) / 1000
                            variance = read_time.get("variance", 3000) / 1000
                            
                            wait_time = base_time + random.uniform(-variance, variance)
                            # Only apply a shorter version of the read time to keep scraping efficient
                            await asyncio.sleep(min(3.0, wait_time))
                        
                        # Random click on neutral areas
                        random_clicks = page_interaction.get("random_clicks", {})
                        if random_clicks and random_clicks.get("enabled", True) and random.random() < random_clicks.get("probability", 0.15):
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
                                                await asyncio.sleep(random.uniform(0.5, 1.5))
                                                break
                                    except Exception:
                                        continue
            
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    async def _handle_cookie_consent(self) -> None:
        """Handle cookie consent dialog if present."""
        try:
            # Get selectors from structure file if available
            selectors = []
            
            if self.structure_loaded:
                cookie_consent = self.structure_manager.get_anti_bot_pattern(
                    "yelp", "cookie_consent", {}
                )
                
                if cookie_consent and "selectors" in cookie_consent:
                    selectors = cookie_consent["selectors"]
                    wait_after = cookie_consent.get("wait_after", 1500) / 1000
                else:
                    # Fallback to default selectors
                    selectors = [
                        'button[id*="cookie-policy"]',
                        'button[class*="cookie-consent"]',
                        'div[role="dialog"] button',
                        '#yscp-btn-accept',
                        'button.yscp-button'
                    ]
                    wait_after = 1.5
            else:
                # Fallback to default selectors
                selectors = [
                    'button[id*="cookie-policy"]',
                    'button[class*="cookie-consent"]',
                    'div[role="dialog"] button',
                    '#yscp-btn-accept',
                    'button.yscp-button'
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
                    "yelp", "popups", {}
                )
                
                if popups and "selectors" in popups:
                    selectors = popups["selectors"]
                    wait_after = popups.get("wait_after", 1000) / 1000
                else:
                    # Fallback to default selectors
                    selectors = [
                        '.close-modal-button',
                        'button[aria-label="Close"]',
                        '.modal__09f24__q8I3M button',
                        'button[data-tracking-label="modal-close"]'
                    ]
                    wait_after = 1.0
            else:
                # Fallback to default selectors
                selectors = [
                    '.close-modal-button',
                    'button[aria-label="Close"]',
                    '.modal__09f24__q8I3M button',
                    'button[data-tracking-label="modal-close"]'
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
    
    async def _handle_login_prompt(self) -> None:
        """Handle login prompts that may appear during scraping."""
        try:
            # Get selectors from structure file if available
            selectors = []
            
            if self.structure_loaded:
                login_prompt = self.structure_manager.get_anti_bot_pattern(
                    "yelp", "login_prompt", {}
                )
                
                if login_prompt and "selectors" in login_prompt:
                    selectors = login_prompt["selectors"]
                    wait_after = login_prompt.get("wait_after", 1000) / 1000
                else:
                    # Fallback to default selectors
                    selectors = [
                        '.auth-close-button',
                        '.signup-close',
                        'button.dismiss-link'
                    ]
                    wait_after = 1.0
            else:
                # Fallback to default selectors
                selectors = [
                    '.auth-close-button',
                    '.signup-close',
                    'button.dismiss-link'
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
                        logger.info(f"Closing login prompt: {selector}")
                        await self.page.click(selector)
                        await asyncio.sleep(wait_after)
                        return
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error handling login prompt: {e}")
    
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
                    "yelp", "captcha_indicators", {}
                )
                
                if captcha_indicators:
                    indicators = captcha_indicators
            else:
                # Fallback to default indicators
                indicators = {
                    "selectors": [
                        "iframe[src*=\"recaptcha\"]",
                        "iframe[src*=\"captcha\"]",
                        "form[action*=\"captcha\"]",
                        "div.g-recaptcha",
                        "div[class*=\"captcha\"]",
                        "div[data-sitekey]"
                    ],
                    "text_patterns": [
                        "security check",
                        "verify you are human",
                        "captcha",
                        "suspicious activity",
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
                    "yelp", "rate_limiting", {}
                )
                
                if rate_limiting:
                    indicators = rate_limiting
            else:
                # Fallback to default indicators
                indicators = {
                    "selectors": [
                        ".distil-alert",
                        "#distil_identify_block",
                        "div[data-component=\"distil-identification\"]"
                    ],
                    "text_patterns": [
                        "unusual activity",
                        "access denied",
                        "too many requests",
                        "rate limited"
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
            
            # Check response status
            response = await self.page.evaluate("() => ({ status: window.performance.getEntriesByType('navigation')[0]?.responseStatus || 200 })")
            if response["status"] in [403, 429]:
                logger.warning(f"Rate limiting detected: HTTP status {response['status']}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for rate limiting: {e}")
            return False
    
    async def _clear_cookies(self) -> None:
        """Clear all cookies to potentially bypass rate limiting."""
        try:
            if self.page:
                # Get all cookies
                cookies = await self.page.cookies()
                
                # Clear all cookies
                await self.page.deleteCookie(*cookies)
                
                logger.info(f"Cleared {len(cookies)} cookies")
        except Exception as e:
            logger.warning(f"Error clearing cookies: {e}")
    
    async def _extract_reviews_from_page(self) -> List[Dict[str, Any]]:
        """Extract reviews from the current page.
        
        Returns:
            List[Dict[str, Any]]: List of reviews from the current page.
        """
        page_reviews = []
        
        try:
            logger.info("Extracting reviews from current page")
            
            # Handle any popups or login prompts that might interfere with scraping
            await self._handle_popups()
            await self._handle_login_prompt()
            
            # Expand "more" links in reviews
            await self._expand_review_texts()
            
            # Get selectors from structure file if available
            review_container = []
            reviewer_name = []
            rating = []
            date = []
            review_text = []
            rating_extractor = []
            date_cleanup_patterns = []
            
            if self.structure_loaded:
                review_container = self.structure_manager.get_selector("yelp", "reviewContainer", [])
                if isinstance(review_container, str):
                    review_container = [review_container]
                
                reviewer_name = self.structure_manager.get_selector("yelp", "reviewerName", [])
                if isinstance(reviewer_name, str):
                    reviewer_name = [reviewer_name]
                
                rating = self.structure_manager.get_selector("yelp", "rating", [])
                if isinstance(rating, str):
                    rating = [rating]
                
                rating_extractor = self.structure_manager.get_selector("yelp", "ratingExtractor", [])
                
                date = self.structure_manager.get_selector("yelp", "date", [])
                if isinstance(date, str):
                    date = [date]
                
                date_cleanup_patterns = self.structure_manager.get_selector("yelp", "dateCleanupPatterns", [])
                
                review_text = self.structure_manager.get_selector("yelp", "reviewText", [])
                if isinstance(review_text, str):
                    review_text = [review_text]
            
            # Fallback to default selectors if needed
            if not review_container:
                review_container = ["div.review", "li.review", "div[data-review-id]"]
            
            if not reviewer_name:
                reviewer_name = [".user-passport-info .css-166la90", ".user-passport-info .user-display-name", "a.user-name"]
            
            if not rating:
                rating = ["div[aria-label*=\"star rating\"]", "div.i-stars", ".rating-large"]
            
            if not rating_extractor:
                rating_extractor = [
                    {
                        "type": "ariaLabel",
                        "pattern": "(\\d+(\\.\\d+)?)",
                        "attribute": "aria-label"
                    },
                    {
                        "type": "classPattern",
                        "pattern": "i-stars--([0-9]+)",
                        "divisor": 10
                    }
                ]
            
            if not date:
                date = [".review-content .rating-qualifier", "span.rating-qualifier", ".review-content span.subtle"]
            
            if not date_cleanup_patterns:
                date_cleanup_patterns = [
                    {"pattern": "Updated.*$", "replacement": ""},
                    {"pattern": "Photos from.*$", "replacement": ""}
                ]
            
            if not review_text:
                review_text = ["p.comment__09f24__D0cxf", ".review-content p", ".review-content .lemon--p__373c0__3Qnnj"]
            
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
                    
                    // Rating extractors
                    const ratingExtractors = {json.dumps(rating_extractor)};
                    
                    // Date cleanup patterns
                    const dateCleanupPatterns = {json.dumps(date_cleanup_patterns)};
                    
                    // Process each review
                    reviewElements.forEach(review => {{
                        try {{
                            // Get reviewer name
                            let reviewerName = '';
                            for (const selector of reviewerNameSelectors) {{
                                const nameElement = review.querySelector(selector);
                                if (nameElement) {{
                                    reviewerName = nameElement.textContent.trim();
                                    break;
                                }}
                            }}
                            
                            // Get rating
                            let rating = 0;
                            for (const selector of ratingSelectors) {{
                                const ratingElement = review.querySelector(selector);
                                if (ratingElement) {{
                                    // Try each extractor
                                    for (const extractor of ratingExtractors) {{
                                        if (extractor.type === "ariaLabel") {{
                                            const ariaLabel = ratingElement.getAttribute(extractor.attribute || 'aria-label');
                                            if (ariaLabel) {{
                                                const ratingMatch = ariaLabel.match(new RegExp(extractor.pattern));
                                                if (ratingMatch) {{
                                                    rating = parseFloat(ratingMatch[1]);
                                                    break;
                                                }}
                                            }}
                                        }} else if (extractor.type === "classPattern") {{
                                            const ratingClass = ratingElement.className;
                                            const ratingMatch = ratingClass.match(new RegExp(extractor.pattern));
                                            if (ratingMatch) {{
                                                rating = parseInt(ratingMatch[1]) / (extractor.divisor || 1);
                                                break;
                                            }}
                                        }}
                                    }}
                                    
                                    if (rating > 0) {{
                                        break;
                                    }}
                                }}
                            }}
                            
                            // Get date
                            let dateText = '';
                            for (const selector of dateSelectors) {{
                                const dateElement = review.querySelector(selector);
                                if (dateElement) {{
                                    dateText = dateElement.textContent.trim();
                                    break;
                                }}
                            }}
                            
                            // Clean up date
                            for (const pattern of dateCleanupPatterns) {{
                                dateText = dateText.replace(new RegExp(pattern.pattern), pattern.replacement);
                            }}
                            
                            // Get review text
                            let reviewText = '';
                            for (const selector of reviewTextSelectors) {{
                                const textElement = review.querySelector(selector);
                                if (textElement) {{
                                    reviewText = textElement.textContent.trim();
                                    break;
                                }}
                            }}
                            
                            // Add to reviews array
                            reviews.push({{
                                reviewer_name: reviewerName,
                                rating: rating,
                                date: dateText.trim(),
                                text: reviewText
                            }});
                        }} catch (e) {{
                            console.error('Error extracting review:', e);
                        }}
                    }});
                    
                    return reviews;
                }}
            """
            
            # Extract reviews
            reviews_data = await self.page.evaluate(js_code)
            
            # Process the reviews
            for review_data in reviews_data:
                # Create review object
                review = {
                    "platform": "Yelp",
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
                
                # Add to reviews list if it has meaningful content
                if review["text"] and review["reviewer_name"]:
                    page_reviews.append(review)
            
            logger.info(f"Extracted {len(page_reviews)} reviews from current page")
            
        except Exception as e:
            logger.error(f"Error extracting reviews from page: {e}", exc_info=True)
        
        return page_reviews
    
    async def _expand_review_texts(self) -> None:
        """Expand truncated review texts by clicking 'More' buttons."""
        try:
            # Get selectors from structure file if available
            expand_button_selectors = []
            batch_size = 2
            delay_between = {"base_time": 2000, "variance": 800}
            
            if self.structure_loaded:
                expand_button = self.structure_manager.get_selector("yelp", "expandButton", [])
                if isinstance(expand_button, list) and expand_button:
                    expand_button_selectors = expand_button
                elif isinstance(expand_button, str):
                    expand_button_selectors = [expand_button]
                
                # Get behavior pattern for expand reviews
                expand_reviews = self.structure_manager.get_behavior_pattern(
                    "yelp", "expand_reviews", {}
                )
                
                if expand_reviews:
                    batch_size = expand_reviews.get("batch_size", 2)
                    delay_between = expand_reviews.get("delay_between", {
                        "base_time": 2000,
                        "variance": 800
                    })
            
            if not expand_button_selectors:
                # Fallback to default selectors
                expand_button_selectors = [
                    'a.js-content-expander',
                    'span.js-expander-link',
                    'button[data-tracking-label="read-more"]'
                ]
            
            # Try multiple approaches to expand reviews
            
            # Method 1: Find all expandable hidden content
            expandable_content = await self.page.querySelectorAll('span.js-content-toggleable.hidden')
            if expandable_content and len(expandable_content) > 0:
                logger.info(f"Found {len(expandable_content)} expandable reviews (method 1)")
                
                # Click all expander links
                for selector in expand_button_selectors:
                    try:
                        await self.page.evaluate(f"""
                            () => {{
                                document.querySelectorAll('{selector}').forEach(button => {{
                                    if (button.textContent.toLowerCase().includes('more')) {{
                                        button.click();
                                    }}
                                }});
                            }}
                        """)
                        
                        # Wait after expanding
                        import random
                        base_time = delay_between.get("base_time", 2000) / 1000
                        variance = delay_between.get("variance", 800) / 1000
                        await asyncio.sleep(base_time + random.uniform(-variance, variance))
                        break
                    except Exception:
                        continue
            
            # Method 2: Find and click "more" buttons directly
            else:
                for selector in expand_button_selectors:
                    try:
                        buttons = await self.page.querySelectorAll(selector)
                        if buttons and len(buttons) > 0:
                            logger.info(f"Found {len(buttons)} expand buttons (method 2)")
                            
                            # Process in batches
                            import random
                            for i in range(0, len(buttons), batch_size):
                                batch = buttons[i:i+batch_size]
                                
                                for button in batch:
                                    try:
                                        # Check if the button is for expanding review
                                        button_text = await self.page.evaluate('(element) => element.textContent.toLowerCase()', button)
                                        if 'more' in button_text:
                                            await button.click()
                                            
                                            # Wait after click with random delay
                                            base_time = delay_between.get("base_time", 2000) / 1000 / 2  # Shorter delay for individual clicks
                                            variance = delay_between.get("variance", 800) / 1000 / 2
                                            await asyncio.sleep(max(0.1, base_time + random.uniform(-variance, variance)))
                                    except Exception:
                                        continue
                                
                                # Wait between batches
                                await async_delay_between_actions("waiting")
                            
                            # Success with this selector
                            break
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.warning(f"Error expanding review texts: {e}")
    
    async def _go_to_next_page(self) -> bool:
        """Navigate to the next page of reviews.
        
        Returns:
            bool: True if successfully navigated to next page, False otherwise.
        """
        try:
            # Get selectors from structure file if available
            next_button_selectors = []
            
            if self.structure_loaded:
                next_page_button = self.structure_manager.get_selector("yelp", "nextPageButton", [])
                if isinstance(next_page_button, list) and next_page_button:
                    next_button_selectors = next_page_button
                elif isinstance(next_page_button, str):
                    next_button_selectors = [next_page_button]
            
            if not next_button_selectors:
                # Fallback to default selectors
                next_button_selectors = [
                    'a.next-link',
                    'a[class*="next"]',
                    'a.u-decoration-none.next',
                    '.pagination-links a[class*="next"]'
                ]
            
            # Try each selector
            for selector in next_button_selectors:
                try:
                    next_button = await self.page.querySelector(selector)
                    
                    if next_button:
                        # Check if disabled
                        is_disabled = await self.page.evaluate("""
                            (element) => {
                                return element.classList.contains('disabled') || 
                                       element.parentElement.classList.contains('disabled') ||
                                       !element.href;
                            }
                        """, next_button)
                        
                        if not is_disabled:
                            # Click the next button
                            await next_button.click()
                            
                            # Wait for page to load
                            await self.page.waitForNavigation({"waitUntil": "networkidle0"})
                            
                            return True
                except Exception:
                    continue
            
            # Try to find the "More Reviews" button
            more_reviews_selectors = []
            
            if self.structure_loaded:
                more_reviews_button = self.structure_manager.get_selector("yelp", "moreReviewsButton", [])
                if isinstance(more_reviews_button, list) and more_reviews_button:
                    more_reviews_selectors = more_reviews_button
                elif isinstance(more_reviews_button, str):
                    more_reviews_selectors = [more_reviews_button]
            
            if not more_reviews_selectors:
                more_reviews_selectors = [
                    'button.more-reviews',
                    'a.more-reviews',
                    'button[data-tracking-label="more-reviews"]'
                ]
            
            # Try each "More Reviews" selector
            for selector in more_reviews_selectors:
                try:
                    more_button = await self.page.querySelector(selector)
                    
                    if more_button:
                        # Click the button
                        await more_button.click()
                        
                        # Wait for content to load
                        await asyncio.sleep(2)
                        
                        return True
                except Exception:
                    continue
            
            logger.info("No next page button found or it's disabled")
            return False
            
        except Exception as e:
            logger.warning(f"Error navigating to next page: {e}")
            return False
    
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
    """Run the Yelp structure-based review scraper."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    
    try:
        # Create scraper
        scraper = YelpStructureScraper()
        
        # Run scraper
        reviews = loop.run_until_complete(scraper.scrape_reviews())
        
        print(f"Successfully scraped {len(reviews)} Yelp reviews")
        return reviews
        
    except Exception as e:
        logger.error(f"Error running Yelp structure scraper: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    run_scraper()
