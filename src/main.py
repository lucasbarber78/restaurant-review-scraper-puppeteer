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

# Import client manager
from src.utils.client_manager import ClientManager

# Import structure analyzer for maintenance
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
    
    def scrape_platform(self, platform: str) -> List[Dict[str, Any]]:
        """Scrape reviews from a specific platform.
        
        Args:
            platform (str): Platform to scrape ("google", "yelp", or "tripadvisor").
            
        Returns:
            List[Dict[str, Any]]: List of reviews from the specified platform.
        """
        logger.info(f"Starting to scrape {platform} reviews for {self.restaurant_name}")
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.csv_path)), exist_ok=True)
        
        # Create event loop
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()
        
        platform_reviews = []
        
        # Scrape reviews from the selected platform
        if platform.lower() == "google":
            logger.info("Starting Google Reviews scraper")
            google_scraper = GoogleReviewScraper(config_path="config.yaml", client_config=self._create_client_config())
            platform_reviews = loop.run_until_complete(google_scraper.scrape_reviews())
            logger.info(f"Collected {len(platform_reviews)} reviews from Google")
        elif platform.lower() == "yelp":
            logger.info("Starting Yelp scraper")
            yelp_scraper = YelpReviewScraper(config_path="config.yaml", client_config=self._create_client_config())
            platform_reviews = loop.run_until_complete(yelp_scraper.scrape_reviews())
            logger.info(f"Collected {len(platform_reviews)} reviews from Yelp")
        elif platform.lower() == "tripadvisor":
            logger.info("Starting TripAdvisor scraper")
            tripadvisor_scraper = TripAdvisorReviewScraper(config_path="config.yaml", client_config=self._create_client_config())
            platform_reviews = loop.run_until_complete(tripadvisor_scraper.scrape_reviews())
            logger.info(f"Collected {len(platform_reviews)} reviews from TripAdvisor")
        else:
            logger.error(f"Unknown platform: {platform}")
            return []
        
        # Add to reviews collection
        self.reviews.extend(platform_reviews)
        
        # Categorize and analyze reviews
        self._categorize_reviews()
        self._analyze_sentiment()
        
        # Save results
        self._save_to_csv()
        
        logger.info(f"Successfully collected a total of {len(self.reviews)} reviews")
        return platform_reviews
    
    def _create_client_config(self) -> Dict[str, Any]:
        """Create a client configuration dictionary from current settings.
        
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
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Restaurant Review Scraper")
    
    # Main options
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced anti-bot detection")
    parser.add_argument("--platform", type=str, choices=["google", "yelp", "tripadvisor"], 
                        help="Scrape only a specific platform")
    parser.add_argument("--max-reviews", type=int, help="Maximum number of reviews to scrape per platform")
    parser.add_argument("--config", type=str, default="config.yaml", 
                        help="Path to configuration file (default: config.yaml)")
    
    # Batch processing options
    parser.add_argument("--batch", action="store_true", help="Process all clients in batch mode")
    parser.add_argument("--client", type=str, help="Process a specific client by name")
    parser.add_argument("--clients-file", type=str, default="clients.json", 
                        help="Path to clients file (default: clients.json)")
    
    # Anti-bot options
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (less visible but more detectable)")
    parser.add_argument("--no-stealth", action="store_true", help="Disable stealth plugins (not recommended)")
    parser.add_argument("--no-random-delays", action="store_true", help="Disable random delays (not recommended)")
    parser.add_argument("--enable-proxy-rotation", action="store_true", help="Enable proxy rotation if configured")
    
    # Structure analysis options
    parser.add_argument("--update-structure", action="store_true", 
                        help="Update the structure analysis before scraping")
    parser.add_argument("--no-structure-analysis", action="store_true", 
                        help="Disable structure-based scraping and use hardcoded selectors")
    
    # Misc options
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    return parser.parse_args()


def update_config_with_args(config, args):
    """Update configuration with command line arguments.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary.
        args (argparse.Namespace): Parsed arguments.
    
    Returns:
        Dict[str, Any]: Updated configuration.
    """
    # Set debugging level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Update max reviews if specified
    if args.max_reviews:
        config["max_reviews_per_platform"] = args.max_reviews
    
    # Update anti-bot settings
    if "anti_bot_settings" not in config:
        config["anti_bot_settings"] = {}
    
    if args.enhanced:
        # Enable enhanced anti-bot detection
        config["anti_bot_settings"]["enable_random_delays"] = not args.no_random_delays
        config["anti_bot_settings"]["enable_stealth_plugins"] = not args.no_stealth
        config["anti_bot_settings"]["headless_mode"] = args.headless
        config["anti_bot_settings"]["simulate_human_behavior"] = True
        config["anti_bot_settings"]["enable_proxy_rotation"] = args.enable_proxy_rotation
    
    # Update Google scraper settings
    if "google_scraper" not in config:
        config["google_scraper"] = {}
    
    config["google_scraper"]["use_structure_analysis"] = not args.no_structure_analysis
    
    return config


def process_client(client_config, args, config_path="config.yaml"):
    """Process a single client.
    
    Args:
        client_config (Dict[str, Any]): Client configuration.
        args (argparse.Namespace): Parsed arguments.
        config_path (str, optional): Path to configuration file. Defaults to "config.yaml".
    
    Returns:
        int: Number of reviews scraped.
    """
    try:
        # Load base configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update configuration with arguments
        config = update_config_with_args(config, args)
        
        # Create scraper with client configuration
        scraper = RestaurantReviewScraper(config_path=config_path, client_config=client_config)
        
        print(f"\nProcessing client: {client_config['name']}")
        
        # Scrape reviews
        if args.platform:
            reviews = scraper.scrape_platform(args.platform)
        else:
            reviews = scraper.scrape_all_platforms()
        
        # Print statistics
        scraper.print_stats()
        
        print(f"\nResults for {client_config['name']} saved to: {scraper.csv_path}")
        
        return len(reviews)
    
    except Exception as e:
        logger.error(f"Error processing client {client_config['name']}: {e}", exc_info=True)
        print(f"\nError processing client {client_config['name']}: {e}")
        return 0


def main():
    """Main function to run the restaurant review scraper."""
    print("=" * 80)
    print("Restaurant Review Scraper (Puppeteer Edition)")
    print("=" * 80)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Update structure analysis if requested
    if args.update_structure:
        print("\nUpdating structure analysis...")
        asyncio.run(update_structure_if_needed())
    
    try:
        # Check if we're in batch mode
        if args.batch or args.client:
            # Load clients
            client_manager = ClientManager(args.clients_file)
            
            if args.client:
                # Process a specific client
                client = client_manager.get_client_by_name(args.client)
                if not client:
                    print(f"Client '{args.client}' not found. Available clients:")
                    for c in client_manager.clients:
                        print(f"- {c['name']}")
                    return
                
                process_client(client, args, args.config)
            else:
                # Process all active clients
                active_clients = client_manager.get_active_clients()
                
                if not active_clients:
                    print("No active clients found. Please add clients to the clients file.")
                    return
                
                print(f"Found {len(active_clients)} active clients")
                
                total_reviews = 0
                for client in active_clients:
                    review_count = process_client(client, args, args.config)
                    total_reviews += review_count
                    
                    # Add delay between clients
                    if client != active_clients[-1]:
                        print("\nPausing between clients to avoid detection...")
                        time.sleep(10)
                
                print(f"\nTotal reviews collected across all clients: {total_reviews}")
        else:
            # Load configuration
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update configuration with arguments
            config = update_config_with_args(config, args)
            
            # Process single restaurant from config
            scraper = RestaurantReviewScraper(config_path=args.config)
            
            print(f"\nScraping reviews for: {scraper.restaurant_name}")
            
            # Scrape reviews
            if args.platform:
                reviews = scraper.scrape_platform(args.platform)
            else:
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
