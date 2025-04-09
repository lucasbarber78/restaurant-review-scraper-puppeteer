#!/usr/bin/env python3
"""
Structure Update Script

This standalone script updates the Google review structure analysis file.
It can be scheduled to run periodically to keep the structure analysis up-to-date.
"""

import os
import sys
import asyncio
import logging
import argparse
import yaml
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import structure analyzer
from src.utils.structure_analyzer import StructureAnalyzer, update_structure_if_needed

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


async def update_structure(force: bool = False, search_term: str = None, config_path: str = "config.yaml"):
    """
    Update the Google review structure analysis.
    
    Args:
        force (bool): Force update regardless of last update time
        search_term (str): Optional custom search term
        config_path (str): Path to configuration file
    """
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Get structure analyzer settings
        structure_config = config.get("structure_analyzer", {})
        output_dir = structure_config.get("output_dir", "Review Site Optimization")
        log_file = structure_config.get("log_file", "structure_update_log.json")
        
        # Initialize structure analyzer
        analyzer = StructureAnalyzer(
            output_dir=output_dir,
            log_file=log_file
        )
        
        # Check if update is needed or forced
        if force or analyzer.should_update_structure():
            logger.info("Starting structure analysis update...")
            
            # Use custom search term if provided, otherwise use default restaurant
            if not search_term:
                restaurant_name = config.get("restaurant_name", "Bowens Island Restaurant")
                search_term = f"{restaurant_name} Reviews"
            
            # Run the analysis
            result = await analyzer.analyze_google_review_structure(search_term=search_term)
            
            if result:
                logger.info("Structure analysis updated successfully!")
                return True
            else:
                logger.error("Failed to update structure analysis")
                return False
        else:
            logger.info("No structure update needed at this time")
            return False
            
    except Exception as e:
        logger.error(f"Error updating structure: {e}", exc_info=True)
        return False


def main():
    """Main function to run the structure update script."""
    parser = argparse.ArgumentParser(description="Update Google review structure analysis")
    parser.add_argument("--force", action="store_true", help="Force update regardless of last update time")
    parser.add_argument("--search-term", help="Custom search term for analysis")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 80)
    print("Google Review Structure Analyzer")
    print("=" * 80)
    
    try:
        # Run the update
        success = asyncio.run(update_structure(
            force=args.force, 
            search_term=args.search_term,
            config_path=args.config
        ))
        
        if success:
            print("\nStructure analysis updated successfully!")
        else:
            print("\nNo update performed")
            
    except Exception as e:
        logger.error(f"Error running update script: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Check structure_update.log for details")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
