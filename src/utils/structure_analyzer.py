#!/usr/bin/env python3
"""
Structure Analyzer Module

This module provides utilities for analyzing and updating the structure of Google review pages.
The analysis is stored in a JSON file that can be used by the scraper to dynamically adapt to
changes in Google's DOM structure.
"""

import os
import json
import logging
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from src.utils.browser_utils import create_browser_session, close_browser_session, take_screenshot
from src.utils.delay_utils import async_delay_between_actions
from src.utils.stealth_plugins import apply_stealth_measures

logger = logging.getLogger(__name__)

class StructureAnalyzer:
    def __init__(self, 
                 output_dir: str = "Review Site Optimization", 
                 output_file: str = "google_search_review_structure_analysis.json",
                 log_file: str = "structure_update_log.json"):
        """
        Initialize the structure analyzer.
        
        Args:
            output_dir (str): Directory to save the structure analysis file
            output_file (str): Name of the structure analysis file
            log_file (str): Path to the update log file
        """
        self.output_dir = output_dir
        self.output_file = output_file
        self.output_path = os.path.join(output_dir, output_file)
        self.log_file = log_file
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    async def analyze_google_review_structure(self, search_term: str = "Bowens Island Restaurant Reviews") -> Optional[Dict[str, Any]]:
        """
        Analyze the structure of Google review results for a given search term.
        
        Args:
            search_term (str): The search term to use
            
        Returns:
            Optional[Dict[str, Any]]: The structure analysis or None if unsuccessful
        """
        browser = None
        page = None
        
        try:
            # Initialize browser with anti-bot measures
            browser_options = {
                "headless": False,  # Use visible browser to reduce detection
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1280,800"
                ]
            }
            
            logger.info(f"Initializing browser for structure analysis of '{search_term}'")
            browser, page = create_browser_session(browser_options)
            
            # Apply stealth measures to avoid detection
            logger.info("Applying stealth measures")
            stealth_enhancer = await apply_stealth_measures(page, "google")
            
            # Add human-like delay
            await async_delay_between_actions("waiting")
            
            # Navigate to Google search with the search term
            search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            logger.info(f"Navigating to search URL: {search_url}")
            await page.goto(search_url, {"waitUntil": "networkidle0"})
            
            # Add another delay for content to fully load
            await async_delay_between_actions("navigation")
            
            # Simulate human behavior
            logger.info("Simulating human behavior")
            await stealth_enhancer.simulate_human_behavior(page)
            
            # Take a screenshot for verification
            screenshots_dir = os.path.join(self.output_dir, "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshots_dir, f"google_structure_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            await take_screenshot(page, screenshot_path)
            logger.info(f"Saved screenshot to {screenshot_path}")
            
            # Analyze review structure
            logger.info("Analyzing page structure")
            structure_analysis = await page.evaluate("""
            () => {
                const result = {
                    timestamp: new Date().toISOString(),
                    searchUrl: window.location.href,
                    initialReviewStructure: {
                        reviews: [],
                        moreReviewsButtons: [],
                        sortOptions: [],
                        overallRating: null,
                        totalReviewCount: null
                    }
                };
                
                // Find review elements using various selectors
                const findReviewElements = () => {
                    const possibleSelectors = [
                        'div[data-review-id]',
                        '.review-container',
                        'div[role="listitem"]',
                        'div.wDYxhc[data-attrid*="review"]',
                        'div.WpKAof',
                        'div[jscontroller] > div.lN6TS',
                        'div.wDYxhc',
                        'div.Jb0Zif .wDYxhc',
                        'div.kp-wholepage .wDYxhc'
                    ];
                    
                    for (const selector of possibleSelectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements && elements.length > 0) {
                            return Array.from(elements).slice(0, 5); // Limit to 5 for analysis
                        }
                    }
                    return [];
                };
                
                // Helper functions to build element paths and get attributes
                function getTagPath(element, maxDepth = 5) {
                    let path = element.tagName.toLowerCase();
                    let current = element;
                    let depth = 0;
                    
                    while (current.parentElement && depth < maxDepth) {
                        current = current.parentElement;
                        path = current.tagName.toLowerCase() + ' > ' + path;
                        depth++;
                    }
                    
                    return path;
                }
                
                function getAttributes(element) {
                    const attributes = {};
                    for (const attr of element.attributes) {
                        attributes[attr.name] = attr.value;
                    }
                    return attributes;
                }
                
                // Find specific elements within a review
                function findReviewerName(element) {
                    const nameSelectors = [
                        '.d4r55',
                        '.info_text div',
                        '.member_info .username',
                        '.y3Ibjb',
                        '.YQVn7d'
                    ];
                    
                    for (const selector of nameSelectors) {
                        const nameElement = element.querySelector(selector);
                        if (nameElement) {
                            return {
                                text: nameElement.textContent.trim(),
                                tagPath: getTagPath(nameElement),
                                attributes: getAttributes(nameElement)
                            };
                        }
                    }
                    
                    return null;
                }
                
                function findRating(element) {
                    const ratingSelectors = [
                        'span[role="img"]',
                        'div[aria-label*="star"]',
                        'g-review-stars',
                        '.KFi5wf'
                    ];
                    
                    for (const selector of ratingSelectors) {
                        const ratingElement = element.querySelector(selector);
                        if (ratingElement) {
                            return {
                                element: getTagPath(ratingElement),
                                attributes: getAttributes(ratingElement),
                                text: ratingElement.textContent.trim(),
                                ariaLabel: ratingElement.getAttribute('aria-label')
                            };
                        }
                    }
                    
                    return null;
                }
                
                function findDate(element) {
                    const dateSelectors = [
                        '.y3Ibjb',
                        '.ratingDate',
                        '.date',
                        '.rsqaWe'
                    ];
                    
                    for (const selector of dateSelectors) {
                        const dateElement = element.querySelector(selector);
                        if (dateElement) {
                            return {
                                text: dateElement.textContent.trim(),
                                tagPath: getTagPath(dateElement),
                                attributes: getAttributes(dateElement)
                            };
                        }
                    }
                    
                    return null;
                }
                
                function findReviewText(element) {
                    const textSelectors = [
                        '.wiI7pd',
                        '.prw_reviews_text_summary_hsx p',
                        '.partial_entry',
                        '.review-content p',
                        '.review-full-text',
                        'span[data-expandable-section]'
                    ];
                    
                    for (const selector of textSelectors) {
                        const textElement = element.querySelector(selector);
                        if (textElement) {
                            return {
                                text: textElement.textContent.trim().substring(0, 100) + '...',
                                tagPath: getTagPath(textElement),
                                attributes: getAttributes(textElement)
                            };
                        }
                    }
                    
                    return null;
                }
                
                // Analyze each review element
                function analyzeElement(element) {
                    const tagPath = getTagPath(element);
                    return {
                        elementInfo: {
                            tagPath: tagPath,
                            attributes: getAttributes(element),
                            innerText: element.innerText.substring(0, 200) + (element.innerText.length > 200 ? '...' : ''),
                            innerHTML: element.innerHTML.substring(0, 200) + (element.innerHTML.length > 200 ? '...' : ''),
                            boundingBox: {},
                            childCount: element.children.length
                        },
                        reviewerName: findReviewerName(element),
                        rating: findRating(element),
                        date: findDate(element),
                        reviewText: findReviewText(element)
                    };
                }
                
                // Find overall rating
                const ratingElements = document.querySelectorAll('.review-score, .rating, .rev_slider, .YQ4gaf');
                if (ratingElements.length > 0) {
                    const element = ratingElements[0];
                    result.initialReviewStructure.overallRating = {
                        value: element.textContent.trim(),
                        element: getTagPath(element),
                        attributes: getAttributes(element)
                    };
                }
                
                // Find total review count
                const countElements = document.querySelectorAll('.reviews_header_count, .review-count, .KFi5wf, .hqzQac');
                if (countElements.length > 0) {
                    const element = countElements[0];
                    result.initialReviewStructure.totalReviewCount = {
                        count: element.textContent.trim().replace(/[^0-9]/g, ''),
                        element: getTagPath(element),
                        text: element.textContent.trim()
                    };
                }
                
                // Find review elements and analyze them
                const reviewElements = findReviewElements();
                result.initialReviewStructure.reviews = reviewElements.map(analyzeElement);
                
                // Find buttons for loading more reviews
                const moreButtons = document.querySelectorAll('button[aria-label*="more"], a.next-link, a[class*="next"], .more-reviews');
                if (moreButtons.length > 0) {
                    result.initialReviewStructure.moreReviewsButtons = Array.from(moreButtons).slice(0, 3).map(button => {
                        return {
                            tagPath: getTagPath(button),
                            attributes: getAttributes(button),
                            text: button.textContent.trim()
                        };
                    });
                }
                
                // Find sort options
                const sortOptions = document.querySelectorAll('select[aria-label*="sort"], .sort-options, .BTtC6e');
                if (sortOptions.length > 0) {
                    result.initialReviewStructure.sortOptions = Array.from(sortOptions).slice(0, 2).map(option => {
                        return {
                            tagPath: getTagPath(option),
                            attributes: getAttributes(option),
                            options: Array.from(option.querySelectorAll('option')).map(opt => opt.textContent.trim())
                        };
                    });
                }
                
                return result;
            }
            """)
            
            # Save the structure analysis
            logger.info(f"Saving structure analysis to {self.output_path}")
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(structure_analysis, f, indent=2)
            
            # Update the log file
            self._update_log()
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Google review structure: {e}", exc_info=True)
            return None
            
        finally:
            # Always close the browser
            if browser:
                logger.info("Closing browser")
                await close_browser_session(browser)
    
    def _update_log(self) -> None:
        """Update the structure update log file."""
        try:
            log_data = {
                "last_update": datetime.now().isoformat(),
                "update_count": 1
            }
            
            # Read existing log if it exists
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        existing_log = json.load(f)
                        log_data["update_count"] = existing_log.get("update_count", 0) + 1
                except:
                    pass
            
            # Write updated log
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2)
                
            logger.info(f"Updated structure update log: {log_data}")
                
        except Exception as e:
            logger.error(f"Error updating structure log: {e}")
    
    def should_update_structure(self, min_days: int = 7, max_days: int = 14) -> bool:
        """
        Determine if we should update the structure analysis.
        
        Args:
            min_days (int): Minimum days between updates
            max_days (int): Maximum days between updates
            
        Returns:
            bool: True if structure should be updated, False otherwise
        """
        try:
            # If log file doesn't exist, we should update
            if not os.path.exists(self.log_file):
                logger.info("No update log found, structure update needed")
                return True
            
            # Read the log file
            with open(self.log_file, "r", encoding='utf-8') as f:
                log = json.load(f)
                last_update = datetime.fromisoformat(log["last_update"])
            
            # Calculate days since last update
            days_since_update = (datetime.now() - last_update).days
            
            # Always update if we're past max_days
            if days_since_update > max_days:
                logger.info(f"Last update was {days_since_update} days ago (> {max_days}), update needed")
                return True
            
            # Don't update if we're before min_days
            if days_since_update < min_days:
                logger.info(f"Last update was only {days_since_update} days ago (< {min_days}), no update needed")
                return False
            
            # Random decision based on probability that increases with time
            update_probability = (days_since_update - min_days) / (max_days - min_days)
            should_update = random.random() < update_probability
            
            logger.info(f"Last update was {days_since_update} days ago, probability {update_probability:.2f}, " + 
                       f"{'update needed' if should_update else 'no update needed'}")
            
            return should_update
            
        except Exception as e:
            logger.error(f"Error checking if structure update needed: {e}")
            # If there's any error, assume we should update
            return True

async def update_structure_if_needed():
    """Update the Google review structure if needed."""
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("Checking if Google review structure needs updating")
    analyzer = StructureAnalyzer()
    
    if analyzer.should_update_structure():
        logger.info("Structure update needed, starting analysis")
        await analyzer.analyze_google_review_structure()
        logger.info("Structure analysis completed")
    else:
        logger.info("No structure update needed at this time")

if __name__ == "__main__":
    asyncio.run(update_structure_if_needed())
