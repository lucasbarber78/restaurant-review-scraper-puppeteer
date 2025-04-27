# Restaurant Review Scraper with Puppeteer

An enhanced web scraping solution specifically designed for restaurant review sites with anti-bot detection mechanisms using Puppeteer.

## Claude-Iterated Memory System

This project uses a Claude-iterated memory system for documentation and project management. This approach:

1. **Organizes knowledge in three tiers:**
   - Core Memory: Essential project information
   - Recall Memory: Conversation history and decisions
   - Archival Memory: Detailed technical documentation

2. **Provides structured access to project information**
   - Use the memory index to navigate between related documents
   - Ask Claude about specific components or features

3. **Evolves documentation naturally through conversations**
   - Documentation updates happen as part of development
   - Maintains consistency across documentation tiers

To learn more about how to use this system, see [CLAUDE_MEMORY_GUIDE.md](CLAUDE_MEMORY_GUIDE.md).

## What's New - Multi-Client Support

The latest update adds support for managing multiple restaurant clients:

- **Multiple Client Configuration**: Easily manage scraping for multiple restaurants via the `clients.json` file
- **Batch Processing**: Process all active clients with a single command
- **Enhanced Command-Line Interface**: Control which platforms to scrape, which client to process, and more
- **Structure Analysis**: Automatically update Google Reviews selectors to adapt to site changes
- **Improved Data Organization**: Store client data in separate directories for better organization

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
- Multi-client management and batch processing

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

### Single Restaurant Configuration

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

### Multiple Client Configuration

The `clients.json` file allows you to manage multiple restaurants:

```json
{
  "client_id": {
    "active": true,
    "restaurant_name": "Restaurant Name",
    "tripadvisor_url": "https://www.tripadvisor.com/...",
    "yelp_url": "https://www.yelp.com/...",
    "google_url": "https://www.google.com/maps/...",
    "date_range": {
      "start": "2024-06-01",
      "end": "2025-04-30"
    },
    "csv_file_path": "data/clients/client_id/reviews.csv"
  }
}
```

Each client can have its own configuration settings that override the defaults from `config.yaml`.

## Documentation Structure

The project documentation is organized using the Claude-iterated memory system:

### Core Memory (`claude_memory/restaurant_review_scraper/core/`)

Contains essential project information:
- `project_overview.md`: High-level description of the project
- `architecture.md`: System architecture and component relationships
- `requirements.md`: Functional and non-functional requirements
- `current_status.md`: Current project status and roadmap
- `ai_workflow.md`: Guidelines for Claude-assisted development

### Recall Memory (`claude_memory/restaurant_review_scraper/recall/`)

Contains session summaries and decision history:
- Session summaries organized by date
- Records of key decisions and rationales
- Tracking of project evolution over time

### Archival Memory (`claude_memory/restaurant_review_scraper/archival/`)

Contains detailed technical documentation:
- Implementation details for specific components
- Configuration guidance
- API documentation
- Detailed technical specifications

## Usage

### Working with Multiple Clients

#### Process All Active Clients

```bash
python src/main.py --all-clients
```

This will process all clients marked as `"active": true` in the `clients.json` file.

#### Process a Specific Client

```bash
python src/main.py --client bowens_island
```

This will process only the specified client, using its configuration from `clients.json`.

#### Process Default Configuration

```bash
python src/main.py
```

This will use the configuration from `config.yaml` without any client-specific settings.

### Platform Selection

You can choose which platforms to scrape:

```bash
# Scrape only TripAdvisor reviews
python src/main.py --platform tripadvisor

# Scrape only Yelp reviews
python src/main.py --platform yelp

# Scrape only Google reviews
python src/main.py --platform google

# Scrape all platforms (default)
python src/main.py --platform all
```

### Structure Analysis

Update the Google structure analysis to adapt to changes in the site's DOM:

```bash
# Update structure analysis
python src/update_structure.py

# Update structure analysis before scraping
python src/main.py --update-structure
```

### Enhanced Anti-Bot Detection

Toggle anti-bot detection features:

```bash
# Use enhanced anti-bot detection
python src/main.py --enhanced

# Run in headless mode (less visible but more detectable)
python src/main.py --enhanced --headless true

# Disable stealth plugins (not recommended)
python src/main.py --enhanced --no-stealth

# Disable random delays (not recommended)
python src/main.py --enhanced --no-random-delays

# Enable proxy rotation if configured in config.yaml
python src/main.py --enhanced --enable-proxy-rotation
```

## Troubleshooting

### Error: "Failed to create browser session"

- Check your Puppeteer installation
- Verify your internet connection
- Try running without headless mode: `--headless false`

### Error: "Bot detection encountered"

- Try running with enhanced anti-bot features: `--enhanced`
- Disable headless mode: set `--headless false`
- Try reducing the number of reviews you're scraping at once

### Error: "No reviews found"

- Verify the URLs in your config file
- Check if the restaurant has any reviews on that platform
- Try running with just one platform to isolate the issue
- Run with `--update-structure` to adapt to DOM changes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
