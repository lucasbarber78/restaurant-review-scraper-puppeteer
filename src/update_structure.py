#!/usr/bin/env python3
"""
Update Structure Analysis Module

This module analyzes the structure of Google Reviews pages to identify key selectors
for scraping. It helps maintain the scraper's resilience against changes to
the Google Maps review structure.
"""

import os
import json
import logging
import asyncio
import yaml
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import utility modules
from src.utils import (
    create_browser_session, 
    close_browser_session, 
    take_screenshot, 
    save_html,
    apply_stealth_measures,
    delay_between_actions, 
    async_delay_between_actions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("structure_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StructureAnalyzer:
    """Analyzer for web page structure."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the structure analyzer.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                Defaults to "config.yaml".
        """
        # Load configuration
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        else:
            self.config = {}
        
        # Get structure analysis settings
        self.structure_settings = self.config.get("structure_analysis_settings", {})
        self.min_samples = self.structure_settings.get("min_samples", 5)
        self.max_samples = self.structure_settings.get("max_samples", 10)
        self.save_samples = self.structure_settings.get("save_samples", True)
        self.samples_dir = self.structure_settings.get("samples_directory", "data/samples")
        
        # Initialize browser session variables
        self.browser = None
        self.page = None
        
        # Anti-bot settings
        anti_bot_settings = self.config.get("anti_bot_settings", {})
        self.use_stealth = anti_bot_settings.get("enable_stealth_plugins", True)
        self.headless = anti_bot_settings.get("headless_mode", False)
        
        logger.info("Initialized Structure Analyzer")
    
    async def init_browser(self) -> None:
        """Initialize the browser session."""
        logger.info("Initializing browser session for structure analysis")
        
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
            await self.page.setDefaultTimeout(60000)  # 60 seconds
            
            logger.info("Browser session initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing browser: {e}", exc_info=True)
            if self.browser:
                await close_browser_session(self.browser)
                self.browser = None
                self.page = None
            raise
    
    async def analyze_google_structure(self) -> Dict[str, Any]:
        """Analyze the structure of Google Maps review pages.
        
        Returns:
            Dict[str, Any]: Structure analysis results.
        """
        logger.info("Starting Google Maps structure analysis")
        
        structure_data = {
            "updated_at": datetime.now().isoformat(),
            "selectors": {},
            "success": False
        }
        
        try:
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Get sample URLs
            sample_urls = self._get_sample_urls()
            
            if not sample_urls:
                logger.error("No sample URLs available for analysis")
                return structure_data
            
            # Analyze samples
            all_selectors = []
            
            for i, url in enumerate(sample_urls[:self.max_samples]):
                logger.info(f"Analyzing sample {i+1}/{min(len(sample_urls), self.max_samples)}: {url}")
                
                # Navigate to the URL
                await self.page.goto(url, {"waitUntil": "networkidle0"})
                await async_delay_between_actions("waiting")
                
                # Save HTML sample if enabled
                if self.save_samples:
                    sample_filename = f"google_sample_{i+1}_{int(time.time())}.html"
                    await self._save_sample(sample_filename)
                
                # Extract selectors
                selectors = await self._extract_google_selectors()
                if selectors:
                    all_selectors.append(selectors)
                
                # Wait between samples
                await async_delay_between_actions("navigation")
            
            # Analyze collected selectors
            structure_data["selectors"] = self._analyze_selectors(all_selectors)
            structure_data["success"] = True
            
            logger.info("Google Maps structure analysis completed successfully")
            return structure_data
            
        except Exception as e:
            logger.error(f"Error analyzing Google structure: {e}", exc_info=True)
            return structure_data
            
        finally:
            # Close browser
            if self.browser:
                await close_browser_session(self.browser)
                self.browser = None
                self.page = None
    
    def _get_sample_urls(self) -> List[str]:
        """Get a list of sample URLs for analysis.
        
        Returns:
            List[str]: List of URLs.
        """
        # Get URLs from config
        urls = []
        
        # First, try to get URLs from clients.json
        clients_path = "clients.json"
        if os.path.exists(clients_path):
            try:
                with open(clients_path, 'r') as file:
                    clients_data = json.load(file)
                
                for client_name, client_data in clients_data.items():
                    if client_data.get("active", True) and "google_url" in client_data:
                        urls.append(client_data["google_url"])
            except Exception as e:
                logger.warning(f"Error reading clients.json: {e}")
        
        # Add URL from config.yaml if it exists
        if "google_url" in self.config:
            if self.config["google_url"] not in urls:
                urls.append(self.config["google_url"])
        
        # Ensure we have at least the minimum required samples
        if len(urls) < self.min_samples:
            # Add some default/backup URLs
            backup_urls = [
                "https://www.google.com/maps/place/Chipotle+Mexican+Grill/@37.7918244,-122.4087275,17z/data=!3m1!4b1!4m6!3m5!1s0x808580869b099e0f:0xf724d8c3b464db9c!8m2!3d37.7918244!4d-122.4061526!16s%2Fg%2F1td63v2t",
                "https://www.google.com/maps/place/McDonald's/@37.7887459,-122.4105551,17z/data=!3m1!4b1!4m6!3m5!1s0x80858062cf4133f7:0xbf56d939dd0678b1!8m2!3d37.7887459!4d-122.4079802!16s%2Fm%2F07gyp7",
                "https://www.google.com/maps/place/Starbucks/@37.7866327,-122.4095442,17z/data=!3m1!4b1!4m6!3m5!1s0x80858083c6810295:0xd75ab7a9c8e80107!8m2!3d37.7866327!4d-122.4069693!16s%2Fm%2F01vsn9",
                "https://www.google.com/maps/place/Outback+Steakhouse/@37.7767736,-122.4185596,17z/data=!3m1!4b1!4m6!3m5!1s0x808f7df7a83d3017:0xc396be3b7d184fc9!8m2!3d37.7767736!4d-122.4159847!16s%2Fm%2F01w5c3",
                "https://www.google.com/maps/place/The+Cheesecake+Factory/@37.7845459,-122.4079433,17z/data=!3m1!4b1!4m6!3m5!1s0x80858089a740e31d:0xb9546c7e5c3d439c!8m2!3d37.7845459!4d-122.4053684!16s%2Fm%2F01w59m4"
            ]
            
            # Add backup URLs until we reach min_samples
            for url in backup_urls:
                if url not in urls and len(urls) < self.min_samples:
                    urls.append(url)
        
        # Shuffle the URLs to avoid bias
        random.shuffle(urls)
        
        return urls
    
    async def _save_sample(self, filename: str) -> None:
        """Save an HTML sample.
        
        Args:
            filename (str): Filename to save as.
        """
        try:
            # Create samples directory if it doesn't exist
            os.makedirs(self.samples_dir, exist_ok=True)
            
            # Save HTML
            sample_path = os.path.join(self.samples_dir, filename)
            await save_html(self.page, sample_path)
            
            logger.debug(f"Saved HTML sample to {sample_path}")
        except Exception as e:
            logger.warning(f"Error saving HTML sample: {e}")
    
    async def _extract_google_selectors(self) -> Dict[str, str]:
        """Extract key selectors from a Google Maps page.
        
        Returns:
            Dict[str, str]: Dictionary of selectors.
        """
        try:
            # Extract selectors using page.evaluate
            selectors = await self.page.evaluate("""
                () => {
                    const selectors = {};
                    
                    // Find the reviews section
                    const findReviewsSection = () => {
                        // Try common container selectors
                        const containers = [
                            document.querySelector('div[data-review-id]'),
                            document.querySelector('div[jsaction*="mouseover:pane.review"]'),
                            document.querySelector('div[jsaction*="reviewShelf.showMoreReviews"]'),
                            document.querySelector('div[data-hveid*="review"]')
                        ];
                        
                        // Return the first non-null container found
                        for (const container of containers) {
                            if (container) {
                                return container;
                            }
                        }
                        
                        return null;
                    };
                    
                    // Find the reviews container
                    const reviewsContainer = findReviewsSection();
                    if (reviewsContainer) {
                        selectors.reviewsContainerSelector = Array.from(reviewsContainer.attributes)
                            .filter(attr => ['class', 'data-review-id', 'jsaction', 'data-hveid'].includes(attr.name))
                            .map(attr => `[${attr.name}="${attr.value}"]`)
                            .join('');
                    }
                    
                    // Find review items
                    const findReviewItems = () => {
                        // Try various selectors for review items
                        const selectors = [
                            'div[data-review-id]',
                            'div[jsaction*="mouseover:pane.review"]',
                            'div.jftiEf', // Common class name
                            'div.WMbnJf' // Alternative class name
                        ];
                        
                        for (const selector of selectors) {
                            const items = document.querySelectorAll(selector);
                            if (items && items.length > 0) {
                                return { selector, count: items.length };
                            }
                        }
                        
                        return null;
                    };
                    
                    const reviewItemsResult = findReviewItems();
                    if (reviewItemsResult) {
                        selectors.reviewItemSelector = reviewItemsResult.selector;
                        selectors.reviewItemCount = reviewItemsResult.count;
                    }
                    
                    // Check for specific components in the first review item (if found)
                    if (reviewItemsResult && reviewItemsResult.count > 0) {
                        const firstReview = document.querySelector(reviewItemsResult.selector);
                        
                        // Reviewer name selector
                        const reviewerElements = [
                            firstReview.querySelector('.d4r55'),
                            firstReview.querySelector('.WNxzHc'),
                            firstReview.querySelector('div.TSUbDb')
                        ];
                        
                        for (const element of reviewerElements) {
                            if (element) {
                                selectors.reviewerNameSelector = element.tagName.toLowerCase() + 
                                    Array.from(element.classList).map(c => '.' + c).join('');
                                break;
                            }
                        }
                        
                        // Rating selector
                        const ratingElements = [
                            firstReview.querySelector('span[role="img"][aria-label*="star"]'),
                            firstReview.querySelector('span[aria-label*="stars"]')
                        ];
                        
                        for (const element of ratingElements) {
                            if (element) {
                                selectors.ratingSelector = 'span[role="img"][aria-label*="star"]';
                                break;
                            }
                        }
                        
                        // Date selector
                        const dateElements = [
                            firstReview.querySelector('.rsqaWe'),
                            firstReview.querySelector('span.xRkPPb'),
                            firstReview.querySelector('span[class*="review-date"]')
                        ];
                        
                        for (const element of dateElements) {
                            if (element) {
                                selectors.dateSelector = element.tagName.toLowerCase() + 
                                    Array.from(element.classList).map(c => '.' + c).join('');
                                break;
                            }
                        }
                        
                        // Review text selector
                        const textElements = [
                            firstReview.querySelector('.wiI7pd'),
                            firstReview.querySelector('span.MyEned'),
                            firstReview.querySelector('span[class*="review-full-text"]')
                        ];
                        
                        for (const element of textElements) {
                            if (element) {
                                selectors.reviewTextSelector = element.tagName.toLowerCase() + 
                                    Array.from(element.classList).map(c => '.' + c).join('');
                                break;
                            }
                        }
                        
                        // More button selector
                        const moreButtons = [
                            firstReview.querySelector('button[jsaction*="pane.review.expandReview"]'),
                            firstReview.querySelector('span[jsaction*="review.expandReview"]'),
                            firstReview.querySelector('button.w8nwRe'),
                            firstReview.querySelector('span.w8nwRe')
                        ];
                        
                        for (const element of moreButtons) {
                            if (element) {
                                selectors.moreButtonSelector = element.tagName.toLowerCase() + 
                                    Array.from(element.classList).map(c => '.' + c).join('');
                                break;
                            }
                        }
                    }
                    
                    // Find the "Next" button for pagination
                    const nextButtons = [
                        document.querySelector('button[aria-label="Next page"]'),
                        document.querySelector('button[jsaction*="pane.review.nextPage"]'),
                        document.querySelector('button[aria-label*="Next"]')
                    ];
                    
                    for (const element of nextButtons) {
                        if (element) {
                            selectors.nextButtonSelector = element.tagName.toLowerCase() + 
                                Array.from(element.classList).map(c => '.' + c).join('');
                            break;
                        }
                    }
                    
                    return selectors;
                }
            """)
            
            logger.debug(f"Extracted selectors: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Error extracting Google selectors: {e}", exc_info=True)
            return {}
    
    def _analyze_selectors(self, all_selectors: List[Dict[str, str]]) -> Dict[str, str]:
        """Analyze collected selectors to find the most reliable ones.
        
        Args:
            all_selectors (List[Dict[str, str]]): List of selector dictionaries.
            
        Returns:
            Dict[str, str]: Best selectors.
        """
        if not all_selectors:
            return {}
        
        # Count occurrences of each selector
        selector_counts = {}
        
        for selector_dict in all_selectors:
            for key, value in selector_dict.items():
                if key not in selector_counts:
                    selector_counts[key] = {}
                
                if value not in selector_counts[key]:
                    selector_counts[key][value] = 0
                
                selector_counts[key][value] += 1
        
        # Choose the most frequent selector for each key
        best_selectors = {}
        
        for key, counts in selector_counts.items():
            if not counts:
                continue
                
            # Find the most frequent selector
            best_selector = max(counts.items(), key=lambda x: x[1])
            
            # Only include if it appeared in multiple samples
            if best_selector[1] >= 2:
                best_selectors[key] = best_selector[0]
        
        logger.info(f"Analysis complete. Found {len(best_selectors)} reliable selectors.")
        return best_selectors


async def run_analysis(output_path: str) -> bool:
    """Run the structure analysis.
    
    Args:
        output_path (str): Path to save analysis results.
        
    Returns:
        bool: Success status.
    """
    try:
        # Create analyzer
        analyzer = StructureAnalyzer()
        
        # Run analysis
        results = await analyzer.analyze_google_structure()
        
        # Save results
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w') as file:
            json.dump(results, file, indent=2)
        
        logger.info(f"Structure analysis saved to {output_path}")
        return results.get("success", False)
        
    except Exception as e:
        logger.error(f"Error running structure analysis: {e}", exc_info=True)
        return False


def update_google_structure(output_path: str = "data/structure_analysis.json") -> bool:
    """Update the Google structure analysis.
    
    Args:
        output_path (str, optional): Path to save analysis results.
        
    Returns:
        bool: Success status.
    """
    try:
        print(f"Starting Google structure analysis...")
        print(f"Results will be saved to: {output_path}")
        
        # Set event loop policy for Windows
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run analysis
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(run_analysis(output_path))
        
        if success:
            print(f"Structure analysis completed successfully!")
        else:
            print(f"Structure analysis failed. Check logs for details.")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in update_google_structure: {e}", exc_info=True)
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Update Google structure analysis")
    parser.add_argument("--output", default="data/structure_analysis.json", help="Output path for analysis results")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Run the update
    update_google_structure(args.output)
