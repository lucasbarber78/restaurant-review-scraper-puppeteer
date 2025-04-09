# Dynamic Structure Analysis for Google Review Scraping

This document explains the dynamic structure analysis feature that has been implemented to improve the reliability of Google review scraping.

## Overview

Google frequently updates their website's DOM structure, which can break hardcoded CSS selectors used in web scrapers. The dynamic structure analysis feature addresses this issue by:

1. Analyzing and mapping the structure of Google review pages
2. Storing this structure in a JSON file
3. Using this structure to dynamically determine the best selectors at runtime
4. Implementing fallback mechanisms to handle changes

## How It Works

### Structure Analysis

The `structure_analyzer.py` module performs an automated analysis of Google review pages:

- It navigates to a Google search results page for a restaurant
- It analyzes various HTML elements that contain review information
- It identifies selectors for reviewer names, ratings, dates, and review text
- It saves this analysis to a JSON file (`google_search_review_structure_analysis.json`)

This analysis is automatically updated periodically to stay current with Google's changes.

### Dynamic Selector Usage

The `google_scraper.py` module uses the structure analysis to extract reviews:

- It loads the structure analysis file at initialization
- It extracts selectors for different review components
- It uses these selectors to find and extract reviews
- If structure-based selectors fail, it falls back to hardcoded selectors

## Key Benefits

1. **Resilience to Changes**: The scraper adapts to changes in Google's DOM structure
2. **Automatic Updates**: The structure is periodically updated without manual intervention
3. **Fallback Mechanisms**: Even if the structure-based selectors fail, the scraper can still function
4. **Cross-Client Compatibility**: One structure analysis can be used for all restaurant clients

## Configuration

Configuration for the structure analysis feature is in the `config.yaml` file:

```yaml
# Google scraper configuration
google_scraper:
  use_structure_analysis: true
  structure_file_path: "Review Site Optimization/google_search_review_structure_analysis.json"
  fallback_to_default_selectors: true
  update_structure_interval_days:
    min: 7   # Minimum days between updates
    max: 14  # Maximum days between updates

# Structure analyzer settings
structure_analyzer:
  output_dir: "Review Site Optimization"
  screenshots_dir: "Review Site Optimization/screenshots"
  log_file: "structure_update_log.json"
```

## Command Line Options

The following command line options are available for managing structure analysis:

```
--update-structure      Update the Google review structure analysis
--no-structure          Disable structure-based scraping
```

Example:

```bash
# Update the structure analysis
python src/main.py --update-structure

# Run scraper without using structure analysis
python src/main.py --no-structure

# Run scraper with structure analysis (default)
python src/main.py
```

## Multiple Client Support

The structure analysis feature works seamlessly with the new multi-client functionality:

- One structure analysis file is used for all restaurant clients
- The structure is restaurant-agnostic, as Google's review structure is consistent across different restaurants
- When running in batch mode, the structure is loaded once and used for all clients

Example:

```bash
# Process all active clients
python src/main.py --batch

# Process a specific client
python src/main.py --client "Bowens Island Restaurant"
```

## Maintenance

The structure analysis is automatically updated based on the configured interval. However, you can force an update:

```bash
python src/main.py --update-structure
```

The update process respects all anti-bot detection measures:

- It uses random delays between actions
- It applies stealth plugins to avoid detection
- It simulates human behavior during the analysis

## Troubleshooting

If you encounter issues with the review extraction:

1. Check if the structure analysis file exists
2. Try forcing a structure update with `--update-structure`
3. If the issue persists, try running with `--no-structure` to fall back to hardcoded selectors
4. Check the logs for detailed error messages

## Files

The following files are part of the structure analysis feature:

- `src/utils/structure_analyzer.py`: Analyzes and updates the structure
- `src/utils/structure_parser.py`: Parses the structure file to extract selectors
- `Review Site Optimization/google_search_review_structure_analysis.json`: The structure analysis file
- `structure_update_log.json`: Logs when the structure was last updated

## Anti-Bot Detection Integration

The structure analysis process is integrated with all anti-bot detection measures:

- It uses random delays between actions
- It applies stealth plugins to avoid detection
- It simulates human behavior during the analysis
- It randomizes the update schedule to avoid creating a detectable pattern

This integration ensures that the structure analysis process itself doesn't increase the risk of detection.
