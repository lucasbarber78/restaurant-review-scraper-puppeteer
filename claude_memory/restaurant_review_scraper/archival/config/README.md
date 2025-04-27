---
title: "Configuration Documentation"
category: "archival/config"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "medium"
components: ["configuration", "documentation"]
keywords: ["config", "settings", "parameters", "documentation"]
---

# Configuration Documentation

This directory contains documentation related to the configuration aspects of the restaurant review scraper system. It focuses on how to configure, customize, and adapt the scraper for different use cases, sites, and environments.

## Purpose

The configuration documentation serves to:

1. Explain the available configuration options and their effects
2. Provide templates for site-specific scraping strategies
3. Document installation and setup procedures
4. Outline environment requirements and dependencies
5. Define schemas for configuration files

## Directory Structure

```
config/
├── README.md                     # This file
├── site_strategy_template.md     # Template for creating site-specific strategies
├── tripadvisor_strategy.md       # TripAdvisor-specific implementation details
├── yelp_strategy.md              # Yelp-specific implementation details
├── google_strategy.md            # Google Reviews-specific implementation details
├── installation.md               # Installation and environment setup guide
├── configuration_schema.md       # Documentation of config.yaml format
├── clients_schema.md             # Documentation of clients.json format
└── environment_variables.md      # Documentation of environment variables
```

## How to Use This Section

### For Developers

If you are a developer working on the scraper:

1. Read the [installation guide](installation.md) to set up your development environment
2. Study the site-specific strategies to understand the implementation details
3. Use the templates when adding support for new review sites
4. Refer to the schema documentation when modifying configuration formats

### For System Administrators

If you are setting up or maintaining the scraper:

1. Follow the [installation guide](installation.md) to install the application
2. Use the [configuration schema](configuration_schema.md) to understand available options
3. Set up environment variables as documented in [environment_variables.md](environment_variables.md)

### For End Users

If you are using the scraper as an end user:

1. Read the [configuration schema](configuration_schema.md) to understand how to customize the scraper
2. Learn how to set up multiple clients in [clients_schema.md](clients_schema.md)
3. Check the site-specific documentation if you encounter issues with particular review sites

## Key Topics

### Site-Specific Strategies

Each review site has its own structure, selectors, and challenges. The site-specific strategy documents explain:

- DOM structure and key selectors
- Navigation patterns
- Date format parsing
- Anti-bot detection techniques
- Known issues and workarounds
- Version history of the strategy

### Configuration Files

The scraper uses several configuration files:

1. **config.yaml**: Main configuration file with global settings
2. **clients.json**: Configuration for multiple restaurant clients
3. **structure_analysis.json**: Automatically updated site structure information

The schema documentation explains all available options, their defaults, and effects.

### Environment Setup

The installation and environment documentation covers:

- System requirements
- Dependency installation
- Browser setup
- Proxy configuration
- Development vs. production environments

## Additions and Updates

When adding a new site-specific strategy or updating configuration options:

1. Use the provided templates to ensure consistent documentation
2. Update any affected schema documentation
3. Note version changes in version history sections
4. Update this README if adding new document types

## Related Sections

- [Implementation Documentation](../implementation/README.md): Technical implementation details
- [API Documentation](../api/README.md): API interfaces and usage
