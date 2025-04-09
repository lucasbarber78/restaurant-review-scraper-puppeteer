#!/usr/bin/env python3
"""
Google Reviews Scraper

This module scrapes reviews from Google Maps using Puppeteer.
It uses dynamic structure analysis to adapt to changes in Google's DOM structure.
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

# Import structure parser
from src.utils.structure_parser import GoogleStructureParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleReviewScraper:
    """Scraper for Google Maps reviews."""
    
    def __init__(self, config_path: str = "config.yaml", client_config: Dict[str, Any] = None):
        """Initialize the Google Reviews scraper.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                Defaults to "config.yaml".
            client_config (Dict[str, Any], optional): Client-specific configuration.
                If provided, overrides values from config.yaml.
        """
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        # Override with client-specific settings if provided
        if client_config:
            self.restaurant_name = client_config.get("name", self.config.get("restaurant_name", ""))
            if "google_url" in client_config:
                self.config["google_url"] = client_config["google_url"]
                
            # Set client-specific output file
            client_name_safe = self.restaurant_name.replace(" ", "_").lower()
            self.csv_path = f"reviews_{client_name_safe}.csv"
        else:
            self.restaurant_name = self.config.get("restaurant_name", "")
            self.csv_path = self.config.get("csv_file_path", "reviews.csv")
            
        # Initialize browser session variables
        self.browser = None
        self.page = None
        
        # Get scraping parameters
        self.url = self.config.get("google_url", "")
        self.date_range = self.config.get("date_range", {})
        self.max_reviews = self.config.get("max_reviews_per_platform", 100)
        self.timeout = self.config.get("timeout_seconds", 60)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        
        # Get Google scraper specific configuration
        google_config = self.config.get("google_scraper", {})
        self.use_structure_analysis = google_config.get("use_structure_analysis", True)
        self.structure_file_path = google_config.get(
            "structure_file_path", 
            "Review Site Optimization/google_search_review_structure_analysis.json"
        )
        self.fallback_to_default_selectors = google_config.get("fallback_to_default_selectors", True)
        
        # Load structure analysis if enabled
        if self.use_structure_analysis:
            self.structure_parser = GoogleStructureParser(self.structure_file_path)
            self.selectors = self.structure_parser.get_review_selectors()
            logger.info(f"Loaded {len(self.selectors['review_container'])} review container selectors")
        else:
            self.structure_parser = None
            self.selectors = None
        
        # Set up anti-bot measures
        self.anti_bot_settings = self.config.get("anti_bot_settings", {})
        self.use_delays = self.anti_bot_settings.get("enable_random_delays", True)
        self.use_stealth = self.anti_bot_settings.get("enable_stealth_plugins", True)
        self.headless = self.anti_bot_settings.get("headless_mode", False)
        self.simulate_human = self.anti_bot_settings.get("simulate_human_behavior", True)
        
        logger.info(f"Initialized Google Reviews scraper for {self.restaurant_name}")
    
    async def init_browser(self) -> None:
        """Initialize the browser session with Puppeteer."""
        logger.info("Initializing browser session for Google Reviews scraping")
        
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
                self.stealth_enhancer = await apply_stealth_measures(self.page, "google")
            
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
    
    async def scrape_reviews(self) -> List[Dict[str, Any]]:
        """Scrape reviews from Google Maps.
        
        Returns:
            List[Dict[str, Any]]: List of scraped reviews.
        """
        logger.info(f"Starting to scrape Google reviews for {self.restaurant_name}")
        reviews = []
        
        try:
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Navigate to the Google Maps page
            logger.info(f"Navigating to {self.url}")
            await self.page.goto(self.url, {"waitUntil": "networkidle0"})
            
            # Apply human-like behavior if enabled
            if self.simulate_human and self.use_stealth:
                await self.stealth_enhancer.simulate_human_behavior(self.page)
            
            # Wait for reviews to load
            await async_delay_between_actions("waiting")
            
            # Take a screenshot for debugging if needed
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshots_dir, f"google_search_{self.restaurant_name.replace(' ', '_').lower()}.png")
            await take_screenshot(self.page, screenshot_path)
            
            # Find reviews section
            reviews_section = await self._find_reviews_section()
            if not reviews_section:
                logger.warning("Reviews section not found, looking for reviews tab to click")
                
                # Check if reviews tab needs to be clicked
                reviews_tab_selector = 'button[jsaction*="pane.rating.moreReviews"]'
                reviews_tab = await self.page.querySelector(reviews_tab_selector)
                if reviews_tab:
                    logger.info("Clicking on reviews tab")
                    await self.page.click(reviews_tab_selector)
                    await async_delay_between_actions("navigation")
                else:
                    logger.warning("Reviews tab not found, trying alternative selectors")
                    await self._try_alternative_review_tabs()
            
            # Check if reviews need to be expanded
            await self._expand_review_texts()
            
            # Scroll to load more reviews
            await self._scroll_to_load_reviews()
            
            # Collect reviews
            reviews = await self._extract_reviews()
            
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
    
    async def _find_reviews_section(self) -> Optional[Any]:
        """Find the reviews section on the page.
        
        Returns:
            Optional[Any]: The reviews section element or None if not found.
        """
        # Try selectors from structure analysis first if available
        if self.use_structure_analysis and self.selectors:
            for selector in self.selectors["review_container"]:
                try:
                    section = await self.page.querySelector(selector)
                    if section:
                        logger.info(f"Found reviews section using selector: {selector}")
                        return section
                except Exception:
                    continue
        
        # Fall back to default selectors
        default_selectors = [
            'div[data-review-id]',
            '.review-container',
            'div[role="listitem"]',
            'div.wDYxhc[data-attrid*="review"]',
            'div[jscontroller] > div.lN6TS',
            'div.Jb0Zif .wDYxhc',
            'div.kp-wholepage .wDYxhc'
        ]
        
        for selector in default_selectors:
            try:
                section = await self.page.querySelector(selector)
                if section:
                    logger.info(f"Found reviews section using default selector: {selector}")
                    return section
            except Exception:
                continue
        
        return None
    
    async def _try_alternative_review_tabs(self) -> bool:
        """Try clicking on alternative review tabs.
        
        Returns:
            bool: True if a tab was clicked successfully, False otherwise.
        """
        tab_selectors = [
            'a[href*="reviews"]',
            'button[aria-label*="review"]',
            'div[role="tab"][aria-label*="review"]',
            'span[aria-label*="Reviews"]',
            'a[data-tab*="reviews"]'
        ]
        
        for selector in tab_selectors:
            try:
                tab = await self.page.querySelector(selector)
                if tab:
                    logger.info(f"Clicking on alternative reviews tab: {selector}")
                    await tab.click()
                    await async_delay_between_actions("navigation")
                    return True
            except Exception:
                continue
        
        return False
    
    async def _expand_review_texts(self) -> None:
        """Expand truncated review texts by clicking 'More' buttons."""
        try:
            # Try selectors from structure analysis first if available
            expand_selectors = []
            if self.use_structure_analysis and self.selectors:
                expand_selectors = [
                    'button[jsaction*="pane.review.expandReview"]',
                    '.review-more-link',
                    'a[role="button"][class*="expand"]',
                    'span[role="button"][class*="expand"]'
                ]
            
            for selector in expand_selectors:
                try:
                    expand_buttons = await self.page.querySelectorAll(selector)
                    if expand_buttons and len(expand_buttons) > 0:
                        logger.info(f"Expanding {len(expand_buttons)} review(s) using selector: {selector}")
                        for button in expand_buttons:
                            try:
                                await button.click()
                                await async_delay_between_actions("click")
                            except Exception:
                                pass
                        return
                except Exception:
                    continue
            
        except Exception as e:
            logger.warning(f"Error expanding review texts: {e}")
    
    async def _scroll_to_load_reviews(self) -> None:
        """Scroll through reviews to load more."""
        try:
            # Calculate number of scrolls based on max reviews with a reasonable limit
            num_scrolls = min(10, self.max_reviews // 5)
            
            logger.info(f"Scrolling {num_scrolls} times to load more reviews")
            
            for i in range(num_scrolls):
                # Try different scroll methods
                scroll_methods = [
                    """
                    () => {
                        const reviewsDiv = document.querySelector('div[role="feed"]');
                        if (reviewsDiv) {
                            reviewsDiv.scrollTop = reviewsDiv.scrollHeight;
                            return true;
                        }
                        return false;
                    }
                    """,
                    """
                    () => {
                        const reviewsContainer = document.querySelector('.review-dialog-list');
                        if (reviewsContainer) {
                            reviewsContainer.scrollTop = reviewsContainer.scrollHeight;
                            return true;
                        }
                        return false;
                    }
                    """,
                    """
                    () => {
                        window.scrollBy(0, 500);
                        return true;
                    }
                    """
                ]
                
                # Try each method until one works
                scroll_successful = False
                for method in scroll_methods:
                    scroll_result = await self.page.evaluate(method)
                    if scroll_result:
                        scroll_successful = True
                        break
                
                if not scroll_successful:
                    logger.warning(f"Scroll attempt {i+1} failed, no suitable container found")
                
                # Apply human-like delay
                await async_delay_between_actions("scroll")
                
                # Check for CAPTCHA after each scroll
                if self.use_stealth:
                    captcha_detected = await self.stealth_enhancer.detect_and_handle_captcha(self.page)
                    if captcha_detected:
                        logger.warning("CAPTCHA detected while scrolling reviews. Pausing...")
                        await async_delay_between_actions("waiting")
                        break
        
        except Exception as e:
            logger.warning(f"Error scrolling to load more reviews: {e}")
    
    async def _extract_reviews(self) -> List[Dict[str, Any]]:
        """Extract reviews from the page using dynamic selectors.
        
        Returns:
            List[Dict[str, Any]]: List of extracted reviews.
        """
        reviews = []
        review_count = 0
        
        try:
            logger.info("Extracting Google reviews")
            
            # Try structure-based extraction if enabled
            if self.use_structure_analysis and self.selectors:
                logger.info("Using structure-based extraction")
                reviews_data = await self._extract_with_structure()
                
                # Fall back to default extraction if structure-based extraction fails or returns no reviews
                if not reviews_data and self.fallback_to_default_selectors:
                    logger.warning("Structure-based extraction failed, falling back to default extraction")
                    reviews_data = await self._extract_with_default_selectors()
            else:
                # Use default extraction
                logger.info("Using default extraction method")
                reviews_data = await self._extract_with_default_selectors()
            
            # Process the reviews
            for review_data in reviews_data:
                if review_count >= self.max_reviews:
                    break
                
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
                reviews.append(review)
                review_count += 1
            
            logger.info(f"Extracted {len(reviews)} Google reviews")
            
        except Exception as e:
            logger.error(f"Error extracting reviews: {e}", exc_info=True)
        
        return reviews
    
    async def _extract_with_structure(self) -> List[Dict[str, Any]]:
        """Extract reviews using structure-based selectors.
        
        Returns:
            List[Dict[str, Any]]: List of extracted reviews.
        """
        try:
            # Convert selectors to JSON string for JavaScript
            review_container_selectors = json.dumps(self.selectors["review_container"])
            reviewer_name_selectors = json.dumps(self.selectors["reviewer_name"])
            rating_selectors = json.dumps(self.selectors["rating"])
            date_selectors = json.dumps(self.selectors["date"])
            review_text_selectors = json.dumps(self.selectors["review_text"])
            
            # Create dynamic extraction script
            extraction_script = f"""
                () => {{
                    const reviews = [];
                    let reviewElements = [];
                    
                    // Try each review container selector
                    const reviewSelectors = {review_container_selectors};
                    for (const selector of reviewSelectors) {{
                        try {{
                            const elements = document.querySelectorAll(selector);
                            if (elements && elements.length > 0) {{
                                reviewElements = Array.from(elements);
                                console.log(`Found ${{reviewElements.length}} reviews using selector: ${{selector}}`);
                                break;
                            }}
                        }} catch (e) {{
                            console.error(`Error with selector ${{selector}}:`, e);
                        }}
                    }}
                    
                    // Process each review
                    reviewElements.forEach(review => {{
                        try {{
                            // Extract reviewer name
                            let reviewerName = '';
                            const nameSelectors = {reviewer_name_selectors};
                            for (const selector of nameSelectors) {{
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
                            
                            // Extract rating
                            let rating = 0;
                            const ratingSelectors = {rating_selectors};
                            for (const selector of ratingSelectors) {{
                                try {{
                                    const ratingElement = review.querySelector(selector);
                                    if (ratingElement) {{
                                        const ariaLabel = ratingElement.getAttribute('aria-label');
                                        if (ariaLabel && ariaLabel.includes('star')) {{
                                            const match = ariaLabel.match(/\\d+/);
                                            if (match) {{
                                                rating = parseInt(match[0]);
                                                break;
                                            }}
                                        }}
                                    }}
                                }} catch (e) {{
                                    // Continue to next selector
                                }}
                            }}
                            
                            // Extract date
                            let dateText = '';
                            const dateSelectors = {date_selectors};
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
                            
                            // Extract review text
                            let reviewText = '';
                            const textSelectors = {review_text_selectors};
                            for (const selector of textSelectors) {{
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
                            console.error('Error extracting review:', e);
                        }}
                    }});
                    
                    return reviews;
                }}
            """
            
            # Execute the extraction script
            reviews_data = await self.page.evaluate(extraction_script)
            logger.info(f"Structure-based extraction found {len(reviews_data)} reviews")
            
            return reviews_data
            
        except Exception as e:
            logger.error(f"Error in structure-based extraction: {e}", exc_info=True)
            return []
    
    async def _extract_with_default_selectors(self) -> List[Dict[str, Any]]:
        """Extract reviews using default selectors.
        
        Returns:
            List[Dict[str, Any]]: List of extracted reviews.
        """
        try:
            # Use the original extraction script with hardcoded selectors
            extraction_script = """
                () => {
                    const reviews = [];
                    const reviewElements = document.querySelectorAll('div[data-review-id]');
                    
                    if (reviewElements.length === 0) {
                        console.log("No reviews found with primary selector, trying alternatives");
                        // Try alternative selectors
                        const alternativeSelectors = [
                            '.review-container',
                            'div[role="listitem"]',
                            'div.wDYxhc[data-attrid*="review"]',
                            'div.Jb0Zif .wDYxhc'
                        ];
                        
                        for (const selector of alternativeSelectors) {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {
                                console.log(`Found ${elements.length} reviews using ${selector}`);
                                elements.forEach(review => {
                                    try {
                                        // Extract review data with different possible selectors
                                        let reviewerName = '';
                                        const nameSelectors = ['.d4r55', '.info_text div', '.member_info .username', '.y3Ibjb'];
                                        for (const nameSelector of nameSelectors) {
                                            const nameElement = review.querySelector(nameSelector);
                                            if (nameElement) {
                                                reviewerName = nameElement.textContent.trim();
                                                break;
                                            }
                                        }
                                        
                                        let rating = 0;
                                        const ratingSelectors = ['span[role="img"]', 'div[aria-label*="star"]', 'g-review-stars'];
                                        for (const ratingSelector of ratingSelectors) {
                                            const ratingElement = review.querySelector(ratingSelector);
                                            if (ratingElement) {
                                                const ariaLabel = ratingElement.getAttribute('aria-label');
                                                if (ariaLabel && ariaLabel.includes('star')) {
                                                    const match = ariaLabel.match(/\\d+/);
                                                    if (match) {
                                                        rating = parseInt(match[0]);
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                        
                                        let dateText = '';
                                        const dateSelectors = ['.y3Ibjb', '.ratingDate', '.date', '.rsqaWe'];
                                        for (const dateSelector of dateSelectors) {
                                            const dateElement = review.querySelector(dateSelector);
                                            if (dateElement) {
                                                dateText = dateElement.textContent.trim();
                                                break;
                                            }
                                        }
                                        
                                        let reviewText = '';
                                        const textSelectors = ['.wiI7pd', '.prw_reviews_text_summary_hsx p', '.partial_entry', '.review-content p'];
                                        for (const textSelector of textSelectors) {
                                            const textElement = review.querySelector(textSelector);
                                            if (textElement) {
                                                reviewText = textElement.textContent.trim();
                                                break;
                                            }
                                        }
                                        
                                        if (reviewerName || rating || dateText || reviewText) {
                                            reviews.push({
                                                reviewer_name: reviewerName,
                                                rating: rating,
                                                date: dateText,
                                                text: reviewText
                                            });
                                        }
                                    } catch (e) {
                                        console.error('Error extracting review:', e);
                                    }
                                });
                                return reviews;
                            }
                        }
                    }
                    
                    // Extract using primary selector
                    reviewElements.forEach(review => {
                        try {
                            // Extract review data
                            const reviewerElement = review.querySelector('.d4r55');
                            const reviewerName = reviewerElement ? reviewerElement.textContent.trim() : '';
                            
                            const ratingElement = review.querySelector('span[role="img"]');
                            const ratingText = ratingElement ? ratingElement.getAttribute('aria-label') : '';
                            const rating = ratingText ? parseInt(ratingText.match(/\\d+/)[0]) : 0;
                            
                            const dateElement = review.querySelector('.rsqaWe');
                            const dateText = dateElement ? dateElement.textContent.trim() : '';
                            
                            const textElement = review.querySelector('.wiI7pd');
                            const reviewText = textElement ? textElement.textContent.trim() : '';
                            
                            reviews.push({
                                reviewer_name: reviewerName,
                                rating: rating,
                                date: dateText,
                                text: reviewText
                            });
                        } catch (e) {
                            console.error('Error extracting review:', e);
                        }
                    });
                    
                    return reviews;
                }
            """
            
            # Execute the extraction script
            reviews_data = await self.page.evaluate(extraction_script)
            logger.info(f"Default extraction found {len(reviews_data)} reviews")
            
            return reviews_data
            
        except Exception as e:
            logger.error(f"Error in default extraction: {e}", exc_info=True)
            return []
    
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


def run_scraper(client_config=None):
    """Run the Google Reviews scraper.
    
    Args:
        client_config (dict, optional): Client-specific configuration.
            If provided, overrides values from config.yaml.
    
    Returns:
        List[Dict[str, Any]]: List of scraped reviews.
    """
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    
    try:
        # Create scraper
        scraper = GoogleReviewScraper(client_config=client_config)
        
        # Run scraper
        reviews = loop.run_until_complete(scraper.scrape_reviews())
        
        print(f"Successfully scraped {len(reviews)} Google reviews for {scraper.restaurant_name}")
        return reviews
        
    except Exception as e:
        logger.error(f"Error running Google scraper: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    run_scraper()
