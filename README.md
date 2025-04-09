# Restaurant Review Scraper - Puppeteer Edition

A comprehensive solution for scraping reviews from TripAdvisor, Yelp, and Google Reviews using Puppeteer with advanced anti-bot detection features.

## Project Objectives

This project aims to solve the following challenges for restaurant owners and managers:

1. **Comprehensive Review Collection**: Automatically gather customer reviews across multiple platforms (TripAdvisor, Yelp, and Google Reviews) to ensure no valuable feedback is missed.

2. **Chronological Analysis**: Filter reviews by specific date ranges to analyze trends, track improvement efforts, and measure the impact of operational changes over time.

3. **Automated Categorization**: Automatically classify reviews into meaningful categories (Food Quality, Wait Times, Pricing, Service, Environment/Atmosphere, Product Availability, etc.) to identify specific areas of strength and weakness.

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

Edit the `config.yaml` file to set your preferences:

```yaml
# Restaurant details
restaurant_name: "Bowens Island Restaurant"
tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html"
yelp_url: "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3"
google_url: "https://www.google.com/maps/place/Bowens+Island+Restaurant/@32.6942361,-79.9653904,17z/data=!4m7!3m6!1s0x88fc6fb9c4167fea:0xf7766add942e243c!8m2!3d32.6942361!4d-79.9628155!9m1!1b1"

# Scraping parameters
date_range:
  start: "2024-06-01"
  end: "2025-04-30"

# Anti-bot detection settings
anti_bot_settings:
  # Random delay settings
  enable_random_delays: true
  delay_base_values:
    click: 1.0
    scroll: 1.5
    navigation: 3.0
    typing: 0.2
  
  # Stealth enhancement settings
  enable_stealth_plugins: true
  headless_mode: false
  simulate_human_behavior: true
  
# Export settings
csv_file_path: "reviews.csv"
```

## Usage

### Main Scraper (All Platforms)

Run the main script:

```bash
python src/main.py
```

### Individual Platform Scrapers

Use individual scrapers for specific platforms:

```bash
# TripAdvisor scraper
python src/tripadvisor_scraper.py

# Yelp scraper
python src/yelp_scraper.py

# Google Reviews scraper
python src/google_scraper.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
