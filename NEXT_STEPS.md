# Next Steps for Restaurant Review Scraper

## What We've Accomplished

We've successfully enhanced the Restaurant Review Scraper with multi-client support and a more robust architecture:

1. **Multi-Client Architecture**
   - Implemented `clients.json` for managing multiple restaurant clients
   - Updated the main scraper to support batch processing
   - Created a flexible command-line interface for controlling scraping behavior

2. **Structure Analysis System**
   - Developed a sophisticated system for analyzing Google Reviews DOM structure
   - Created a mechanism to adapt to changes in site structure
   - Implemented automatic selector detection for resilient scraping

3. **Enhanced Configuration**
   - Improved the configuration system with structure analysis settings
   - Added platform-specific scraping options
   - Updated directory structure for better organization

4. **Documentation and Setup**
   - Updated README.md with comprehensive documentation
   - Created a helper script for setting up the directory structure
   - Updated .gitignore to properly exclude generated files

## Future Plans for TripAdvisor and Yelp Structure Analysis

We've decided to extend the structure analysis approach to TripAdvisor and Yelp by:

1. **Creating Platform-Specific Structure Files**
   - `tripadvisor_structure.json` - To store TripAdvisor-specific selectors and patterns
   - `yelp_structure.json` - To store Yelp-specific selectors and patterns

2. **Incorporating Platform-Specific Anti-Bot Techniques**
   - Each platform file will include specialized detection avoidance measures
   - Custom behavior patterns tailored to each site's expectations
   - Adaptive timing and interaction models

3. **Unified Structure Analysis Framework**
   - Extending the existing structure analysis system to support all platforms
   - Implementing platform-specific analysis logic
   - Creating a consistent interface for all platforms

## Implementation Steps for Future Development

To implement these enhancements, here are the detailed steps:

### 1. Extend the Structure Analyzer Class

The existing `StructureAnalyzer` class in `update_structure.py` should be extended to support multiple platforms:

```python
class StructureAnalyzer:
    def __init__(self, config_path: str = "config.yaml", platform: str = "google"):
        # Load configuration
        # ...
        
        # Store platform-specific settings
        self.platform = platform
        self.output_path = f"data/{platform}_structure.json"
        
    async def analyze_structure(self):
        """Main entry point for structure analysis."""
        if self.platform == "google":
            return await self.analyze_google_structure()
        elif self.platform == "tripadvisor":
            return await self.analyze_tripadvisor_structure()
        elif self.platform == "yelp":
            return await self.analyze_yelp_structure()
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
```

### 2. Create TripAdvisor Structure Analysis

Implement a TripAdvisor-specific structure analysis method:

```python
async def analyze_tripadvisor_structure(self) -> Dict[str, Any]:
    """Analyze the structure of TripAdvisor review pages.
    
    Returns:
        Dict[str, Any]: Structure analysis results.
    """
    logger.info("Starting TripAdvisor structure analysis")
    
    structure_data = {
        "updated_at": datetime.now().isoformat(),
        "selectors": {},
        "anti_bot_patterns": {},
        "success": False
    }
    
    try:
        # Initialize browser if needed
        if not self.browser or not self.page:
            await self.init_browser()
        
        # Get sample URLs for TripAdvisor
        sample_urls = self._get_sample_urls_for_platform("tripadvisor")
        
        # Analyze samples
        all_selectors = []
        anti_bot_patterns = []
        
        for i, url in enumerate(sample_urls[:self.max_samples]):
            # Navigate to URL and extract selectors
            # ...
            
            # Detect anti-bot patterns specific to TripAdvisor
            # - Cookie consent dialogs
            # - Login prompts
            # - CAPTCHA patterns
            # - Rate limiting indicators
            
        # Analyze collected data
        structure_data["selectors"] = self._analyze_selectors(all_selectors)
        structure_data["anti_bot_patterns"] = self._analyze_anti_bot_patterns(anti_bot_patterns)
        structure_data["success"] = True
        
        return structure_data
        
    except Exception as e:
        logger.error(f"Error analyzing TripAdvisor structure: {e}", exc_info=True)
        return structure_data
    
    finally:
        # Close browser
        # ...
```

### 3. Create Yelp Structure Analysis

Implement a Yelp-specific structure analysis method:

```python
async def analyze_yelp_structure(self) -> Dict[str, Any]:
    """Analyze the structure of Yelp review pages.
    
    Returns:
        Dict[str, Any]: Structure analysis results.
    """
    logger.info("Starting Yelp structure analysis")
    
    structure_data = {
        "updated_at": datetime.now().isoformat(),
        "selectors": {},
        "anti_bot_patterns": {},
        "success": False
    }
    
    try:
        # Initialize browser if needed
        if not self.browser or not self.page:
            await self.init_browser()
        
        # Get sample URLs for Yelp
        sample_urls = self._get_sample_urls_for_platform("yelp")
        
        # Analyze samples
        all_selectors = []
        anti_bot_patterns = []
        
        for i, url in enumerate(sample_urls[:self.max_samples]):
            # Navigate to URL and extract selectors
            # ...
            
            # Detect anti-bot patterns specific to Yelp
            # - Advanced fingerprinting techniques
            # - Login requirements
            # - Anti-bot JavaScript
            # - Rate limiting approaches
            
        # Analyze collected data
        structure_data["selectors"] = self._analyze_selectors(all_selectors)
        structure_data["anti_bot_patterns"] = self._analyze_anti_bot_patterns(anti_bot_patterns)
        structure_data["success"] = True
        
        return structure_data
        
    except Exception as e:
        logger.error(f"Error analyzing Yelp structure: {e}", exc_info=True)
        return structure_data
    
    finally:
        # Close browser
        # ...
```

### 4. Update Scrapers to Use Structure Files

Modify the platform-specific scrapers to use the structure analysis data:

```python
class YelpReviewScraper:
    def __init__(self, config_path: str = "config.yaml"):
        # ...
        
        # Load structure analysis data
        self.structure_data = self._load_structure_data()
        
    def _load_structure_data(self) -> Dict[str, Any]:
        """Load Yelp structure analysis data."""
        structure_path = "data/yelp_structure.json"
        if os.path.exists(structure_path):
            try:
                with open(structure_path, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.warning(f"Error loading structure data: {e}")
        
        # Return default structure if file not found or error
        return {"selectors": {}, "anti_bot_patterns": {}}
        
    async def scrape_reviews(self) -> List[Dict[str, Any]]:
        # ...
        
        # Use dynamic selectors from structure analysis
        reviewer_selector = self.structure_data["selectors"].get(
            "reviewerNameSelector", 
            ".user-passport-info .css-166la90"  # Fallback
        )
        
        # Apply anti-bot patterns if available
        if "cookie_consent" in self.structure_data["anti_bot_patterns"]:
            await self._handle_cookie_consent_dynamic()
        
        # ...
```

### 5. Enhance the Command-Line Interface

Update the command-line interface to support structure analysis for all platforms:

```python
# In src/update_structure.py
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update structure analysis")
    parser.add_argument("--platform", choices=["google", "tripadvisor", "yelp", "all"], 
                        default="all", help="Platform to analyze")
    parser.add_argument("--output-dir", default="data", 
                        help="Directory to store structure files")
    # ...
    
    args = parser.parse_args()
    
    if args.platform == "all":
        platforms = ["google", "tripadvisor", "yelp"]
    else:
        platforms = [args.platform]
    
    for platform in platforms:
        print(f"Updating structure analysis for {platform}...")
        output_path = f"{args.output_dir}/{platform}_structure.json"
        success = update_platform_structure(platform, output_path)
        # ...
```

### 6. Testing and Validation Framework

Create a validation system to ensure the structure analysis is accurate:

```python
# New file: src/validate_structure.py
async def validate_structure(platform: str) -> bool:
    """Validate structure analysis results for a platform.
    
    Args:
        platform (str): Platform name.
        
    Returns:
        bool: Validation success status.
    """
    # Load structure data
    structure_path = f"data/{platform}_structure.json"
    if not os.path.exists(structure_path):
        logger.error(f"Structure file not found: {structure_path}")
        return False
    
    with open(structure_path, 'r') as file:
        structure_data = json.load(file)
    
    # Initialize browser
    browser, page = create_browser_session()
    
    try:
        # Get test URL from config
        url = get_test_url_for_platform(platform)
        
        # Navigate to test URL
        await page.goto(url, {"waitUntil": "networkidle0"})
        
        # Test selectors
        successful_selectors = 0
        total_selectors = len(structure_data["selectors"])
        
        for name, selector in structure_data["selectors"].items():
            try:
                element = await page.querySelector(selector)
                if element:
                    successful_selectors += 1
            except Exception:
                pass
        
        success_rate = successful_selectors / total_selectors if total_selectors > 0 else 0
        
        logger.info(f"Structure validation for {platform}: {success_rate:.2%} success rate")
        
        return success_rate >= 0.7  # Require at least 70% of selectors to work
        
    except Exception as e:
        logger.error(f"Error validating structure: {e}", exc_info=True)
        return False
        
    finally:
        # Close browser
        await close_browser_session(browser)
```

## Next Actions

1. **Structure Analysis Components**
   - [ ] Implement TripAdvisor structure analysis
   - [ ] Implement Yelp structure analysis
   - [ ] Create platform-specific anti-bot pattern detection

2. **Integration**
   - [ ] Update scrapers to use dynamic structure files
   - [ ] Enhance command-line interface
   - [ ] Create validation framework

3. **Documentation**
   - [ ] Document structure file formats
   - [ ] Update README with new features
   - [ ] Create examples for customizing anti-bot behaviors

4. **Testing**
   - [ ] Test across multiple client sites
   - [ ] Validate structure analysis accuracy
   - [ ] Compare success rates between static and dynamic selectors

By following these steps, we'll create a more resilient and adaptable scraping system that can withstand changes in platform structures and enhance our anti-bot detection avoidance capabilities.
