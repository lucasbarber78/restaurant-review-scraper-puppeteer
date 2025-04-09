#!/usr/bin/env python3
"""
TripAdvisor Reviews Scraper

This module scrapes reviews from TripAdvisor using Puppeteer.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TripAdvisorReviewScraper:
    """Scraper for TripAdvisor reviews."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the TripAdvisor review scraper.
        
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
        
        # Output settings
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
        logger.info(f"Initialized TripAdvisor scraper for {self.restaurant_name}")
    
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
        """Scrape reviews from TripAdvisor.
        
        Returns:
            List[Dict[str, Any]]: List of scraped reviews.
        """
        logger.info(f"Starting to scrape TripAdvisor reviews for {self.restaurant_name}")
        reviews = []
        
        try:
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Navigate to the TripAdvisor page
            logger.info(f"Navigating to {self.url}")
            await self.page.goto(self.url, {"waitUntil": "networkidle0"})
            
            # Apply human-like behavior if enabled
            if self.simulate_human and self.use_stealth:
                await self.stealth_enhancer.simulate_human_behavior(self.page)
            
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
    
    async def _handle_cookie_consent(self) -> None:
        """Handle cookie consent dialog if present."""
        try:
            # Common cookie consent button selectors
            cookie_selectors = [
                'button#onetrust-accept-btn-handler',
                'button[id*="accept"]',
                'button[id*="cookie"]',
                'button[class*="cookie"]',
                'button[class*="accept"]',
                '.evidon-banner-acceptbutton',
                '#gdpr-consent-tool-wrapper button[type="submit"]'
            ]
            
            for selector in cookie_selectors:
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
                        await async_delay_between_actions("click")
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
            # Try different selectors for the review count
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
            
            # Extract reviews using page.evaluate
            reviews_data = await self.page.evaluate("""
                () => {
                    const reviews = [];
                    
                    // Try primary selector (newer TripAdvisor layout)
                    let reviewElements = document.querySelectorAll('div[data-reviewid]');
                    
                    // If no reviews found, try alternative selector (older layout)
                    if (reviewElements.length === 0) {
                        reviewElements = document.querySelectorAll('.review-container');
                    }
                    
                    // Process each review
                    reviewElements.forEach(review => {
                        try {
                            // Get reviewer name (try different selectors)
                            let reviewerName = '';
                            const nameElement = review.querySelector('.info_text div') || 
                                                review.querySelector('.memberOverlayLink') ||
                                                review.querySelector('.member_info .username');
                            if (nameElement) {
                                reviewerName = nameElement.textContent.trim();
                            }
                            
                            // Get rating (try different selectors)
                            let rating = 0;
                            const ratingElement = review.querySelector('span.ui_bubble_rating');
                            if (ratingElement) {
                                const ratingClass = ratingElement.className;
                                const ratingMatch = ratingClass.match(/bubble_([0-9]+)/);
                                if (ratingMatch) {
                                    rating = parseInt(ratingMatch[1]) / 10;
                                }
                            }
                            
                            // Get date (try different selectors)
                            let dateText = '';
                            const dateElement = review.querySelector('.ratingDate') || 
                                               review.querySelector('.date');
                            if (dateElement) {
                                dateText = dateElement.textContent.trim();
                                // Remove "Reviewed" or "Date of visit" text if present
                                dateText = dateText.replace(/^Reviewed\\s+/, '')
                                                   .replace(/^Date of visit:?\\s+/, '');
                            }
                            
                            // Get review text (try different selectors)
                            let reviewText = '';
                            const textElement = review.querySelector('.prw_reviews_text_summary_hsx p') || 
                                               review.querySelector('.partial_entry') ||
                                               review.querySelector('.review-container .entry');
                            if (textElement) {
                                reviewText = textElement.textContent.trim();
                            }
                            
                            // Add to reviews array
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
            """)
            
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
            # Find all "More" buttons
            more_buttons = await self.page.querySelectorAll('span.taLnk.ulBlueLinks') or \
                           await self.page.querySelectorAll('div.taLnk.ulBlueLinks')
            
            if more_buttons:
                logger.info(f"Expanding {len(more_buttons)} truncated reviews")
                for button in more_buttons:
                    try:
                        # Check if the button is for expanding review
                        button_text = await self.page.evaluate('(element) => element.textContent', button)
                        if button_text and ('More' in button_text or 'more' in button_text):
                            await button.click()
                            await async_delay_between_actions("click")
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
            # Find the next page button
            next_button = await self.page.querySelector('a.nav.next')
            
            if not next_button:
                # Try alternative selector
                next_button = await self.page.querySelector('a.ui_button.nav.next')
            
            if not next_button:
                # One more alternative
                next_button = await self.page.querySelector('[data-page-number="next"]')
            
            # Check if the button exists and is not disabled
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
    """Run the TripAdvisor review scraper."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    
    try:
        # Create scraper
        scraper = TripAdvisorReviewScraper()
        
        # Run scraper
        reviews = loop.run_until_complete(scraper.scrape_reviews())
        
        print(f"Successfully scraped {len(reviews)} TripAdvisor reviews")
        return reviews
        
    except Exception as e:
        logger.error(f"Error running TripAdvisor scraper: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    run_scraper()
