#!/usr/bin/env python3
"""
Google Reviews Scraper

This module scrapes reviews from Google Maps using Puppeteer.
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

class GoogleReviewScraper:
    """Scraper for Google Maps reviews."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the Google Reviews scraper.
        
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
        
        # Output settings
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
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
            
            # Find reviews section
            reviews_section = await self.page.querySelector('div[data-review-id]')
            if not reviews_section:
                logger.info("Looking for reviews section")
                
                # Check if reviews tab needs to be clicked
                reviews_tab_selector = 'button[jsaction*="pane.rating.moreReviews"]'
                reviews_tab = await self.page.querySelector(reviews_tab_selector)
                if reviews_tab:
                    logger.info("Clicking on reviews tab")
                    await self.page.click(reviews_tab_selector)
                    await async_delay_between_actions("navigation")
            
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
    
    async def _extract_reviews(self) -> List[Dict[str, Any]]:
        """Extract reviews from the page.
        
        Returns:
            List[Dict[str, Any]]: List of extracted reviews.
        """
        reviews = []
        review_count = 0
        
        try:
            logger.info("Extracting Google reviews")
            
            # Check if we need to expand all reviews
            expand_buttons = await self.page.querySelectorAll('button[jsaction*="pane.review.expandReview"]')
            if expand_buttons:
                logger.info(f"Expanding {len(expand_buttons)} review(s)")
                for button in expand_buttons:
                    try:
                        await button.click()
                        await async_delay_between_actions("click")
                    except:
                        pass
            
            # Scroll through reviews to load more
            for _ in range(min(10, self.max_reviews // 5)):  # Limiting scrolls based on max reviews
                # Scroll down in the reviews section
                await self.page.evaluate("""
                    () => {
                        const reviewsDiv = document.querySelector('div[role="feed"]');
                        if (reviewsDiv) {
                            reviewsDiv.scrollTop = reviewsDiv.scrollHeight;
                        }
                    }
                """)
                
                # Apply human-like delay
                await async_delay_between_actions("scroll")
                
                # Check for CAPTCHA
                if self.use_stealth:
                    captcha_detected = await self.stealth_enhancer.detect_and_handle_captcha(self.page)
                    if captcha_detected:
                        logger.warning("CAPTCHA detected while scrolling reviews. Pausing...")
                        await async_delay_between_actions("waiting")
            
            # Extract reviews using page.evaluate
            reviews_data = await self.page.evaluate("""
                () => {
                    const reviews = [];
                    const reviewElements = document.querySelectorAll('div[data-review-id]');
                    
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
            """)
            
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
    """Run the Google Reviews scraper."""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    
    try:
        # Create scraper
        scraper = GoogleReviewScraper()
        
        # Run scraper
        reviews = loop.run_until_complete(scraper.scrape_reviews())
        
        print(f"Successfully scraped {len(reviews)} Google reviews")
        return reviews
        
    except Exception as e:
        logger.error(f"Error running Google scraper: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    run_scraper()
