#!/usr/bin/env python3
"""
Structure Analyzer Module

This module analyzes and manages platform-specific structure files for selectors
and anti-bot patterns. It provides a unified interface for accessing structure data
across different review platforms.
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Import utility modules
from src.utils import (
    create_browser_session, 
    close_browser_session, 
    take_screenshot,
    apply_stealth_measures,
    async_delay_between_actions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StructureAnalyzer:
    """Analyzer for platform-specific website structures."""
    
    def __init__(self, config_path: str = "config.yaml", platform: str = "all"):
        """Initialize the structure analyzer.
        
        Args:
            config_path (str, optional): Path to the configuration file. Defaults to "config.yaml".
            platform (str, optional): Platform to analyze. Options: "tripadvisor", "yelp", 
                                     "google", "all". Defaults to "all".
        """
        import yaml
        
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        # Initialize browser session variables
        self.browser = None
        self.page = None
        
        # Set platform and paths
        if platform.lower() == "all":
            self.platforms = ["tripadvisor", "yelp", "google"]
        else:
            self.platforms = [platform.lower()]
            
        # Set up structure data paths
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self.output_paths = {
            platform: os.path.join(self.data_dir, f"{platform}_structure.json")
            for platform in self.platforms
        }
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Get analysis parameters
        self.max_samples = self.config.get("structure_analysis", {}).get("max_samples", 3)
        self.sample_urls = self._get_sample_urls()
        
        # Set up anti-bot measures for browser
        self.anti_bot_settings = self.config.get("anti_bot_settings", {})
        self.use_stealth = self.anti_bot_settings.get("enable_stealth_plugins", True)
        self.headless = self.anti_bot_settings.get("headless_mode", False)
        
        logger.info(f"Initialized Structure Analyzer for platforms: {', '.join(self.platforms)}")
    
    async def analyze_all_platforms(self) -> Dict[str, bool]:
        """Analyze all configured platforms.
        
        Returns:
            Dict[str, bool]: Dictionary with platform names as keys and success status as values.
        """
        results = {}
        
        for platform in self.platforms:
            try:
                logger.info(f"Analyzing structure for {platform}...")
                result = await self.analyze_platform(platform)
                results[platform] = result
            except Exception as e:
                logger.error(f"Error analyzing {platform}: {e}", exc_info=True)
                results[platform] = False
        
        return results
    
    async def analyze_platform(self, platform: str) -> bool:
        """Analyze the structure of a specific platform.
        
        Args:
            platform (str): Platform to analyze.
            
        Returns:
            bool: True if analysis was successful, False otherwise.
        """
        try:
            if platform == "tripadvisor":
                structure_data = await self._analyze_tripadvisor_structure()
            elif platform == "yelp":
                structure_data = await self._analyze_yelp_structure()
            elif platform == "google":
                structure_data = await self._analyze_google_structure()
            else:
                logger.error(f"Unsupported platform: {platform}")
                return False
            
            # Save structure data
            if structure_data and structure_data.get("success", False):
                output_path = self.output_paths[platform]
                with open(output_path, 'w') as file:
                    json.dump(structure_data, file, indent=2)
                logger.info(f"Saved {platform} structure data to {output_path}")
                return True
            else:
                logger.warning(f"Analysis for {platform} did not produce valid results")
                return False
                
        except Exception as e:
            logger.error(f"Error analyzing {platform} structure: {e}", exc_info=True)
            return False
            
        finally:
            # Close browser if open
            if self.browser:
                await close_browser_session(self.browser)
                self.browser = None
                self.page = None
    
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
            
            logger.info("Browser session initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing browser: {e}", exc_info=True)
            if self.browser:
                await close_browser_session(self.browser)
                self.browser = None
                self.page = None
            raise
    
    async def _analyze_tripadvisor_structure(self) -> Dict[str, Any]:
        """Analyze the structure of TripAdvisor review pages.
        
        Returns:
            Dict[str, Any]: Structure analysis results.
        """
        logger.info("Starting TripAdvisor structure analysis")
        
        structure_data = {
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "selectors": {},
            "anti_bot_patterns": {},
            "success": False
        }
        
        try:
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Apply stealth measures if enabled
            if self.use_stealth:
                self.stealth_enhancer = await apply_stealth_measures(self.page, "tripadvisor")
            
            # Get sample URLs for TripAdvisor
            platform_urls = self.sample_urls.get("tripadvisor", [])
            if not platform_urls:
                logger.warning("No sample URLs configured for TripAdvisor")
                return structure_data
            
            # Process each sample URL
            all_selectors = {}
            anti_bot_patterns = {}
            
            for i, url in enumerate(platform_urls[:self.max_samples]):
                logger.info(f"Analyzing TripAdvisor sample URL {i+1}/{min(self.max_samples, len(platform_urls))}: {url}")
                
                # Navigate to URL
                await self.page.goto(url, {"waitUntil": "networkidle0"})
                await async_delay_between_actions("navigation")
                
                # Extract selectors
                selectors = await self._extract_tripadvisor_selectors()
                for key, value in selectors.items():
                    if key not in all_selectors:
                        all_selectors[key] = []
                    all_selectors[key].append(value)
                
                # Extract anti-bot patterns
                patterns = await self._extract_tripadvisor_anti_bot_patterns()
                for key, value in patterns.items():
                    if key not in anti_bot_patterns:
                        anti_bot_patterns[key] = []
                    anti_bot_patterns[key].append(value)
            
            # Analyze collected data
            structure_data["selectors"] = self._analyze_selector_results(all_selectors)
            structure_data["anti_bot_patterns"] = self._analyze_anti_bot_results(anti_bot_patterns)
            structure_data["success"] = True
            
            return structure_data
            
        except Exception as e:
            logger.error(f"Error analyzing TripAdvisor structure: {e}", exc_info=True)
            return structure_data
    
    async def _analyze_yelp_structure(self) -> Dict[str, Any]:
        """Analyze the structure of Yelp review pages.
        
        Returns:
            Dict[str, Any]: Structure analysis results.
        """
        logger.info("Starting Yelp structure analysis")
        
        structure_data = {
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "selectors": {},
            "anti_bot_patterns": {},
            "success": False
        }
        
        try:
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Apply stealth measures if enabled
            if self.use_stealth:
                self.stealth_enhancer = await apply_stealth_measures(self.page, "yelp")
            
            # Get sample URLs for Yelp
            platform_urls = self.sample_urls.get("yelp", [])
            if not platform_urls:
                logger.warning("No sample URLs configured for Yelp")
                return structure_data
            
            # Process each sample URL
            all_selectors = {}
            anti_bot_patterns = {}
            
            for i, url in enumerate(platform_urls[:self.max_samples]):
                logger.info(f"Analyzing Yelp sample URL {i+1}/{min(self.max_samples, len(platform_urls))}: {url}")
                
                # Navigate to URL
                await self.page.goto(url, {"waitUntil": "networkidle0"})
                await async_delay_between_actions("navigation")
                
                # Extract selectors
                selectors = await self._extract_yelp_selectors()
                for key, value in selectors.items():
                    if key not in all_selectors:
                        all_selectors[key] = []
                    all_selectors[key].append(value)
                
                # Extract anti-bot patterns
                patterns = await self._extract_yelp_anti_bot_patterns()
                for key, value in patterns.items():
                    if key not in anti_bot_patterns:
                        anti_bot_patterns[key] = []
                    anti_bot_patterns[key].append(value)
            
            # Analyze collected data
            structure_data["selectors"] = self._analyze_selector_results(all_selectors)
            structure_data["anti_bot_patterns"] = self._analyze_anti_bot_results(anti_bot_patterns)
            structure_data["success"] = True
            
            return structure_data
            
        except Exception as e:
            logger.error(f"Error analyzing Yelp structure: {e}", exc_info=True)
            return structure_data
    
    async def _analyze_google_structure(self) -> Dict[str, Any]:
        """Analyze the structure of Google review pages.
        
        Returns:
            Dict[str, Any]: Structure analysis results.
        """
        logger.info("Starting Google structure analysis")
        
        structure_data = {
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "selectors": {},
            "anti_bot_patterns": {},
            "success": False
        }
        
        try:
            # Initialize browser if needed
            if not self.browser or not self.page:
                await self.init_browser()
            
            # Apply stealth measures if enabled
            if self.use_stealth:
                self.stealth_enhancer = await apply_stealth_measures(self.page, "google")
            
            # Get sample URLs for Google
            platform_urls = self.sample_urls.get("google", [])
            if not platform_urls:
                logger.warning("No sample URLs configured for Google")
                return structure_data
            
            # Process each sample URL
            all_selectors = {}
            anti_bot_patterns = {}
            
            for i, url in enumerate(platform_urls[:self.max_samples]):
                logger.info(f"Analyzing Google sample URL {i+1}/{min(self.max_samples, len(platform_urls))}: {url}")
                
                # Navigate to URL
                await self.page.goto(url, {"waitUntil": "networkidle0"})
                await async_delay_between_actions("navigation")
                
                # Extract selectors
                selectors = await self._extract_google_selectors()
                for key, value in selectors.items():
                    if key not in all_selectors:
                        all_selectors[key] = []
                    all_selectors[key].append(value)
                
                # Extract anti-bot patterns
                patterns = await self._extract_google_anti_bot_patterns()
                for key, value in patterns.items():
                    if key not in anti_bot_patterns:
                        anti_bot_patterns[key] = []
                    anti_bot_patterns[key].append(value)
            
            # Analyze collected data
            structure_data["selectors"] = self._analyze_selector_results(all_selectors)
            structure_data["anti_bot_patterns"] = self._analyze_anti_bot_results(anti_bot_patterns)
            structure_data["success"] = True
            
            return structure_data
            
        except Exception as e:
            logger.error(f"Error analyzing Google structure: {e}", exc_info=True)
            return structure_data
    
    async def _extract_tripadvisor_selectors(self) -> Dict[str, Any]:
        """Extract selectors from a TripAdvisor page.
        
        Returns:
            Dict[str, Any]: Extracted selectors.
        """
        selectors = {}
        
        try:
            # Extract review container selectors
            review_containers = await self.page.evaluate("""
                () => {
                    const selectors = [];
                    
                    // Try different selectors for review containers
                    const selectorCandidates = [
                        "div[data-reviewid]",
                        ".review-container",
                        ".review"
                    ];
                    
                    for (const selector of selectorCandidates) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            selectors.push({
                                selector: selector,
                                count: elements.length
                            });
                        }
                    }
                    
                    return selectors;
                }
            """)
            
            if review_containers:
                selectors["reviewContainer"] = sorted(review_containers, key=lambda x: x["count"], reverse=True)[0]["selector"]
            
            # Extract reviewer name selectors
            # Similar evaluation for other elements...
            
            # For demonstration, I'll just return a sample result
            # In a real implementation, you would extract all needed selectors
            
            # Analyze rating structure
            # Extract date format patterns
            # Identify review text containers
            # Find expand buttons
            # Detect next page navigation
            
            return selectors
            
        except Exception as e:
            logger.error(f"Error extracting TripAdvisor selectors: {e}", exc_info=True)
            return {}
    
    async def _extract_tripadvisor_anti_bot_patterns(self) -> Dict[str, Any]:
        """Extract anti-bot patterns from a TripAdvisor page.
        
        Returns:
            Dict[str, Any]: Extracted anti-bot patterns.
        """
        patterns = {}
        
        try:
            # Check for cookie consent dialogs
            cookie_consent = await self.page.evaluate("""
                () => {
                    const selectors = [
                        'button#onetrust-accept-btn-handler',
                        'button[id*="accept"]',
                        'button[id*="cookie"]',
                        'button[class*="cookie"]',
                        'button[class*="accept"]',
                        '.evidon-banner-acceptbutton',
                        '#gdpr-consent-tool-wrapper button[type="submit"]'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && element.offsetParent !== null) {
                            return {
                                selector: selector,
                                visible: true
                            };
                        }
                    }
                    
                    return null;
                }
            """)
            
            if cookie_consent:
                patterns["cookie_consent"] = cookie_consent["selector"]
            
            # Check for popups
            # Check for login prompts
            # Check for CAPTCHA indicators
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error extracting TripAdvisor anti-bot patterns: {e}", exc_info=True)
            return {}
    
    async def _extract_yelp_selectors(self) -> Dict[str, Any]:
        """Extract selectors from a Yelp page.
        
        Returns:
            Dict[str, Any]: Extracted selectors.
        """
        # Similar implementation as TripAdvisor but with Yelp-specific selectors
        return {}
    
    async def _extract_yelp_anti_bot_patterns(self) -> Dict[str, Any]:
        """Extract anti-bot patterns from a Yelp page.
        
        Returns:
            Dict[str, Any]: Extracted anti-bot patterns.
        """
        # Similar implementation as TripAdvisor but with Yelp-specific patterns
        return {}
    
    async def _extract_google_selectors(self) -> Dict[str, Any]:
        """Extract selectors from a Google page.
        
        Returns:
            Dict[str, Any]: Extracted selectors.
        """
        # Similar implementation for Google Maps reviews
        return {}
    
    async def _extract_google_anti_bot_patterns(self) -> Dict[str, Any]:
        """Extract anti-bot patterns from a Google page.
        
        Returns:
            Dict[str, Any]: Extracted anti-bot patterns.
        """
        # Similar implementation for Google-specific patterns
        return {}
    
    def _analyze_selector_results(self, all_selectors: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Analyze selector results from multiple samples.
        
        Args:
            all_selectors (Dict[str, List[Any]]): Collected selectors from all samples.
            
        Returns:
            Dict[str, Any]: Analyzed and merged selectors.
        """
        merged_selectors = {}
        
        for key, values in all_selectors.items():
            # Filter out None values
            values = [v for v in values if v]
            
            if not values:
                continue
                
            # For simple string selectors, use the most common one
            if all(isinstance(v, str) for v in values):
                from collections import Counter
                most_common = Counter(values).most_common(1)
                if most_common:
                    merged_selectors[key] = most_common[0][0]
            else:
                # For complex objects, just take the first one for now
                # In a real implementation, you would merge these intelligently
                merged_selectors[key] = values[0]
        
        return merged_selectors
    
    def _analyze_anti_bot_results(self, all_patterns: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Analyze anti-bot pattern results from multiple samples.
        
        Args:
            all_patterns (Dict[str, List[Any]]): Collected patterns from all samples.
            
        Returns:
            Dict[str, Any]: Analyzed and merged patterns.
        """
        # Similar to selector analysis but for anti-bot patterns
        return self._analyze_selector_results(all_patterns)
    
    def _get_sample_urls(self) -> Dict[str, List[str]]:
        """Get sample URLs from configuration.
        
        Returns:
            Dict[str, List[str]]: Dictionary of platform-specific sample URLs.
        """
        structure_analysis = self.config.get("structure_analysis", {})
        sample_urls = {}
        
        # TripAdvisor URLs
        tripadvisor_urls = structure_analysis.get("tripadvisor_sample_urls", [])
        if not tripadvisor_urls and "tripadvisor_url" in self.config:
            tripadvisor_urls = [self.config["tripadvisor_url"]]
        sample_urls["tripadvisor"] = tripadvisor_urls
        
        # Yelp URLs
        yelp_urls = structure_analysis.get("yelp_sample_urls", [])
        if not yelp_urls and "yelp_url" in self.config:
            yelp_urls = [self.config["yelp_url"]]
        sample_urls["yelp"] = yelp_urls
        
        # Google URLs
        google_urls = structure_analysis.get("google_sample_urls", [])
        if not google_urls and "google_url" in self.config:
            google_urls = [self.config["google_url"]]
        sample_urls["google"] = google_urls
        
        return sample_urls


class StructureManager:
    """Manager for accessing and using platform-specific structure files."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the structure manager.
        
        Args:
            data_dir (str, optional): Directory containing structure files. Defaults to None.
        """
        if data_dir is None:
            # Default to 'data' directory at project root
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        # Store loaded structures
        self.structures = {}
        self.load_status = {}
        
        logger.info(f"Initialized Structure Manager with data directory: {self.data_dir}")
    
    def load_structure(self, platform: str) -> bool:
        """Load structure data for a specific platform.
        
        Args:
            platform (str): Platform name.
            
        Returns:
            bool: True if structure was loaded successfully, False otherwise.
        """
        try:
            structure_path = os.path.join(self.data_dir, f"{platform}_structure.json")
            
            if not os.path.exists(structure_path):
                logger.warning(f"Structure file not found: {structure_path}")
                self.load_status[platform] = False
                return False
            
            with open(structure_path, 'r') as file:
                structure_data = json.load(file)
            
            self.structures[platform] = structure_data
            self.load_status[platform] = True
            
            logger.info(f"Loaded {platform} structure from {structure_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading {platform} structure: {e}", exc_info=True)
            self.load_status[platform] = False
            return False
    
    def load_all_structures(self) -> Dict[str, bool]:
        """Load structure data for all supported platforms.
        
        Returns:
            Dict[str, bool]: Dictionary with platform names as keys and load status as values.
        """
        platforms = ["tripadvisor", "yelp", "google"]
        results = {}
        
        for platform in platforms:
            results[platform] = self.load_structure(platform)
        
        return results
    
    def get_selector(self, platform: str, selector_name: str, default: Any = None) -> Any:
        """Get a selector for a specific platform.
        
        Args:
            platform (str): Platform name.
            selector_name (str): Selector name.
            default (Any, optional): Default value if selector is not found. Defaults to None.
            
        Returns:
            Any: Selector value or default.
        """
        if platform not in self.structures:
            if not self.load_structure(platform):
                return default
        
        return self.structures[platform].get("selectors", {}).get(selector_name, default)
    
    def get_anti_bot_pattern(self, platform: str, pattern_name: str, default: Any = None) -> Any:
        """Get an anti-bot pattern for a specific platform.
        
        Args:
            platform (str): Platform name.
            pattern_name (str): Pattern name.
            default (Any, optional): Default value if pattern is not found. Defaults to None.
            
        Returns:
            Any: Pattern value or default.
        """
        if platform not in self.structures:
            if not self.load_structure(platform):
                return default
        
        return self.structures[platform].get("anti_bot_patterns", {}).get(pattern_name, default)
    
    def get_behavior_pattern(self, platform: str, pattern_name: str, default: Any = None) -> Any:
        """Get a behavior pattern for a specific platform.
        
        Args:
            platform (str): Platform name.
            pattern_name (str): Pattern name.
            default (Any, optional): Default value if pattern is not found. Defaults to None.
            
        Returns:
            Any: Pattern value or default.
        """
        if platform not in self.structures:
            if not self.load_structure(platform):
                return default
        
        return self.structures[platform].get("behavior_patterns", {}).get(pattern_name, default)
    
    def get_fingerprinting(self, platform: str, feature_name: str, default: Any = None) -> Any:
        """Get a fingerprinting feature for a specific platform.
        
        Args:
            platform (str): Platform name.
            feature_name (str): Feature name.
            default (Any, optional): Default value if feature is not found. Defaults to None.
            
        Returns:
            Any: Feature value or default.
        """
        if platform not in self.structures:
            if not self.load_structure(platform):
                return default
        
        return self.structures[platform].get("fingerprinting", {}).get(feature_name, default)
    
    def get_structure_timestamp(self, platform: str) -> Optional[str]:
        """Get the timestamp of when a structure was last updated.
        
        Args:
            platform (str): Platform name.
            
        Returns:
            Optional[str]: Timestamp or None if not found.
        """
        if platform not in self.structures:
            if not self.load_structure(platform):
                return None
        
        return self.structures[platform].get("updated_at")
    
    def structure_exists(self, platform: str) -> bool:
        """Check if a structure file exists for a specific platform.
        
        Args:
            platform (str): Platform name.
            
        Returns:
            bool: True if structure exists, False otherwise.
        """
        structure_path = os.path.join(self.data_dir, f"{platform}_structure.json")
        return os.path.exists(structure_path)
    
    def structure_needs_update(self, platform: str, days_threshold: int = 30) -> bool:
        """Check if a structure file needs to be updated.
        
        Args:
            platform (str): Platform name.
            days_threshold (int, optional): Days threshold for update. Defaults to 30.
            
        Returns:
            bool: True if structure needs update, False otherwise.
        """
        if not self.structure_exists(platform):
            return True
        
        if platform not in self.structures:
            if not self.load_structure(platform):
                return True
        
        timestamp_str = self.structures[platform].get("updated_at")
        if not timestamp_str:
            return True
        
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str)
            
            # Calculate age in days
            age_days = (datetime.now() - timestamp).days
            
            # Check if older than threshold
            return age_days > days_threshold
            
        except Exception as e:
            logger.error(f"Error checking structure age: {e}", exc_info=True)
            return True


async def update_platform_structure(platform: str, output_path: str = None) -> bool:
    """Update structure for a specific platform.
    
    Args:
        platform (str): Platform to analyze.
        output_path (str, optional): Path to save structure file. Defaults to None.
        
    Returns:
        bool: True if update was successful, False otherwise.
    """
    try:
        analyzer = StructureAnalyzer(platform=platform)
        result = await analyzer.analyze_platform(platform)
        
        if output_path:
            logger.info(f"Structure file saved to: {output_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating {platform} structure: {e}", exc_info=True)
        return False


def main():
    """Main function for command line usage."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Update platform structure files")
    parser.add_argument("--platform", choices=["tripadvisor", "yelp", "google", "all"], 
                      default="all", help="Platform to analyze")
    parser.add_argument("--config", default="config.yaml", 
                      help="Path to configuration file")
    parser.add_argument("--output-dir", default="data", 
                      help="Directory to store structure files")
    parser.add_argument("--validate", action="store_true", 
                      help="Validate existing structure files instead of updating")
    
    args = parser.parse_args()
    
    if args.validate:
        # Validate existing structure files
        manager = StructureManager(args.output_dir)
        results = manager.load_all_structures()
        
        for platform, status in results.items():
            print(f"{platform}: {'Valid' if status else 'Invalid or missing'}")
        
        sys.exit(0 if all(results.values()) else 1)
    
    # Update structure files
    if args.platform == "all":
        platforms = ["tripadvisor", "yelp", "google"]
    else:
        platforms = [args.platform]
    
    # Set up asyncio event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop()
    
    results = {}
    for platform in platforms:
        print(f"Updating structure analysis for {platform}...")
        output_path = os.path.join(args.output_dir, f"{platform}_structure.json")
        
        # Run the update
        success = loop.run_until_complete(
            update_platform_structure(platform, output_path)
        )
        
        results[platform] = success
        print(f"{platform}: {'Success' if success else 'Failed'}")
    
    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
