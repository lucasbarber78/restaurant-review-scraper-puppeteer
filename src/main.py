#!/usr/bin/env python3
"""
Restaurant Review Scraper - Main Module

This module coordinates the scraping of restaurant reviews from TripAdvisor, Yelp, and Google Reviews.
It supports batch processing of multiple restaurant clients and dynamic structure analysis.
"""

import os
import logging
import asyncio
import yaml
import csv
import time
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import scrapers
from src.tripadvisor_scraper import TripAdvisorReviewScraper
from src.yelp_scraper import YelpReviewScraper
from src.google_scraper import GoogleReviewScraper

# Import utility modules
from src.utils.client_manager import ClientManager
from src.utils.structure_analyzer import update_structure_if_needed

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
    
    def __init__(self, config_path: str = "config.yaml", client_config: Dict[str, Any] = None):
        """Initialize the restaurant review scraper.
        
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
            
            # Update URLs
            if "google_url" in client_config:
                self.config["google_url"] = client_config["google_url"]
            if "yelp_url" in client_config:
                self.config["yelp_url"] = client_config["yelp_url"]
            if "tripadvisor_url" in client_config:
                self.config["tripadvisor_url"] = client_config["tripadvisor_url"]
            
            # Set client-specific output file
            client_name_safe = self.restaurant_name.replace(" ", "_").lower()
            self.csv_path = f"reviews_{client_name_safe}.csv"
        else:
            self.restaurant_name = self.config.get("restaurant_name", "")
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
        tripadvisor_scraper = TripAdvisorReviewScraper(config_path="config.yaml", client_config=self._create_client_config())
        tripadvisor_reviews = loop.run_until_complete(tripadvisor_scraper.scrape_reviews())
        logger.info(f"Collected {len(tripadvisor_reviews)} reviews from TripAdvisor")
        self.reviews.extend(tripadvisor_reviews)
        
        # Wait a bit between platforms to avoid detection
        time.sleep(5)
        
        # Scrape reviews from Yelp
        logger.info("Starting Yelp scraper")
        yelp_scraper = YelpReviewScraper(config_path="config.yaml", client_config=self._create_client_config())
        yelp_reviews = loop.run_until_complete(yelp_scraper.scrape_reviews())
        logger.info(f"Collected {len(yelp_reviews)} reviews from Yelp")
        self.reviews.extend(yelp_reviews)
        
        # Wait a bit between platforms to avoid detection
        time.sleep(5)
        
        # Scrape reviews from Google
        logger.info("Starting Google Reviews scraper")
        google_scraper = GoogleReviewScraper(config_path="config.yaml", client_config=self._create_client_config())
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
    
    def _create_client_config(self) -> Dict[str, Any]:
        """Create a client configuration dictionary from the current settings.
        
        Returns:
            Dict[str, Any]: Client configuration dictionary.
        """
        return {
            "name": self.restaurant_name,
            "google_url": self.config.get("google_url", ""),
            "yelp_url": self.config.get("yelp_url", ""),
            "tripadvisor_url": self.config.get("tripadvisor_url", "")
        }
    
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


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Restaurant Review Scraper (Puppeteer Edition)")
    
    # Add arguments
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced anti-bot detection features")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file")
    parser.add_argument("--client", type=str, help="Specific client name to scrape (from clients.json)")
    parser.add_argument("--all-clients", action="store_true", help="Scrape all active clients")
    parser.add_argument("--platform", type=str, choices=["google", "yelp", "tripadvisor", "all"], 
                      default="all", help="Specific platform to scrape")
    parser.add_argument("--max-reviews", type=int, help="Maximum number of reviews to scrape per platform")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--no-stealth", action="store_true", help="Disable stealth plugins")
    parser.add_argument("--no-random-delays", action="store_true", help="Disable random delays")
    parser.add_argument("--enable-proxy-rotation", action="store_true", help="Enable proxy rotation")
    parser.add_argument("--update-structure", action="store_true", 
                      help="Update structure analysis before scraping")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()


def main():
    """Main function to run the restaurant review scraper."""
    print("=" * 80)
    print("Restaurant Review Scraper (Puppeteer Edition)")
    print("=" * 80)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Update structure analysis if requested
        if args.update_structure:
            print("Updating Google review structure analysis...")
            asyncio.run(update_structure_if_needed())
            print("Structure analysis updated successfully")
        
        # Process a single client or all clients
        if args.all_clients:
            process_all_clients(args)
        elif args.client:
            process_single_client(args.client, args)
        else:
            # No client specified, use config.yaml
            process_default_client(args)
        
        print("\nScraping completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Check scraper.log for details")


def process_all_clients(args):
    """Process all active clients from clients.json."""
    # Load clients
    client_manager = ClientManager()
    active_clients = client_manager.get_active_clients()
    
    if not active_clients:
        print("No active clients found. Please add clients to clients.json")
        return
    
    print(f"Found {len(active_clients)} active clients")
    
    # Process each client
    for client_config in active_clients:
        print(f"\nProcessing client: {client_config['name']}")
        
        # Modify config with command line arguments
        update_client_config_with_args(client_config, args)
        
        # Create scraper with client-specific settings
        scraper = RestaurantReviewScraper(config_path=args.config, client_config=client_config)
        
        # Scrape all platforms
        reviews = scraper.scrape_all_platforms()
        
        # Print statistics
        scraper.print_stats()
        
        print(f"\nResults for {client_config['name']} saved to: {scraper.csv_path}")
        
        # Wait between clients to avoid detection
        if client_config != active_clients[-1]:
            print("Waiting before processing next client...")
            time.sleep(10)


def process_single_client(client_name, args):
    """Process a single client by name."""
    # Load clients
    client_manager = ClientManager()
    client_config = client_manager.get_client_by_name(client_name)
    
    if not client_config:
        print(f"Client '{client_name}' not found. Please check clients.json")
        return
    
    print(f"Processing client: {client_config['name']}")
    
    # Modify config with command line arguments
    update_client_config_with_args(client_config, args)
    
    # Create scraper with client-specific settings
    scraper = RestaurantReviewScraper(config_path=args.config, client_config=client_config)
    
    # Scrape all platforms
    reviews = scraper.scrape_all_platforms()
    
    # Print statistics
    scraper.print_stats()
    
    print(f"\nResults for {client_config['name']} saved to: {scraper.csv_path}")


def process_default_client(args):
    """Process the default client from config.yaml."""
    # Create scraper
    scraper = RestaurantReviewScraper(config_path=args.config)
    
    # Scrape all platforms
    print(f"\nScraping reviews for: {scraper.restaurant_name}")
    reviews = scraper.scrape_all_platforms()
    
    # Print statistics
    scraper.print_stats()
    
    print(f"\nResults saved to: {scraper.csv_path}")


def update_client_config_with_args(client_config, args):
    """Update client configuration with command line arguments."""
    # Update anti-bot settings
    if "anti_bot_settings" not in client_config:
        client_config["anti_bot_settings"] = {}
    
    if args.headless:
        client_config["anti_bot_settings"]["headless_mode"] = True
    
    if args.no_stealth:
        client_config["anti_bot_settings"]["enable_stealth_plugins"] = False
    
    if args.no_random_delays:
        client_config["anti_bot_settings"]["enable_random_delays"] = False
    
    if args.enable_proxy_rotation:
        client_config["anti_bot_settings"]["enable_proxy_rotation"] = True
    
    # Update max reviews
    if args.max_reviews:
        client_config["max_reviews_per_platform"] = args.max_reviews


if __name__ == "__main__":
    main()
