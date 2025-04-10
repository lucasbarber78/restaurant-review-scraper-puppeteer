#!/usr/bin/env python3
"""
Update Structure Script

This script serves as a command-line interface for updating platform-specific structure files.
It provides additional functionality beyond the core structure_analyzer.py module.
"""

import os
import sys
import argparse
import asyncio
import logging
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import structure analyzer
from src.utils.structure_analyzer import StructureAnalyzer, StructureManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("structure_update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_config_with_structure_settings(config_path: str = "config.yaml") -> bool:
    """Update the configuration file with structure analysis settings.
    
    Args:
        config_path (str, optional): Path to configuration file. Defaults to "config.yaml".
        
    Returns:
        bool: True if configuration was updated successfully, False otherwise.
    """
    try:
        # Load existing configuration
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Add structure analysis section if it doesn't exist
        if "structure_analysis" not in config:
            config["structure_analysis"] = {}
        
        # Set default structure analysis settings if not present
        structure_analysis = config["structure_analysis"]
        
        if "enabled" not in structure_analysis:
            structure_analysis["enabled"] = True
        
        if "max_samples" not in structure_analysis:
            structure_analysis["max_samples"] = 3
        
        if "check_interval_days" not in structure_analysis:
            structure_analysis["check_interval_days"] = 30
        
        if "auto_update" not in structure_analysis:
            structure_analysis["auto_update"] = True
        
        # Add platform-specific sample URLs if not present
        if "tripadvisor_sample_urls" not in structure_analysis:
            if "tripadvisor_url" in config:
                structure_analysis["tripadvisor_sample_urls"] = [config["tripadvisor_url"]]
            else:
                structure_analysis["tripadvisor_sample_urls"] = [
                    "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html",
                    "https://www.tripadvisor.com/Restaurant_Review-g60763-d802686-Reviews-Le_Bernardin-New_York_City_New_York.html"
                ]
        
        if "yelp_sample_urls" not in structure_analysis:
            if "yelp_url" in config:
                structure_analysis["yelp_sample_urls"] = [config["yelp_url"]]
            else:
                structure_analysis["yelp_sample_urls"] = [
                    "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3",
                    "https://www.yelp.com/biz/shake-shack-new-york-13"
                ]
        
        if "google_sample_urls" not in structure_analysis:
            if "google_url" in config:
                structure_analysis["google_sample_urls"] = [config["google_url"]]
            else:
                structure_analysis["google_sample_urls"] = [
                    "https://www.google.com/maps/place/Bowens+Island+Restaurant/@32.6942361,-79.9653904,17z",
                    "https://www.google.com/maps/place/Le+Bernardin/@40.7615168,-73.9829381,17z"
                ]
        
        # Save updated configuration
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Configuration updated successfully: {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}", exc_info=True)
        return False

def validate_structures() -> Dict[str, bool]:
    """Validate existing structure files.
    
    Returns:
        Dict[str, bool]: Dictionary with platform names as keys and validation status as values.
    """
    try:
        # Create structure manager
        manager = StructureManager()
        
        # Load all structures
        results = manager.load_all_structures()
        
        # Check structure timestamps
        for platform in results.keys():
            if results[platform]:
                # Check if structure is up to date
                timestamp = manager.get_structure_timestamp(platform)
                if timestamp:
                    try:
                        timestamp_dt = datetime.fromisoformat(timestamp)
                        age_days = (datetime.now() - timestamp_dt).days
                        
                        logger.info(f"{platform} structure is {age_days} days old")
                        
                        # Mark as invalid if too old
                        if age_days > 30:
                            logger.warning(f"{platform} structure is more than 30 days old")
                            results[platform] = False
                    except Exception as e:
                        logger.warning(f"Error parsing {platform} timestamp: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error validating structures: {e}", exc_info=True)
        return {"tripadvisor": False, "yelp": False, "google": False}

async def update_all_structures() -> Dict[str, bool]:
    """Update all platform structures.
    
    Returns:
        Dict[str, bool]: Dictionary with platform names as keys and update status as values.
    """
    try:
        # Create structure analyzer
        analyzer = StructureAnalyzer()
        
        # Analyze all platforms
        results = await analyzer.analyze_all_platforms()
        
        return results
        
    except Exception as e:
        logger.error(f"Error updating structures: {e}", exc_info=True)
        return {"tripadvisor": False, "yelp": False, "google": False}

def print_structure_info(platform: str) -> None:
    """Print information about a platform structure file.
    
    Args:
        platform (str): Platform name.
    """
    try:
        # Create structure manager
        manager = StructureManager()
        
        # Check if structure exists
        if not manager.structure_exists(platform):
            print(f"No structure file found for {platform}")
            return
        
        # Load structure
        if not manager.load_structure(platform):
            print(f"Error loading structure for {platform}")
            return
        
        # Get timestamp
        timestamp = manager.get_structure_timestamp(platform)
        if timestamp:
            try:
                timestamp_dt = datetime.fromisoformat(timestamp)
                age_days = (datetime.now() - timestamp_dt).days
                print(f"Structure timestamp: {timestamp} ({age_days} days old)")
            except Exception:
                print(f"Structure timestamp: {timestamp}")
        
        # Get selectors
        selectors = manager.structures[platform].get("selectors", {})
        print(f"Selectors: {len(selectors)}")
        for name in selectors.keys():
            print(f"  - {name}")
        
        # Get anti-bot patterns
        patterns = manager.structures[platform].get("anti_bot_patterns", {})
        print(f"Anti-bot patterns: {len(patterns)}")
        for name in patterns.keys():
            print(f"  - {name}")
        
        # Get behavior patterns
        behaviors = manager.structures[platform].get("behavior_patterns", {})
        print(f"Behavior patterns: {len(behaviors)}")
        for name in behaviors.keys():
            print(f"  - {name}")
        
    except Exception as e:
        print(f"Error printing structure info: {e}")

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Update and manage platform structure files")
    parser.add_argument("--platform", choices=["tripadvisor", "yelp", "google", "all"], 
                      default="all", help="Platform to analyze")
    parser.add_argument("--config", default="config.yaml", 
                      help="Path to configuration file")
    parser.add_argument("--validate", action="store_true", 
                      help="Validate existing structure files instead of updating")
    parser.add_argument("--update-config", action="store_true", 
                      help="Update configuration file with structure analysis settings")
    parser.add_argument("--info", action="store_true",
                      help="Print information about structure files")
    parser.add_argument("--force", action="store_true",
                      help="Force update even if structures are up to date")
    
    args = parser.parse_args()
    
    # Update configuration file if requested
    if args.update_config:
        success = update_config_with_structure_settings(args.config)
        print(f"Configuration update: {'Success' if success else 'Failed'}")
        if not success:
            sys.exit(1)
    
    # Validate existing structures if requested
    if args.validate:
        results = validate_structures()
        
        all_valid = True
        for platform, status in results.items():
            print(f"{platform}: {'Valid' if status else 'Invalid or missing'}")
            if not status:
                all_valid = False
        
        sys.exit(0 if all_valid else 1)
    
    # Print structure information if requested
    if args.info:
        if args.platform == "all":
            platforms = ["tripadvisor", "yelp", "google"]
        else:
            platforms = [args.platform]
        
        for platform in platforms:
            print(f"\n=== {platform.upper()} STRUCTURE ===")
            print_structure_info(platform)
        
        sys.exit(0)
    
    # Update structures
    if args.platform == "all":
        platforms = ["tripadvisor", "yelp", "google"]
    else:
        platforms = [args.platform]
    
    # Check if update is needed
    if not args.force:
        manager = StructureManager()
        update_needed = False
        
        for platform in platforms:
            if manager.structure_needs_update(platform):
                update_needed = True
                print(f"{platform} structure needs update")
            else:
                print(f"{platform} structure is up to date")
        
        if not update_needed:
            print("All structures are up to date. Use --force to update anyway.")
            sys.exit(0)
    
    # Set up asyncio event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop()
    
    # Update structures
    analyzer = StructureAnalyzer(config_path=args.config, platform=args.platform)
    
    if args.platform == "all":
        results = loop.run_until_complete(analyzer.analyze_all_platforms())
    else:
        result = loop.run_until_complete(analyzer.analyze_platform(args.platform))
        results = {args.platform: result}
    
    # Print results
    for platform, success in results.items():
        print(f"{platform}: {'Success' if success else 'Failed'}")
    
    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
