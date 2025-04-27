---
title: "Configuration Guide"
category: "archival/config"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
components: ["config", "settings"]
keywords: ["configuration", "settings", "yaml", "json", "options"]
---

# Configuration Guide

## Purpose

This document provides comprehensive instructions for configuring the restaurant review scraper, including both single-restaurant and multi-client configurations, advanced settings, and platform-specific options.

## Configuration Files Overview

The scraper uses two main configuration files:

1. **config.yaml**: Core configuration and default settings
2. **clients.json**: Multi-client management settings

## Core Configuration (config.yaml)

The `config.yaml` file contains the primary configuration settings:

```yaml
# Basic restaurant settings (for single restaurant mode)
restaurant_name: "Bowens Island Restaurant"
tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html"
yelp_url: "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3"
google_url: "https://www.google.com/maps/place/Bowens+Island+Restaurant/@32.6942361,-79.9653904,17z/data=!4m7!3m6!1s0x88fc6fb9c4167fea:0xf7766add942e243c!8m2!3d32.6942361!4d-79.9628155!9m1!1b1"

# Date range to filter reviews
date_range:
  start: "2024-06-01"  # Format: YYYY-MM-DD
  end: "2025-04-30"    # Format: YYYY-MM-DD

# Anti-bot detection settings
anti_bot_settings:
  # Random delay settings
  enable_random_delays: true
  delay_base_values:
    click: 1.0        # Base seconds for click actions
    scroll: 1.5       # Base seconds for scroll actions
    navigation: 3.0   # Base seconds for page navigation
    typing: 0.2       # Base seconds per character when typing
  
  # Delay variance (percentage)
  delay_variance: 50  # +/- percentage variation of base delay
  
  # Stealth enhancement settings
  enable_stealth_plugins: true
  headless_mode: false
  simulate_human_behavior: true
  
  # Browser fingerprinting settings
  browser_profile:
    use_consistent_profile: true
    rotate_profiles: false
    profiles_path: "data/browser_profiles.json"

# Proxy settings
proxy_settings:
  enable_proxy_rotation: false
  proxy_type: "http"  # http, socks4, or socks5
  proxies:
    - host: "proxy1.example.com"
      port: 8080
      username: "user1"
      password: "pass1"
    - host: "proxy2.example.com"
      port: 8080
      username: "user2"
      password: "pass2"
  rotation_strategy: "round-robin"  # round-robin, random, error-based
  max_consecutive_requests: 10      # Max requests before rotating
  error_threshold: 3                # Number of errors before marking proxy as unhealthy

# Scraping settings
scraping_settings:
  max_reviews_per_platform: 100     # Maximum number of reviews to scrape per platform
  platforms:                        # Platforms to scrape (comment out to disable)
    - tripadvisor
    - yelp
    - google
  sort_by_date: true                # Try to sort reviews by date (newest first)
  min_rating: 1                     # Minimum star rating to include (1-5)
  max_rating: 5                     # Maximum star rating to include (1-5)
  include_empty_reviews: false      # Whether to include reviews with no text

# Error handling
error_handling:
  max_retries: 3                    # Maximum number of retries for failed operations
  retry_delay: 5                    # Seconds to wait between retries
  skip_on_error: true               # Continue to next platform if one fails
  screenshot_on_error: true         # Save screenshot when error occurs
  error_screenshots_path: "screenshots/errors"

# Structure analysis settings
structure_analysis_path: "data/structure_analysis.json"
update_structure_on_start: false    # Whether to update structure analysis when starting scraper
structure_analysis_settings:
  min_samples: 5                    # Minimum number of samples to collect for structure analysis
  max_samples: 10                   # Maximum number of samples to collect for structure analysis
  save_samples: true                # Whether to save HTML samples during structure analysis
  samples_directory: "data/samples" # Directory to save HTML samples

# Data processing settings
data_processing:
  enable_sentiment_analysis: true   # Analyze sentiment of reviews
  enable_categorization: true       # Categorize reviews by topic
  category_keywords:                # Keywords for each category
    food_quality:
      - "food"
      - "taste"
      - "flavor"
      # ... more keywords
    service:
      - "service"
      - "staff"
      - "waiter"
      # ... more keywords
    # ... more categories

# Export settings
csv_file_path: "reviews.csv"        # Path for output CSV file
json_export: false                  # Also export as JSON
json_file_path: "reviews.json"      # Path for optional JSON export

# Debugging
debug: false                        # Enable debug logging
verbose: false                      # Enable verbose output
log_file: "logs/scraper.log"        # Path for log file
```

## Multi-Client Configuration (clients.json)

The `clients.json` file defines settings for multiple restaurant clients:

```json
{
  "bowens_island": {
    "active": true,
    "restaurant_name": "Bowens Island Restaurant",
    "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html",
    "yelp_url": "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3",
    "google_url": "https://www.google.com/maps/place/Bowens+Island+Restaurant/@32.6942361,-79.9653904,17z/data=!4m7!3m6!1s0x88fc6fb9c4167fea:0xf7766add942e243c!8m2!3d32.6942361!4d-79.9628155!9m1!1b1",
    "date_range": {
      "start": "2024-06-01",
      "end": "2025-04-30"
    },
    "csv_file_path": "data/clients/bowens_island/reviews.csv",
    "max_reviews_per_platform": 50,
    "platforms": ["tripadvisor", "yelp", "google"]
  },
  "husk_charleston": {
    "active": true,
    "restaurant_name": "Husk Restaurant",
    "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-g54171-d2216598-Reviews-Husk_Restaurant-Charleston_South_Carolina.html",
    "yelp_url": "https://www.yelp.com/biz/husk-charleston",
    "google_url": "https://www.google.com/maps/place/Husk/@32.7779517,-79.9339102,17z/data=!4m7!3m6!1s0x88fe7a4277e1bb2d:0x74c05b772e31b800!8m2!3d32.7779517!4d-79.9317215!9m1!1b1",
    "date_range": {
      "start": "2024-06-01",
      "end": "2025-04-30"
    },
    "csv_file_path": "data/clients/husk_charleston/reviews.csv",
    "max_reviews_per_platform": 75,
    "platforms": ["tripadvisor", "yelp", "google"]
  }
}
```

## Configuration Inheritance

When using multi-client mode:

1. Settings in `config.yaml` act as global defaults
2. Client-specific settings in `clients.json` override the defaults
3. Command-line arguments override both config files

The resolution order is:
```
Command Line → Client-Specific Config → Global Config → Hardcoded Defaults
```

## Platform-Specific Configuration

### TripAdvisor-Specific Settings

```yaml
platform_settings:
  tripadvisor:
    sort_option: "date_desc"        # date_desc, rating_desc, rating_asc
    expand_review_text: true        # Auto-expand truncated reviews
    extract_user_contributions: true # Extract reviewer contribution count
    language: "en"                  # Review language to filter for
    max_scroll_attempts: 10         # Max attempts to scroll for more reviews
```

### Yelp-Specific Settings

```yaml
platform_settings:
  yelp:
    sort_option: "date_desc"        # date_desc, rating_desc, rating_asc, elites_desc
    extract_check_ins: true         # Extract check-in count if available
    extract_photos: true            # Extract photo count if available
    extract_elite_status: true      # Note if reviewer has Elite status
    max_pagination_clicks: 20       # Maximum pagination clicks
```

### Google-Specific Settings

```yaml
platform_settings:
  google:
    sort_option: "newest"           # newest, highest, lowest
    min_rating_filter: 0            # UI filter for minimum rating (0-5)
    max_rating_filter: 5            # UI filter for maximum rating (0-5)
    expand_review_text: true        # Auto-expand truncated reviews
    extract_local_guide: true       # Note if reviewer is a Local Guide
    max_scroll_attempts: 15         # Max attempts to scroll for more reviews
```

## Advanced Configuration Options

### Browser Fingerprinting Configuration

Create custom browser profiles in `data/browser_profiles.json`:

```json
[
  {
    "name": "Windows Chrome 94",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "platform": "Win32",
    "screenResolution": {"width": 1920, "height": 1080},
    "viewport": {"width": 1280, "height": 800},
    "language": "en-US",
    "colorDepth": 24,
    "deviceMemory": 8,
    "hardwareConcurrency": 8,
    "timezone": "America/New_York",
    "plugins": [
      "Chrome PDF Plugin",
      "Chrome PDF Viewer",
      "Native Client"
    ]
  },
  {
    "name": "MacOS Safari",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "platform": "MacIntel",
    "screenResolution": {"width": 2560, "height": 1600},
    "viewport": {"width": 1280, "height": 800},
    "language": "en-US",
    "colorDepth": 24,
    "deviceMemory": 8,
    "hardwareConcurrency": 8,
    "timezone": "America/Los_Angeles",
    "plugins": [
      "QuickTime Plugin",
      "Safari PDF Viewer"
    ]
  }
]
```

### Proxy Provider API Integration

Configure third-party proxy providers:

```yaml
proxy_settings:
  # ... basic proxy settings
  
  proxy_provider:
    enabled: false
    provider: "brightdata"  # brightdata, smartproxy, luminati, etc.
    api_key: "your_api_key_here"
    api_url: "https://api.provider.com/v1"
    proxy_type: "datacenter"  # datacenter, residential, mobile
    country: "US"
    session_duration: 600     # Session duration in seconds
    max_concurrent_sessions: 5
```

### Structure Analysis Configuration

Fine-tune the structure analysis system that adapts to site changes:

```yaml
structure_analysis_settings:
  # ... basic structure analysis settings
  
  advanced:
    selector_confidence_threshold: 0.8  # Minimum confidence to use a selector
    use_fuzzy_matching: true            # Use fuzzy matching for selectors
    fuzzy_threshold: 0.7                # Threshold for fuzzy matches (0.0-1.0)
    backup_selector_count: 3            # Number of backup selectors to maintain
    max_selector_length: 150            # Maximum length for generated selectors
    prefer_stable_attributes:           # Attributes to prefer when generating selectors
      - "data-test-id"
      - "id"
      - "class"
    ignore_attributes:                  # Attributes to ignore when generating selectors
      - "style"
      - "tabindex"
```

## Environment Variables

The scraper also supports configuration via environment variables:

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `SCRAPER_DEBUG` | Enable debug mode | `false` |
| `SCRAPER_CONFIG_PATH` | Path to config.yaml | `./config.yaml` |
| `SCRAPER_CLIENTS_PATH` | Path to clients.json | `./clients.json` |
| `SCRAPER_HEADLESS` | Enable headless browser mode | `false` |
| `SCRAPER_MAX_REVIEWS` | Maximum reviews per platform | `100` |
| `SCRAPER_PROXY_ENABLED` | Enable proxy rotation | `false` |
| `SCRAPER_PLATFORMS` | Comma-separated list of platforms | `tripadvisor,yelp,google` |

Environment variables override settings in both config files and take priority over everything except command-line arguments.

## Command-Line Arguments

The scraper supports various command-line arguments for quick configuration:

```bash
# Basic usage
python src/main.py [options]

# Options
--config PATH             Custom config file path
--client CLIENT_ID        Process specific client
--all-clients             Process all active clients
--platform PLATFORM       Platform to scrape (tripadvisor, yelp, google, or all)
--max-reviews NUMBER      Maximum reviews per platform
--dates START END         Date range (YYYY-MM-DD format)
--enhanced                Use enhanced anti-bot detection
--headless BOOL           Run in headless mode
--no-stealth              Disable stealth plugins
--no-random-delays        Disable random delays
--enable-proxy-rotation   Enable proxy rotation
--update-structure        Update structure analysis before scraping
--debug                   Show debug information
--help                    Show help message
```

## Configuration Best Practices

1. **Start with defaults**: Use the default configuration as a starting point
2. **Client-specific customization**: Override only what's necessary in clients.json
3. **Security**: Store sensitive information (API keys, proxy credentials) in environment variables
4. **Version control**: Track configuration changes in git, but exclude credentials
5. **Testing**: Test configuration changes on a single client before applying to all
6. **Structure analysis**: When site scraping breaks, run update_structure.py to adapt

## Common Configuration Scenarios

### High-Volume Scraping

```yaml
scraping_settings:
  max_reviews_per_platform: 500
  platforms:
    - tripadvisor
    - yelp
    - google

anti_bot_settings:
  enable_random_delays: true
  delay_base_values:
    click: 2.0        # Longer delays
    scroll: 3.0
    navigation: 5.0
    typing: 0.5
  
proxy_settings:
  enable_proxy_rotation: true
  rotation_strategy: "error-based"
  max_consecutive_requests: 5
```

### Stealth Focused

```yaml
anti_bot_settings:
  enable_random_delays: true
  delay_variance: 80  # Higher variance for more human-like behavior
  enable_stealth_plugins: true
  headless_mode: false
  simulate_human_behavior: true
  browser_profile:
    use_consistent_profile: true
    rotate_profiles: false

proxy_settings:
  enable_proxy_rotation: true
  rotation_strategy: "random"
  max_consecutive_requests: 3
```

### Minimal Configuration

```yaml
restaurant_name: "Example Restaurant"
tripadvisor_url: "https://www.tripadvisor.com/..."
date_range:
  start: "2024-06-01"
  end: "2025-04-30"

anti_bot_settings:
  enable_random_delays: true
  enable_stealth_plugins: true
  headless_mode: false

scraping_settings:
  max_reviews_per_platform: 50
  platforms:
    - tripadvisor

csv_file_path: "reviews.csv"
```

## Related Components

- [Scraper Design](../implementation/scraper_design.md)
- [Site-Specific Strategies](site_strategies.md)
- [Data Processing](../implementation/data_processing.md)
- [Browser Fingerprinting](../implementation/browser_fingerprinting.md)
- [Command-Line Interface](command_line_interface.md)
