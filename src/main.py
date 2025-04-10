#!/usr/bin/env python3
"""
Restaurant Review Scraper - Main Module

This module coordinates the scraping of restaurant reviews from TripAdvisor, Yelp, and Google Reviews.
It now supports batch processing of multiple restaurant clients and uses structure-based scrapers
for improved resilience to website changes.
"""

import os
import logging
import asyncio
import yaml
import csv
import json
import time
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Import structure-based scrapers
from src.tripadvisor_structure_scraper import TripAdvisorStructureScraper
from src.yelp_structure_scraper import YelpStructureScraper
from src.google_structure_scraper import GoogleStructureScraper

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
    
    def __init__(self, config_path: str = "config.yaml", client_config: Dict = None):
        """Initialize the restaurant review scraper.
        
        Args:
            config_path (str, optional): Path to the configuration file. 
                Defaults to "config.yaml".
            client_config (Dict, optional): Client-specific configuration that
                overrides the default config. Defaults to None.
        """
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Override with client-specific configuration if provided
        if client_config:
            # Deep merge client config with default config
            self._merge_config(client_config)
        
        # Get restaurant details
        self.restaurant_name = self.config.get("restaurant_name", "")
        
        # Output file
        self.csv_path = self.config.get("csv_file_path", "reviews.csv")
        
        # Anti-bot settings
        self.use_enhanced = self.config.get("use_enhanced", False)
        
        # Structure analysis settings
        self.structure_analysis_path = self.config.get("structure_analysis_path", "structure_analysis.json")
        
        # Initialize review collection
        self.reviews = []
        
        logger.info(f"Initialized Restaurant Review Scraper for {self.restaurant_name}")
    
    def _merge_config(self, client_config: Dict) -> None:
        """Deep merge client config with default config.
        
        Args:
            client_config (Dict): Client-specific configuration.
        """
        for key, value in client_config.items():
            if isinstance(value, dict) and key in self.config and isinstance(self.config[key], dict):
                # Recursively merge nested dictionaries
                self._merge_config_dict(self.config[key], value)
            else:
                # Override or add key-value pair
                self.config[key] = value
        
        logger.debug(f"Configuration merged with client-specific settings")
    
    def _merge_config_dict(self, target: Dict, source: Dict) -> None:
        """Helper method to recursively merge dictionaries.
        
        Args:
            target (Dict): Target dictionary to merge into.
            source (Dict): Source dictionary to merge from.
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                # Recursively merge nested dictionaries
                self._merge_config_dict(target[key], value)
            else:
                # Override or add key-value pair
                target[key] = value
    
    def scrape_all_platforms(self) -> List[Dict[str, Any]]:
        """Scrape reviews from all platforms.
        
        Returns:
            List[Dict[str, Any]]: Combined list of reviews from all platforms.
        """
        logger.info(f"Starting to scrape reviews for {self.restaurant_name} from all platforms")
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.csv_path)), exist_ok=True)
        
        # Create event loop
        if os.name == 'nt':  # Windows
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()
        
        # Get platforms to scrape
        platforms = self.config.get("platforms_to_scrape", ["tripadvisor", "yelp", "google"])
        
        # Scrape reviews from TripAdvisor
        if "tripadvisor" in platforms:
            logger.info("Starting TripAdvisor structure scraper")
            tripadvisor_scraper = TripAdvisorStructureScraper(config_path=None, config_dict=self.config)
            tripadvisor_reviews = loop.run_until_complete(tripadvisor_scraper.scrape_reviews())
            logger.info(f"Collected {len(tripadvisor_reviews)} reviews from TripAdvisor")
            self.reviews.extend(tripadvisor_reviews)
            
            # Wait a bit between platforms to avoid detection
            time.sleep(5)
        
        # Scrape reviews from Yelp
        if "yelp" in platforms:
            logger.info("Starting Yelp structure scraper")
            yelp_scraper = YelpStructureScraper(config_path=None, config_dict=self.config)
            yelp_reviews = loop.run_until_complete(yelp_scraper.scrape_reviews())
            logger.info(f"Collected {len(yelp_reviews)} reviews from Yelp")
            self.reviews.extend(yelp_reviews)
            
            # Wait a bit between platforms to avoid detection
            time.sleep(5)
        
        # Scrape reviews from Google
        if "google" in platforms:
            logger.info("Starting Google structure scraper")
            google_scraper = GoogleStructureScraper(config_path=None, config_dict=self.config)
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


def update_structure_analysis(config):
    """Update structure analysis file.
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        bool: True if structure analysis was updated successfully, False otherwise
    """
    try:
        structure_analysis_path = config.get("structure_analysis_path", "structure_analysis.json")
        logger.info(f"Updating structure analysis at {structure_analysis_path}")
        
        # Import the update_structure module here to avoid circular imports
        from src.update_structure import update_google_structure
        
        # Update the structure analysis
        success = update_google_structure(structure_analysis_path)
        
        if success:
            logger.info("Structure analysis updated successfully")
        else:
            logger.warning("Structure analysis update failed")
        
        return success
    except Exception as e:
        logger.error(f"Error updating structure analysis: {e}", exc_info=True)
        return False


def validate_structure_files(args):
    """Validate structure files against live websites.
    
    Args:
        args (argparse.Namespace): Command line arguments.
        
    Returns:
        bool: True if all validations passed, False otherwise.
    """
    try:
        from src.utils.structure_analyzer import StructureManager
        
        manager = StructureManager()
        results = {}
        
        # Determine which platforms to validate
        platforms = []
        if args.platform == "all":
            platforms = ["tripadvisor", "yelp", "google"]
        else:
            platforms = [args.platform]
        
        print(f"\nValidating structure files for: {', '.join(platforms)}")
        print("=" * 60)
        
        all_valid = True
        for platform in platforms:
            # Check if structure file exists
            if manager.structure_exists(platform):
                # Load structure
                is_loaded = manager.load_structure(platform)
                if is_loaded:
                    # Check if structure needs update
                    needs_update = manager.structure_needs_update(platform)
                    if needs_update:
                        print(f"{platform}: Structure file found but is outdated")
                        all_valid = False
                        results[platform] = "Outdated"
                    else:
                        # Validate structure against required selectors
                        structure = manager.structures[platform]
                        required_selectors = structure.get("validation", {}).get("required_selectors", [])
                        selectors = structure.get("selectors", {})
                        
                        missing_selectors = [sel for sel in required_selectors if sel not in selectors]
                        
                        if missing_selectors:
                            print(f"{platform}: Missing required selectors: {', '.join(missing_selectors)}")
                            all_valid = False
                            results[platform] = "Missing selectors"
                        else:
                            print(f"{platform}: Structure file valid")
                            results[platform] = "Valid"
                else:
                    print(f"{platform}: Structure file found but could not be loaded")
                    all_valid = False
                    results[platform] = "Load failed"
            else:
                print(f"{platform}: Structure file not found")
                all_valid = False
                results[platform] = "Not found"
        
        print("=" * 60)
        print(f"Validation {'succeeded' if all_valid else 'failed'}")
        
        return all_valid
    
    except Exception as e:
        logger.error(f"Error validating structure files: {e}", exc_info=True)
        return False


def load_client_config(client_name, clients_path="clients.json"):
    """Load client-specific configuration.
    
    Args:
        client_name (str): Name of the client to load configuration for
        clients_path (str, optional): Path to clients.json file. Defaults to "clients.json".
        
    Returns:
        Dict: Client configuration dictionary or None if not found
    """
    try:
        # Check if the clients file exists
        if not os.path.exists(clients_path):
            logger.error(f"Clients file not found: {clients_path}")
            return None
        
        # Load clients data
        with open(clients_path, 'r') as file:
            clients_data = json.load(file)
        
        # Find the client
        if client_name in clients_data:
            logger.info(f"Loaded configuration for client: {client_name}")
            return clients_data[client_name]
        else:
            logger.error(f"Client not found in clients file: {client_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error loading client configuration: {e}", exc_info=True)
        return None


def get_active_clients(clients_path="clients.json"):
    """Get list of active clients from clients.json file.
    
    Args:
        clients_path (str, optional): Path to clients.json file. Defaults to "clients.json".
        
    Returns:
        List[str]: List of active client names
    """
    try:
        # Check if the clients file exists
        if not os.path.exists(clients_path):
            logger.error(f"Clients file not found: {clients_path}")
            return []
        
        # Load clients data
        with open(clients_path, 'r') as file:
            clients_data = json.load(file)
        
        # Filter active clients
        active_clients = []
        for client_name, client_data in clients_data.items():
            if client_data.get("active", True):
                active_clients.append(client_name)
        
        logger.info(f"Found {len(active_clients)} active clients")
        return active_clients
            
    except Exception as e:
        logger.error(f"Error getting active clients: {e}", exc_info=True)
        return []


def process_client(client_name=None, config_path="config.yaml", args=None):
    """Process a single client.
    
    Args:
        client_name (str, optional): Name of the client to process. Defaults to None.
        config_path (str, optional): Path to the configuration file. Defaults to "config.yaml".
        args (argparse.Namespace, optional): Command line arguments. Defaults to None.
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Load the default configuration
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Apply command line arguments to configuration
        if args:
            # Override platforms to scrape
            if args.platform and args.platform != "all":
                config["platforms_to_scrape"] = [args.platform]
            
            # Override max reviews per platform
            if args.max_reviews:
                config["max_reviews_per_platform"] = args.max_reviews
            
            # Override enhanced settings
            if args.enhanced:
                config["use_enhanced"] = True
            
            # Override headless mode
            if args.headless is not None:
                if "anti_bot_settings" not in config:
                    config["anti_bot_settings"] = {}
                config["anti_bot_settings"]["headless_mode"] = args.headless
            
            # Override stealth plugins
            if args.no_stealth:
                if "anti_bot_settings" not in config:
                    config["anti_bot_settings"] = {}
                config["anti_bot_settings"]["enable_stealth_plugins"] = False
            
            # Override random delays
            if args.no_random_delays:
                if "anti_bot_settings" not in config:
                    config["anti_bot_settings"] = {}
                config["anti_bot_settings"]["enable_random_delays"] = False
            
            # Override proxy rotation
            if args.enable_proxy_rotation:
                if "anti_bot_settings" not in config:
                    config["anti_bot_settings"] = {}
                config["anti_bot_settings"]["enable_proxy_rotation"] = True
        
        # Load client-specific configuration if a client name is provided
        client_config = None
        if client_name:
            client_config = load_client_config(client_name)
            if not client_config:
                logger.error(f"Failed to load configuration for client: {client_name}")
                return False
            
            # Update the output path to be client-specific
            if "csv_file_path" in client_config:
                # Ensure the directory exists
                csv_path = client_config["csv_file_path"]
                os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
        
        # Update structure analysis if requested
        if args and args.update_structure:
            update_success = update_structure_analysis(config)
            if not update_success:
                logger.warning("Proceeding with scraping despite structure analysis update failure")
        
        # Create and run the scraper
        scraper = RestaurantReviewScraper(config_path=None, client_config=client_config)
        reviews = scraper.scrape_all_platforms()
        
        # Print statistics
        scraper.print_stats()
        
        logger.info(f"Completed processing for {'client ' + client_name if client_name else 'default configuration'}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {'client ' + client_name if client_name else 'default configuration'}: {e}", exc_info=True)
        return False


def main():
    """Main function to run the restaurant review scraper."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Restaurant Review Scraper (Puppeteer Edition)")
    
    # Client selection options
    client_group = parser.add_mutually_exclusive_group()
    client_group.add_argument("--client", help="Name of the client to process")
    client_group.add_argument("--all-clients", action="store_true", help="Process all active clients")
    
    # Platform selection
    parser.add_argument("--platform", choices=["tripadvisor", "yelp", "google", "all"], default="all",
                        help="Platform to scrape (default: all)")
    
    # Scraping parameters
    parser.add_argument("--max-reviews", type=int, help="Maximum number of reviews to scrape per platform")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    
    # Structure analysis
    parser.add_argument("--update-structure", action="store_true", help="Update Google structure analysis before scraping")
    parser.add_argument("--validate-structure", action="store_true", help="Validate structure files against live websites")
    
    # Enhanced anti-bot detection options
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced anti-bot detection features")
    parser.add_argument("--headless", type=bool, nargs="?", const=True, default=None, 
                       help="Run in headless mode")
    parser.add_argument("--no-stealth", action="store_true", help="Disable stealth plugins")
    parser.add_argument("--no-random-delays", action="store_true", help="Disable random delays")
    parser.add_argument("--enable-proxy-rotation", action="store_true", help="Enable proxy rotation")
    
    # Debug options
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    print("=" * 80)
    print("Restaurant Review Scraper (Puppeteer Edition)")
    print("=" * 80)
    
    try:
        # Validate structure files if requested
        if args.validate_structure:
            validate_structure_files(args)
            return
            
        # Process all active clients
        if args.all_clients:
            print(f"\nProcessing all active clients")
            
            # Get list of active clients
            active_clients = get_active_clients()
            
            if not active_clients:
                logger.error("No active clients found")
                print("No active clients found. Please check your clients.json file.")
                return
            
            # Process each client
            successful_clients = 0
            for client_name in active_clients:
                print(f"\n--- Processing client: {client_name} ---")
                success = process_client(client_name, args.config, args)
                if success:
                    successful_clients += 1
            
            print(f"\nCompleted processing {successful_clients} out of {len(active_clients)} clients")
            
        # Process a single client
        elif args.client:
            print(f"\nProcessing client: {args.client}")
            success = process_client(args.client, args.config, args)
            if not success:
                print(f"Failed to process client: {args.client}")
        
        # Process default configuration
        else:
            print(f"\nProcessing with default configuration")
            success = process_client(None, args.config, args)
            if not success:
                print("Failed to process with default configuration")
        
        print("\nScraping completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Check scraper.log for details")


if __name__ == "__main__":
    main()
