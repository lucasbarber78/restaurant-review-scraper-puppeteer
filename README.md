# Restaurant Review Scraper - Puppeteer Edition

A comprehensive solution for scraping reviews from TripAdvisor, Yelp, and Google Reviews using Puppeteer with advanced anti-bot detection features.

## Project Objectives

This project aims to solve the following challenges for restaurant owners and managers:

1. **Comprehensive Review Collection**: Automatically gather customer reviews across multiple platforms (TripAdvisor, Yelp, and Google Reviews) to ensure no valuable feedback is missed.

2. **Chronological Analysis**: Filter reviews by specific date ranges to analyze trends, track improvement efforts, and measure the impact of operational changes over time.

3. **Automated Categorization**: Automatically classify reviews into meaningful categories (Food Quality, Wait Times, Pricing, Service, Environment/Atmosphere, etc.) to identify specific areas of strength and weakness.

4. **Sentiment Analysis**: Determine whether reviews are positive or negative to quickly gauge overall customer satisfaction and identify problem areas.

5. **Consolidated Reporting**: Export all review data to a well-organized CSV file with detailed metadata for easy analysis, sharing, and presentation to stakeholders.

6. **Trend Identification**: Identify emerging issues or consistent problems by analyzing patterns in customer feedback across time periods and platforms.

7. **Operational Decision Support**: Provide actionable insights to guide operational improvements, staff training, menu adjustments, and other business decisions.

## Features

- Scrape reviews from multiple platforms:
  - TripAdvisor
  - Yelp
  - Google Reviews
- Filter reviews by date range
- Export reviews to CSV with detailed metadata:
  - Review date
  - Reviewer name
  - Review text
  - Rating
  - Review category (automatically classified)
  - Sentiment (positive/negative)
- Automated categorization of reviews based on content
- Anti-bot detection techniques for reliable scraping
- Configurable scraping parameters
- **NEW:** Dynamic structure analysis for resilience to website changes
- **NEW:** Multi-client batch processing

## Enhanced Anti-Bot Detection System

This scraper uses advanced anti-bot detection evasion techniques:

1. **Random Delays**: Implements human-like variable timing between actions to evade bot detection:
   - Gaussian distribution for natural randomization
   - Contextual delays based on action type (clicking, scrolling, typing)
   - Occasional pauses to simulate human reading/thinking

2. **Stealth Plugins**: Integrated sophisticated browser fingerprinting and behavior simulation:
   - Realistic browser fingerprinting with consistent user-agent and headers
   - WebGL renderer and vendor spoofing to avoid canvas fingerprinting
   - JavaScript API modifications to hide automation indicators
   - Platform-specific stealth techniques for Yelp and TripAdvisor

3. **Human-Like Behavior**: Simulates natural user interactions:
   - Variable scrolling patterns with occasional upward scrolls
   - Random expansion of "Read more" links
   - Natural mouse movement patterns

## Dynamic Structure Analysis

The new structure analysis system helps the scraper adapt to changes in website layouts:

- Automatically analyzes the structure of Google review pages
- Dynamically determines the best selectors for finding review elements
- Periodically updates the structure analysis to stay current with website changes
- Falls back to default selectors if structure-based extraction fails

## Multi-Client Support

You can now scrape reviews for multiple restaurant clients in a single run:

- Define clients in the `clients.json` file
- Process all active clients with a single command
- Each client gets a separate CSV output file
- Anti-bot measures are maintained across client processing

## Requirements

- Python 3.8+
- Node.js 14+
- Puppeteer

## Installation

```bash
# Clone the repository
git clone https://github.com/lucasbarber78/restaurant-review-scraper-puppeteer.git
cd restaurant-review-scraper-puppeteer

# Install dependencies
pip install -r requirements.txt
npm install puppeteer
```

## Configuration

### Main Configuration

Edit the `config.yaml` file to set your preferences:

```yaml
# Restaurant details
restaurant_name: "Bowens Island Restaurant"
tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html"
yelp_url: "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3"
google_url: "https://www.google.com/search?q=Bowens+Island+Restaurant+Reviews"

# Scraping parameters
date_range:
  start: "2024-06-01"
  end: "2025-04-30"

# Anti-bot detection settings
anti_bot_settings:
  enable_random_delays: true
  enable_stealth_plugins: true
  headless_mode: false
  simulate_human_behavior: true
  
# Google scraper specific configuration
google_scraper:
  use_structure_analysis: true
  structure_file_path: "Review Site Optimization/google_search_review_structure_analysis.json"
  fallback_to_default_selectors: true

# Export settings
csv_file_path: "reviews.csv"
```

### Client Configuration

Edit the `clients.json` file to configure multiple restaurant clients:

```json
[
  {
    "name": "Bowens Island Restaurant",
    "google_url": "https://www.google.com/search?q=Bowens+Island+Restaurant+Reviews",
    "yelp_url": "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3",
    "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html",
    "active": true
  },
  {
    "name": "Another Restaurant",
    "google_url": "https://www.google.com/search?q=Another+Restaurant+Reviews",
    "yelp_url": "https://www.yelp.com/biz/another-restaurant",
    "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-example",
    "active": true
  }
]
```

## Usage

### Main Scraper (All Platforms)

Run the main script:

```bash
python src/main.py
```

### Enhanced Anti-Bot Mode

Run with enhanced anti-bot features:

```bash
python src/main.py --enhanced
```

### Batch Processing

Process all active clients:

```bash
python src/main.py --enhanced --all-clients
```

Process a specific client:

```bash
python src/main.py --enhanced --client "Bowens Island Restaurant"
```

### Additional Command Line Options

```bash
# Scrape only specific platforms
python src/main.py --enhanced --platform yelp google

# Set maximum number of reviews per platform
python src/main.py --enhanced --max-reviews 50

# Use a custom configuration file
python src/main.py --enhanced --config my_custom_config.yaml

# Update structure analysis before scraping
python src/main.py --enhanced --update-structure

# Run in headless mode (less visible but more detectable)
python src/main.py --enhanced --headless

# Disable stealth plugins (not recommended)
python src/main.py --enhanced --no-stealth

# Disable random delays (not recommended)
python src/main.py --enhanced --no-random-delays
```

## Structure Maintenance

To update the structure analysis manually:

```bash
python -c "from src.utils.structure_analyzer import update_structure_if_needed; import asyncio; asyncio.run(update_structure_if_needed())"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
