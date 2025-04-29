---
title: "Installation and Setup Guide"
category: "implementation"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
tags: ["setup", "installation", "configuration", "environment"]
related_documents: 
  - "claude_memory/restaurant_review_scraper/archival/config/configuration_guide.md"
  - "claude_memory/restaurant_review_scraper/core/requirements.md"
---

# Installation and Setup Guide

This document provides comprehensive instructions for installing and setting up the Restaurant Review Scraper with Puppeteer. It covers environment setup, dependency installation, and initial configuration.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8+
- **Node.js**: 14+
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 1GB free space for application and dependencies

## Prerequisites

Before setting up the scraper, ensure you have the following prerequisites installed:

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation with `python --version`

2. **Node.js 14+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify installation with `node --version`

3. **Git**
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Verify installation with `git --version`

## Installation Steps

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/lucasbarber78/restaurant-review-scraper-puppeteer.git
cd restaurant-review-scraper-puppeteer
```

### Install Python Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Install Node.js Dependencies

```bash
# Install Puppeteer and related packages
npm install puppeteer
```

## Project Configuration

### Basic Configuration

1. Edit the `config.yaml` file to set your preferences:

```yaml
# Restaurant details
restaurant_name: "Your Restaurant Name"
tripadvisor_url: "https://www.tripadvisor.com/Restaurant_Review-..."
yelp_url: "https://www.yelp.com/biz/..."
google_url: "https://www.google.com/maps/place/..."

# Scraping parameters
date_range:
  start: "2025-01-01"
  end: "2025-04-27"

# Anti-bot detection settings
anti_bot_settings:
  enable_random_delays: true
  delay_base_values:
    click: 1.0
    scroll: 1.5
    navigation: 3.0
    typing: 0.2
  
  enable_stealth_plugins: true
  headless_mode: false
  simulate_human_behavior: true
  
# Export settings
csv_file_path: "reviews.csv"
```

### Multi-Client Configuration

For managing multiple restaurant clients, configure the `clients.json` file:

```json
{
  "client_id": {
    "active": true,
    "restaurant_name": "Restaurant Name",
    "tripadvisor_url": "https://www.tripadvisor.com/...",
    "yelp_url": "https://www.yelp.com/...",
    "google_url": "https://www.google.com/maps/...",
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-04-27"
    },
    "csv_file_path": "data/clients/client_id/reviews.csv"
  }
}
```

## Directory Structure Setup

The scraper requires a specific directory structure. You can set it up manually or use the included setup script:

### Manual Setup

Create the following directory structure:

```
restaurant-review-scraper-puppeteer/
├── data/
│   ├── structure_analysis.json
│   ├── samples/
│   └── clients/
│       ├── client1/
│       │   └── reviews.csv
│       ├── client2/
│       │   └── reviews.csv
│       └── client3/
│           └── reviews.csv
└── screenshots/
```

### Using the Setup Script

Alternatively, run the setup script to automatically create the directory structure:

```bash
python setup_project_structure.py
```

This will guide you through a series of questions to configure your project structure.

#### Setup Script Options

- **Interactive Mode**: `python setup_project_structure.py`
- **Using a Configuration File**: `python setup_project_structure.py --config my_project_config.yaml`
- **Non-Interactive Mode**: `python setup_project_structure.py --config my_project_config.yaml --non-interactive`

Additional options:
- `--output-dir`: Specify the directory where files will be generated (default: current directory)
- `--save-config`: Specify where to save the configuration (default: project_config.yaml)

## Verifying the Installation

To verify your installation is working properly:

1. Run the structure analysis tool:

```bash
python src/update_structure.py
```

2. Test a basic scrape with a single platform:

```bash
python src/main.py --platform tripadvisor --max-reviews 5
```

If both commands complete without errors, your installation is successful.

## Troubleshooting

### Common Issues

1. **Failed to create browser session**
   - Check your Puppeteer installation
   - Verify your internet connection
   - Try running without headless mode: `--headless false`

2. **Bot detection encountered**
   - Try running with enhanced anti-bot features: `--enhanced`
   - Disable headless mode: remove `--headless` flag or set `--headless false`
   - Try reducing the number of reviews you're scraping at once

3. **No reviews found**
   - Verify the URLs in your config file
   - Check if the restaurant has any reviews on that platform
   - Try running with just one platform to isolate the issue
   - Run with `--update-structure` to adapt to DOM changes

4. **Date parsing failed**
   - The date format wasn't recognized
   - The review will still be included but might not be filtered correctly by date
   - Consider updating the date parsing patterns in `date_utils.py`

## Next Steps

After successful installation and setup:

1. Review the [Configuration Guide](../config/configuration_guide.md) for customizing your setup
2. Explore the [Site Strategies](../config/site_strategies.md) for platform-specific configurations
3. Check the [Testing and Validation](testing_validation.md) document for ensuring proper operation

For more information on requirements and dependencies, see the [Requirements](../../core/requirements.md) document.
