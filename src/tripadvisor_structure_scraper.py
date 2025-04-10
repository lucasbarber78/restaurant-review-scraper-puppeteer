#!/usr/bin/env python3
"""
TripAdvisor Reviews Scraper with Structure Support

This module scrapes reviews from TripAdvisor using the structure files for dynamic selectors
and anti-bot patterns. It builds on the original TripAdvisor scraper but uses the new
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

class TripAdvisorStructureScraper:
    """Scraper for TripAdvisor reviews using structure files."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the TripAdvisor structure-based review scraper.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                Defaults to "config.yaml".
        """
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        # Initialize browser session variables
        self.browser = None
        self.page = None
        self.stealth_enhancer = None
        
        # Get scraping parameters
        self.url = self.config.get("tripadvisor_url", "")
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
        self.structure_loaded = self.structure_manager.load_structure("tripadvisor")
        
        # Check if structure needs update
        self.structure_needs_update = (
            not self.structure_loaded or
            self.structure_manager.structure_needs_update("tripadvisor")
        )
        
        # Output settings
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
        logger.info(f"Initialized TripAdvisor structure scraper for {self.restaurant_name}")
        if self.structure_loaded:
            logger.info("TripAdvisor structure loaded successfully")
        else:
            logger.warning("TripAdvisor structure not loaded, using fallback selectors")
    
    async def init_browser(self) -> None:
        """Initialize the browser session with Puppeteer."""
        logger.info("Initializing browser session for TripAdvisor scraping")
        
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
            
            # Create browser session
            self.browser, self.page = create_browser_session(browser_options)
            
            # Apply stealth measures if enabled
            if self.use_stealth:
                self.stealth_enhancer = await apply_stealth_measures(self.page, "tripadvisor")
                
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
            fingerprinting = self.structure_manager.structures["tripadvisor"].get("fingerprinting", {})
            
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
                    }}
                """)
            
            # Apply special properties
            special_properties = fingerprinting.get("special_properties", {})
            if special_properties:
                webdriver = "false" if not special_properties.get("webdriver", False) else "true"
                chrome_automation = "false" if not special_properties.get("chrome_automation", False) else "true"
                
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
                
            logger.info("Applied fingerprinting settings from structure file")
                
        except Exception as e:
            logger.warning(f"Error applying structure fingerprinting: {e}")
    
    async def scrape_reviews(self) -> List[Dict[str, Any]]:
        """Scrape reviews from TripAdvisor using structure-based selectors.
        
        Returns:
            List[Dict[str, Any]]: List of scraped reviews.
        """
        logger.info(f"Starting to scrape TripAdvisor reviews for {self.restaurant_name}")
        reviews = []
        
        try:
            # Check if structure file is loaded
            if not self.structure_loaded and self.structure_needs_update:
                logger.warning("TripAdvisor structure not loaded or needs update")
                logger.info("Using default selectors")
            
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Navigate to the TripAdvisor page
            logger.info(f"Navigating to {self.url}")
            await self.page.goto(self.url, {"waitUntil": "networkidle0"})
            
            # Apply human-like behavior if enabled
            if self.simulate_human and self.stealth_enhancer:
                await self._simulate_human_behavior()
            
            # Wait for reviews to load
            await async_delay_between_actions("waiting")
            
            # Handle cookie consent if present
            await self._handle_cookie_consent()
            
            # Get total review count
            total_reviews = await self._get_total_review_count()
            logger.info(f"Found approximately {total_reviews} reviews")
            
            # Collect reviews
            page_num = 0
            reviews_to_collect = min(self.max_reviews, total_reviews)
            
            while len(reviews) < reviews_to_collect:
                # Get reviews from current page
                page_reviews = await self._extract_reviews_from_page()
                reviews.extend(page_reviews)
                
                # Stop if we've collected enough reviews
                if len(reviews) >= reviews_to_collect:
                    break
                
                # Navigate to next page
                has_next_page = await self._go_to_next_page()
                if not has_next_page:
                    break
                
                page_num += 1
                logger.info(f"Navigated to page {page_num + 1}")
                
                # Apply delay between page navigations
                await async_delay_between_actions("navigation")
                
                # Apply human-like behavior between pages
                if self.simulate_human and self.stealth_enhancer:
                    await self._simulate_human_behavior()
            
            # Filter reviews by date if date range is specified
            if self.date_range:
                reviews = self._filter_reviews_by_date(reviews)
            
            # Save to CSV
            self._save_to_csv(reviews)
            
            logger.info(f"Successfully scraped {len(reviews)} TripAdvisor reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping TripAdvisor reviews: {e}", exc_info=True)
            # Take a screenshot to help with debugging
            if self.page:
                await take_screenshot(self.page, "tripadvisor_scraper_error.png")
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
            await self.stealth_enhancer.simulate_human_behavior(self.page)
            
            # Additional behaviors from structure file if available
            if self.structure_loaded:
                behavior_patterns = self.structure_manager.structures["tripadvisor"].get("behavior_patterns", {})
                
                if behavior_patterns:
                    # Initial wait
                    initial_wait = behavior_patterns.get("initial_wait", {})
                    if initial_wait:
                        base_time = initial_wait.get("base_time", 2000) / 1000
                        variance = initial_wait.get("variance", 500) / 1000
                        
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
                        
                        # Occasional up scroll
                        up_scroll = scroll_pattern.get("occasional_up_scroll", {})
                        if up_scroll and random.random() < up_scroll.get("probability", 0.2):
                            pixels = up_scroll.get("pixels", 50)
                            variance = up_scroll.get("variance", 30)
                            
                            scroll_pixels = pixels + random.randint(-variance, variance)
                            await self.page.evaluate(f"window.scrollBy(0, -{scroll_pixels})")
                            await asyncio.sleep(random.uniform(0.2, 0.7))
                    
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
                                    element = await self.page.querySelector(selector)
                                    if element:
                                        await element.hover()
                                        
                                        # Wait for hover duration
                                        duration = photo_hover.get("duration", {})
                                        base_time = duration.get("base_time", 1200) / 1000
                                        variance = duration.get("variance", 400) / 1000
                                        
                                        hover_time = base_time + random.uniform(-variance, variance)
                                        await asyncio.sleep(max(0.1, hover_time))
                                        break
                                except Exception:
                                    continue
                    
                    # Rating hover
                    rating_hover = hover_behaviors.get("rating_hover", {})
                    if rating_hover and random.random() < rating_hover.get("probability", 0.2):
                        selectors = rating_hover.get("selectors", [])
                        if selectors:
                            # Try to hover over a rating
                            for selector in selectors:
                                try:
                                    element = await self.page.querySelector(selector)
                                    if element:
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
            
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    async def _handle_cookie_consent(self) -> None:
        """Handle cookie consent dialog if present."""
        try:
            # Get selectors from structure file if available
            selectors = []
            
            if self.structure_loaded:
                cookie_consent = self.structure_manager.get_anti_bot_pattern(
                    "tripadvisor", "cookie_consent", {}
                )
                
                if cookie_consent and "selectors" in cookie_consent:
                    selectors = cookie_consent["selectors"]
                    wait_after = cookie_consent.get("wait_after", 1500) / 1000
                else:
                    # Fallback to default selectors
                    selectors = [
                        'button#onetrust-accept-btn-handler',
                        'button[id*="accept"]',
                        'button[id*="cookie"]',
                        'button[class*="cookie"]',
                        'button[class*="accept"]',
                        '.evidon-banner-acceptbutton',
                        '#gdpr-consent-tool-wrapper button[type="submit"]'
                    ]
                    wait_after = 1.5
            else:
                # Fallback to default selectors
                selectors = [
                    'button#onetrust-accept-btn-handler',
                    'button[id*="accept"]',
                    'button[id*="cookie"]',
                    'button[class*="cookie"]',
                    'button[class*="accept"]',
                    '.evidon-banner-acceptbutton',
                    '#gdpr-consent-tool-wrapper button[type="submit"]'
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
    
    async def _get_total_review_count(self) -> int:
        """Get the total number of reviews.
        
        Returns:
            int: Total number of reviews or 0 if not found.
        """
        try:
            # Get selectors from structure file if available
            selectors = []
            
            if self.structure_loaded:
                total_reviews_count = self.structure_manager.get_selector(
                    "tripadvisor", "totalReviewsCount", []
                )
                
                if isinstance(total_reviews_count, list) and total_reviews_count:
                    selectors = total_reviews_count
                else:
                    # Fallback to default selectors
                    selectors = [
                        '.reviews_header_count', 
                        '.header_rating span.reviews_header_count',
                        'a.restaurants-detail-overview-cards-RatingsOverviewCard__ratingCount--DFxkG'
                    ]
            else:
                # Fallback to default selectors
                selectors = [
                    '.reviews_header_count', 
                    '.header_rating span.reviews_header_count',
                    'a.restaurants-detail-overview-cards-RatingsOverviewCard__ratingCount--DFxkG'
                ]
            
            for selector in selectors:
                try:
                    element = await self.page.querySelector(selector)
                    if element:
                        count_text = await self.page.evaluate(
                            '(element) => element.textContent', 
                            element
                        )
                        
                        # Extract numbers from the text
                        import re
                        count_match = re.search(r'[\d,]+', count_text)
                        if count_match:
                            count_str = count_match.group(0).replace(',', '')
                            return int(count_str)
                except Exception:
                    continue
            
            # Fallback: Just return a large number
            return 1000
            
        except Exception as e:
            logger.warning(f"Error getting total review count: {e}")
            return 0
    
    async def _extract_reviews_from_page(self) -> List[Dict[str, Any]]:
        """Extract reviews from the current page.
        
        Returns:
            List[Dict[str, Any]]: List of reviews from the current page.
        """
        page_reviews = []
        
        try:
            logger.info("Extracting reviews from current page")
            
            # Expand all review texts (if they're truncated)
            await self._expand_review_texts()
            
            # Get selectors from structure file if available
            review_container = []
            reviewer_name = []
            rating = []
            date = []
            review_text = []
            rating_extractor = None
            date_cleanup_patterns = []
            
            if self.structure_loaded:
                review_container = self.structure_manager.get_selector("tripadvisor", "reviewContainer", [])
                if isinstance(review_container, str):
                    review_container = [review_container]
                
                reviewer_name = self.structure_manager.get_selector("tripadvisor", "reviewerName", [])
                if isinstance(reviewer_name, str):
                    reviewer_name = [reviewer_name]
                
                rating = self.structure_manager.get_selector("tripadvisor", "rating", [])
                if isinstance(rating, str):
                    rating = [rating]
                
                rating_extractor = self.structure_manager.get_selector("tripadvisor", "ratingExtractor", None)
                
                date = self.structure_manager.get_selector("tripadvisor", "date", [])
                if isinstance(date, str):
                    date = [date]
                
                date_cleanup_patterns = self.structure_manager.get_selector("tripadvisor", "dateCleanupPatterns", [])
                
                review_text = self.structure_manager.get_selector("tripadvisor", "reviewText", [])
                if isinstance(review_text, str):
                    review_text = [review_text]
            
            # Fallback to default selectors if needed
            if not review_container:
                review_container = ["div[data-reviewid]", ".review-container"]
            
            if not reviewer_name:
                reviewer_name = [".info_text div", ".memberOverlayLink", ".member_info .username"]
            
            if not rating:
                rating = ["span.ui_bubble_rating"]
            
            if not rating_extractor:
                rating_extractor = {
                    "type": "classPattern",
                    "pattern": "bubble_([0-9]+)",
                    "divisor": 10
                }
            
            if not date:
                date = [".ratingDate", ".date"]
            
            if not date_cleanup_patterns:
                date_cleanup_patterns = [
                    {"pattern": "^Reviewed\\s+", "replacement": ""},
                    {"pattern": "^Date of visit:?\\s+", "replacement": ""}
                ]
            
            if not review_text:
                review_text = [".prw_reviews_text_summary_hsx p", ".partial_entry", ".review-container .entry"]
            
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
                                    // Extract rating based on rating extractor
                                    const extractorType = {json.dumps(rating_extractor.get("type", ""))};
                                    const extractorPattern = {json.dumps(rating_extractor.get("pattern", ""))};
                                    const extractorDivisor = {json.dumps(rating_extractor.get("divisor", 1))};
                                    
                                    if (extractorType === "classPattern") {{
                                        const ratingClass = ratingElement.className;
                                        const ratingMatch = ratingClass.match(new RegExp(extractorPattern));
                                        if (ratingMatch) {{
                                            rating = parseInt(ratingMatch[1]) / extractorDivisor;
                                        }}
                                    }}
                                    break;
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
                            const dateCleanupPatterns = {json.dumps(date_cleanup_patterns)};
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
                                date: dateText,
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
                    "platform": "TripAdvisor",
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
    
    async def _expand_review_texts(self) -> None:
        """Expand truncated review texts by clicking 'More' buttons."""
        try:
            # Get selectors from structure file if available
            expand_button_selectors = []
            batch_size = 3
            delay_between = {"base_time": 1500, "variance": 500}
            
            if self.structure_loaded:
                expand_button = self.structure_manager.get_selector("tripadvisor", "expandButton", [])
                if isinstance(expand_button, list) and expand_button:
                    expand_button_selectors = expand_button
                elif isinstance(expand_button, str):
                    expand_button_selectors = [expand_button]
                
                # Get behavior pattern for expand reviews
                expand_reviews = self.structure_manager.get_behavior_pattern(
                    "tripadvisor", "expand_reviews", {}
                )
                
                if expand_reviews:
                    batch_size = expand_reviews.get("batch_size", 3)
                    delay_between = expand_reviews.get("delay_between", {
                        "base_time": 1500,
                        "variance": 500
                    })
            
            if not expand_button_selectors:
                # Fallback to default selectors
                expand_button_selectors = ['span.taLnk.ulBlueLinks', 'div.taLnk.ulBlueLinks']
            
            # Find all "More" buttons
            more_buttons = []
            for selector in expand_button_selectors:
                buttons = await self.page.querySelectorAll(selector)
                if buttons:
                    more_buttons.extend(buttons)
            
            if more_buttons:
                logger.info(f"Expanding {len(more_buttons)} truncated reviews")
                
                # Process in batches
                for i in range(0, len(more_buttons), batch_size):
                    batch = more_buttons[i:i+batch_size]
                    
                    for button in batch:
                        try:
                            # Check if the button is for expanding review
                            button_text = await self.page.evaluate('(element) => element.textContent', button)
                            if button_text and ('More' in button_text or 'more' in button_text):
                                await button.click()
                                
                                # Wait after click with random delay
                                if delay_between:
                                    base_time = delay_between.get("base_time", 1500) / 1000
                                    variance = delay_between.get("variance", 500) / 1000
                                    
                                    import random
                                    delay_time = base_time + random.uniform(-variance, variance)
                                    await asyncio.sleep(max(0.1, delay_time))
                        except Exception:
                            continue
                    
                    # Wait between batches
                    await async_delay_between_actions("waiting")
                        
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
                next_page_button = self.structure_manager.get_selector("tripadvisor", "nextPageButton", [])
                if isinstance(next_page_button, list) and next_page_button:
                    next_button_selectors = next_page_button
                elif isinstance(next_page_button, str):
                    next_button_selectors = [next_page_button]
            
            if not next_button_selectors:
                # Fallback to default selectors
                next_button_selectors = [
                    'a.nav.next',
                    'a.ui_button.nav.next',
                    '[data-page-number="next"]'
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
    """Run the TripAdvisor structure-based review scraper."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    
    try:
        # Create scraper
        scraper = TripAdvisorStructureScraper()
        
        # Run scraper
        reviews = loop.run_until_complete(scraper.scrape_reviews())
        
        print(f"Successfully scraped {len(reviews)} TripAdvisor reviews")
        return reviews
        
    except Exception as e:
        logger.error(f"Error running TripAdvisor structure scraper: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    run_scraper()
