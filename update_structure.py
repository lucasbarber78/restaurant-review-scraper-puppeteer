#!/usr/bin/env python3
"""
Google Review Structure Analyzer - Utility Script

This script updates the structure analysis file for Google reviews.
It can be run manually or scheduled as a periodic task.
"""

import asyncio
import argparse
import logging
from src.utils.structure_analyzer import StructureAnalyzer

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


async def update_structure(search_term=None, force=False):
    """
    Update the Google review structure analysis.
    
    Args:
        search_term (str, optional): Search term to use for analysis. 
            Defaults to "Bowens Island Restaurant Reviews".
        force (bool, optional): Force update regardless of last update time.
            Defaults to False.
    """
    analyzer = StructureAnalyzer()
    
    if force or analyzer.should_update_structure():
        logger.info("Starting structure analysis update...")
        
        # Use provided search term or default
        term = search_term or "Bowens Island Restaurant Reviews"
        logger.info(f"Using search term: {term}")
        
        # Run analysis
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


def main():
    """Main function to update Google review structure analysis."""
    parser = argparse.ArgumentParser(description="Update Google Review Structure Analysis")
    parser.add_argument("--search", type=str, help="Search term to use for analysis")
    parser.add_argument("--force", action="store_true", help="Force update regardless of last update time")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Run update
    asyncio.run(update_structure(args.search, args.force))


if __name__ == "__main__":
    main()
