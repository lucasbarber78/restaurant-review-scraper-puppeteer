#!/usr/bin/env python3
"""
Restaurant Review Scraper - Main Module

This module coordinates the scraping of restaurant reviews from TripAdvisor, Yelp, and Google Reviews.
"""

import os
import logging
import asyncio
import yaml
import csv
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import scrapers
from src.tripadvisor_scraper import TripAdvisorReviewScraper
from src.yelp_scraper import YelpReviewScraper
from src.google_scraper import GoogleReviewScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RestaurantReviewScraper:
    """Main class to coordinate restaurant review scraping."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the restaurant review scraper.
        
        Args:
            config_path (str, optional): Path to the configuration file. 
                Defaults to "config.yaml".
        """
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Get restaurant details
        self.restaurant_name = self.config.get("restaurant_name", "")
        
        # Output file
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
        # Initialize review collection
        self.reviews = []
        
        logger.info(f"Initialized Restaurant Review Scraper for {self.restaurant_name}")
    
    def scrape_all_platforms(self) -> List[Dict[str, Any]]:
        """Scrape reviews from all platforms.
        
        Returns:
            List[Dict[str, Any]]: Combined list of reviews from all platforms.
        """
        logger.info(f"Starting to scrape reviews for {self.restaurant_name} from all platforms")
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.csv_path)), exist_ok=True)
        
        # Create event loop
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()
        
        # Scrape reviews from TripAdvisor
        logger.info("Starting TripAdvisor scraper")
        tripadvisor_scraper = TripAdvisorReviewScraper()
        tripadvisor_reviews = loop.run_until_complete(tripadvisor_scraper.scrape_reviews())
        logger.info(f"Collected {len(tripadvisor_reviews)} reviews from TripAdvisor")
        self.reviews.extend(tripadvisor_reviews)
        
        # Wait a bit between platforms to avoid detection
        time.sleep(5)
        
        # Scrape reviews from Yelp
        logger.info("Starting Yelp scraper")
        yelp_scraper = YelpReviewScraper()
        yelp_reviews = loop.run_until_complete(yelp_scraper.scrape_reviews())
        logger.info(f"Collected {len(yelp_reviews)} reviews from Yelp")
        self.reviews.extend(yelp_reviews)
        
        # Wait a bit between platforms to avoid detection
        time.sleep(5)
        
        # Scrape reviews from Google
        logger.info("Starting Google Reviews scraper")
        google_scraper = GoogleReviewScraper()
        google_reviews = loop.run_until_complete(google_scraper.scrape_reviews())
        logger.info(f"Collected {len(google_reviews)} reviews from Google")
        self.reviews.extend(google_reviews)
        
        # Categorize and analyze reviews
        self._categorize_reviews()
        self._analyze_sentiment()
        
        # Save combined results
        self._save_to_csv()
        
        logger.info(f"Successfully collected a total of {len(self.reviews)} reviews")
        return self.reviews
    
    def _categorize_reviews(self) -> None:
        """Categorize reviews based on their content."""
        logger.info("Categorizing reviews")
        
        # Get category keywords from config
        category_keywords = self.config.get("category_keywords", {})
        
        # Categorize each review
        for review in self.reviews:
            review_text = review.get("text", "").lower()
            
            highest_match_count = 0
            best_category = "Uncategorized"
            
            # Check each category
            for category, keywords in category_keywords.items():
                match_count = sum(1 for keyword in keywords if keyword.lower() in review_text)
                
                if match_count > highest_match_count:
                    highest_match_count = match_count
                    best_category = category
            
            # Assign category
            review["category"] = best_category
        
        logger.info("Reviews categorized successfully")
    
    def _analyze_sentiment(self) -> None:
        """Perform simple sentiment analysis on reviews."""
        logger.info("Analyzing review sentiment")
        
        # Simple sentiment analysis based on rating
        for review in self.reviews:
            rating = review.get("rating", 0)
            
            # Determine sentiment based on rating
            if rating >= 4:
                sentiment = "Positive"
            elif rating >= 3:
                sentiment = "Neutral"
            else:
                sentiment = "Negative"
            
            # Assign sentiment
            review["sentiment"] = sentiment
        
        logger.info("Sentiment analysis completed")
    
    def _save_to_csv(self) -> None:
        """Save all reviews to a single CSV file."""
        if not self.reviews:
            logger.warning("No reviews to save")
            return
        
        # Define field names
        fieldnames = [
            "platform", "restaurant_name", "reviewer_name", 
            "rating", "date", "standardized_date", 
            "text", "category", "sentiment"
        ]
        
        # Write to CSV
        try:
            with open(self.csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.reviews)
                
            logger.info(f"Successfully saved {len(self.reviews)} reviews to {self.csv_path}")
            
        except Exception as e:
            logger.error(f"Error saving reviews to CSV: {e}", exc_info=True)
    
    def generate_stats(self) -> Dict[str, Any]:
        """Generate statistics about the collected reviews.
        
        Returns:
            Dict[str, Any]: Dictionary of statistics.
        """
        if not self.reviews:
            logger.warning("No reviews to generate statistics from")
            return {}
        
        stats = {
            "restaurant_name": self.restaurant_name,
            "total_reviews": len(self.reviews),
            "platforms": {},
            "categories": {},
            "sentiment": {},
            "average_rating": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
        # Calculate statistics
        total_rating = 0
        
        for review in self.reviews:
            # Platform stats
            platform = review.get("platform", "Unknown")
            if platform not in stats["platforms"]:
                stats["platforms"][platform] = 0
            stats["platforms"][platform] += 1
            
            # Category stats
            category = review.get("category", "Uncategorized")
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1
            
            # Sentiment stats
            sentiment = review.get("sentiment", "Unknown")
            if sentiment not in stats["sentiment"]:
                stats["sentiment"][sentiment] = 0
            stats["sentiment"][sentiment] += 1
            
            # Rating stats
            rating = review.get("rating", 0)
            total_rating += rating
            
            # Rating distribution
            rounded_rating = round(rating)
            if 1 <= rounded_rating <= 5:
                stats["rating_distribution"][rounded_rating] += 1
        
        # Calculate average rating
        if stats["total_reviews"] > 0:
            stats["average_rating"] = total_rating / stats["total_reviews"]
        
        return stats
    
    def print_stats(self) -> None:
        """Print statistics about the collected reviews."""
        stats = self.generate_stats()
        
        if not stats:
            print("No statistics available")
            return
        
        print(f"\n=== REVIEW STATISTICS FOR {stats['restaurant_name']} ===")
        print(f"Total Reviews: {stats['total_reviews']}")
        print(f"Average Rating: {stats['average_rating']:.1f}/5.0")
        
        print("\nReviews by Platform:")
        for platform, count in stats["platforms"].items():
            print(f"  {platform}: {count} ({count/stats['total_reviews']*100:.1f}%)")
        
        print("\nReviews by Category:")
        for category, count in stats["categories"].items():
            print(f"  {category}: {count} ({count/stats['total_reviews']*100:.1f}%)")
        
        print("\nSentiment Analysis:")
        for sentiment, count in stats["sentiment"].items():
            print(f"  {sentiment}: {count} ({count/stats['total_reviews']*100:.1f}%)")
        
        print("\nRating Distribution:")
        for rating, count in sorted(stats["rating_distribution"].items()):
            print(f"  {rating} Stars: {count} ({count/stats['total_reviews']*100:.1f}%)")
        
        print("\nReview collection completed!")


def main():
    """Main function to run the restaurant review scraper."""
    print("=" * 80)
    print("Restaurant Review Scraper (Puppeteer Edition)")
    print("=" * 80)
    
    try:
        # Create scraper
        scraper = RestaurantReviewScraper()
        
        # Scrape all platforms
        print(f"\nScraping reviews for: {scraper.restaurant_name}")
        reviews = scraper.scrape_all_platforms()
        
        # Print statistics
        scraper.print_stats()
        
        print(f"\nResults saved to: {scraper.csv_path}")
        print("\nScraping completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Check scraper.log for details")


if __name__ == "__main__":
    main()
