#!/usr/bin/env python3
"""
Structure Analysis Updater

This script updates the Google review structure analysis file, which helps the scraper
adapt to changes in Google's DOM structure. It's designed to be run periodically
as a scheduled task to ensure the scraper stays up-to-date.
"""

import asyncio
import logging
import argparse
import os
from datetime import datetime

from src.utils.structure_analyzer import StructureAnalyzer, update_structure_if_needed

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f"structure_update_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def update_structure(force=False, search_term=None):
    """
    Update the Google review structure analysis.
    
    Args:
        force (bool): Force update even if it's not needed
        search_term (str): Custom search term to use for analysis
    """
    logger.info("Starting structure analysis update")
    
    try:
        # Create analyzer
        analyzer = StructureAnalyzer()
        
        # Check if we should update
        if force or analyzer.should_update_structure():
            logger.info("Structure update needed or forced")
            
            # Use default or custom search term
            term = search_term or "Bowens Island Restaurant Reviews"
            logger.info(f"Using search term: {term}")
            
            # Perform analysis
            result = await analyzer.analyze_google_review_structure(term)
            
            if result:
                logger.info("Structure analysis updated successfully")
                return True
            else:
                logger.error("Structure analysis update failed")
                return False
        else:
            logger.info("No structure update needed at this time")
            return False
            
    except Exception as e:
        logger.error(f"Error updating structure: {e}", exc_info=True)
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Update Google review structure analysis")
    
    parser.add_argument("--force", action="store_true", 
                        help="Force update even if it's not needed")
    parser.add_argument("--search-term", type=str, 
                        help="Custom search term to use for analysis")
    
    return parser.parse_args()


def main():
    """Main function to run the structure updater."""
    print("=" * 80)
    print("Google Review Structure Analyzer")
    print("=" * 80)
    
    # Parse command line arguments
    args = parse_args()
    
    # Run the update
    result = asyncio.run(update_structure(force=args.force, search_term=args.search_term))
    
    if result:
        print("\nStructure analysis updated successfully")
    else:
        print("\nNo update performed or update failed")
        print("Check the log file for details")


if __name__ == "__main__":
    main()
