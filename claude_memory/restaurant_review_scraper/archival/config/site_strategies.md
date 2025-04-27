---
title: "Site-Specific Scraping Strategies"
category: "archival/config"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "medium"
components: ["scraper", "implementation", "config"]
keywords: ["strategies", "scraping", "site-specific", "tripadvisor", "yelp", "google"]
---

# Site-Specific Scraping Strategies

## Purpose

This document provides detailed strategies for scraping each supported review platform. It covers the unique challenges, DOM structure, selector strategies, and anti-bot measures specific to each site.

## General Strategy Template

Each site-specific strategy follows this general structure:

```javascript
class PlatformStrategy {
  constructor(config) {
    this.config = config;
    this.selectors = this.getSelectors();
  }

  async initialize(page) {
    // Platform-specific initialization
  }

  getSelectors() {
    // Return platform-specific selectors
    return {
      reviewContainer: '',
      reviewerName: '',
      rating: '',
      date: '',
      reviewText: '',
      pagination: '',
      // Other selectors
    };
  }

  async navigateToReviews(page, url) {
    // Platform-specific navigation
  }

  async extractReviews(page) {
    // Platform-specific extraction
  }

  async handlePagination(page, currentPage) {
    // Platform-specific pagination
  }

  async postProcessReviews(reviews) {
    // Platform-specific post-processing
  }
}
```

## TripAdvisor Strategy

### Overview

TripAdvisor presents several unique challenges:

1. Multi-level pagination with "Show more" buttons
2. JavaScript-rendered content
3. Advanced bot detection
4. Date formats that vary by locale
5. Dynamic content loading with scroll events

### Selectors

```javascript
const tripadvisorSelectors = {
  reviewContainer: '.review-container',
  reviewerName: '.info_text div',
  userProfile: '.memberOverlayLink',
  rating: 'div.ui_column.is-9 > span.ui_bubble_rating',
  date: '.ratingDate',
  reviewText: '.reviewText',
  moreLink: '.moreLink',
  pagination: '.ui_pagination',
  nextButton: '.nav.next',
  totalReviews: '.reviews_header_count',
  sortOptions: '.sortRow select',
  locationRating: '[data-test-target=review-rating]',
  // Additional selectors
};
```

### Navigation Strategy

TripAdvisor requires careful navigation to avoid detection:

```javascript
async navigateToReviews(page, url) {
  // Initial navigation with appropriate delays
  await page.goto(url, {
    waitUntil: 'networkidle2',
    timeout: 60000
  });
  
  // Wait for reviews to load
  await page.waitForSelector(this.selectors.reviewContainer, {
    timeout: 30000
  });
  
  // Sort by date if configured
  if (this.config.sort_by_date) {
    await page.select(this.selectors.sortOptions, 'date_desc');
    
    // Wait for re-render
    await page.waitForTimeout(3000);
    await page.waitForSelector(this.selectors.reviewContainer, {
      timeout: 30000
    });
  }
  
  // Randomized pre-scraping behavior
  await this.randomPreScrapingBehavior(page);
}
```

### Extraction Strategy

TripAdvisor's review extraction requires careful DOM traversal:

```javascript
async extractReviews(page) {
  // Extract visible reviews
  const reviews = await page.evaluate((selectors) => {
    const reviews = [];
    const reviewElements = document.querySelectorAll(selectors.reviewContainer);
    
    for (const element of reviewElements) {
      try {
        // Check if reviewer name exists (filters out advertisements)
        const reviewerNameEl = element.querySelector(selectors.reviewerName);
        if (!reviewerNameEl) continue;
        
        // Extract reviewer information
        const reviewerName = reviewerNameEl.textContent.trim();
        
        // Extract rating - TripAdvisor stores rating in a class name
        const ratingEl = element.querySelector(selectors.rating);
        const ratingClass = ratingEl ? ratingEl.className : '';
        const ratingMatch = ratingClass.match(/bubble_(\d+)/);
        const rating = ratingMatch ? parseInt(ratingMatch[1]) / 10 : null;
        
        // Extract date with fallback
        const dateEl = element.querySelector(selectors.date);
        const dateText = dateEl ? dateEl.getAttribute('title') || dateEl.textContent.trim() : '';
        
        // Extract review text - handle "More" links
        let reviewTextEl = element.querySelector(selectors.reviewText);
        let reviewText = reviewTextEl ? reviewTextEl.textContent.trim() : '';
        
        // Get more detailed location ratings if available
        const locationRatingEl = element.querySelector(selectors.locationRating);
        const locationRating = locationRatingEl ? parseFloat(locationRatingEl.textContent) : null;
        
        reviews.push({
          platform: 'tripadvisor',
          reviewerName,
          rating,
          date: dateText,
          text: reviewText,
          metadata: {
            locationRating,
            // Other metadata
          }
        });
      } catch (err) {
        console.error('Error extracting review:', err);
      }
    }
    
    return reviews;
  }, this.selectors);
  
  return reviews;
}
```

### Pagination Strategy

TripAdvisor uses a complex pagination system:

```javascript
async handlePagination(page, currentPage, maxPages) {
  if (currentPage >= maxPages) {
    return false;
  }
  
  // Check if there's a next page button
  const hasNextPage = await page.evaluate((selector) => {
    const nextButton = document.querySelector(selector);
    return nextButton && !nextButton.classList.contains('disabled');
  }, this.selectors.nextButton);
  
  if (!hasNextPage) {
    return false;
  }
  
  // Click the next page button with human-like behavior
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 }),
    page.click(this.selectors.nextButton)
  ]);
  
  // Random delay between page loads
  await page.waitForTimeout(4000 + Math.random() * 3000);
  
  // Wait for reviews to load on new page
  await page.waitForSelector(this.selectors.reviewContainer, {
    timeout: 30000
  });
  
  return true;
}
```

### Anti-Detection Measures

TripAdvisor-specific anti-detection measures:

1. Expand "More" links randomly like a human
2. Random interactions with non-essential elements
3. Variation in scroll behavior specific to TripAdvisor's layout
4. Platform-specific delays between actions

## Yelp Strategy

### Overview

Yelp has several unique characteristics:

1. Infinite scrolling instead of pagination buttons
2. Heavy use of Ajax for loading content
3. Strict rate limiting and bot detection
4. Review content occasionally behind "more" buttons
5. Different URL structure for business pages

### Selectors

```javascript
const yelpSelectors = {
  reviewContainer: 'ul.undefined li .review',
  reviewerName: '.user-passport-info .fs-block a',
  rating: '.i-stars',
  date: '.review-date',
  reviewText: '.review-content p',
  moreLink: '.more-link',
  showMoreReviews: '.review-feed .load-more a',
  reviewsCount: '[data-hypernova-key="yelp_main__84c6a5232d794"]',
  sortOptions: '.review-feed .dropdown a',
  filterPanel: '.filter-panel',
  // Additional selectors
};
```

### Navigation Strategy

Yelp requires careful navigation approach:

```javascript
async navigateToReviews(page, url) {
  // Initial navigation with appropriate delays
  await page.goto(url, {
    waitUntil: 'networkidle2',
    timeout: 60000
  });
  
  // Wait for reviews to load
  await page.waitForSelector(this.selectors.reviewContainer, {
    timeout: 30000
  });
  
  // Sort by date if configured
  if (this.config.sort_by_date) {
    // Open sort dropdown
    await page.click('.review-feed .dropdown-toggle-button');
    await page.waitForTimeout(1000);
    
    // Click the date option
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2' }),
      page.click('a[href*="sort_by=date_desc"]')
    ]);
    
    // Wait for re-render
    await page.waitForSelector(this.selectors.reviewContainer, {
      timeout: 30000
    });
  }
  
  // Randomized pre-scraping behavior
  await this.randomPreScrapingBehavior(page);
}
```

### Extraction Strategy

Yelp's review extraction has unique requirements:

```javascript
async extractReviews(page) {
  // Expand "more" links randomly before extraction
  await this.expandMoreLinks(page);
  
  // Extract visible reviews
  const reviews = await page.evaluate((selectors) => {
    const reviews = [];
    const reviewElements = document.querySelectorAll(selectors.reviewContainer);
    
    for (const element of reviewElements) {
      try {
        // Extract reviewer information
        const reviewerNameEl = element.querySelector(selectors.reviewerName);
        const reviewerName = reviewerNameEl ? reviewerNameEl.textContent.trim() : 'Anonymous';
        
        // Extract rating - Yelp stores rating in a class name
        const ratingEl = element.querySelector(selectors.rating);
        const ratingClass = ratingEl ? ratingEl.className : '';
        const ratingMatch = ratingClass.match(/star-rating-(\d+)/);
        const rating = ratingMatch ? parseInt(ratingMatch[1]) / 10 : null;
        
        // Extract date
        const dateEl = element.querySelector(selectors.date);
        const dateText = dateEl ? dateEl.textContent.trim() : '';
        
        // Extract review text
        const reviewTextEl = element.querySelector(selectors.reviewText);
        const reviewText = reviewTextEl ? reviewTextEl.textContent.trim() : '';
        
        // Get check-in count if available
        const checkInsEl = element.querySelector('.review-footer-userStats');
        const checkIns = checkInsEl ? this.extractNumber(checkInsEl.textContent) : null;
        
        reviews.push({
          platform: 'yelp',
          reviewerName,
          rating,
          date: dateText,
          text: reviewText,
          metadata: {
            checkIns,
            // Other metadata
          }
        });
      } catch (err) {
        console.error('Error extracting review:', err);
      }
    }
    
    return reviews;
  }, this.selectors);
  
  return reviews;
}
```

### Pagination Strategy

Yelp uses infinite scrolling instead of traditional pagination:

```javascript
async handlePagination(page, currentPage, maxPages) {
  if (currentPage >= maxPages) {
    return false;
  }
  
  // Check if there's a "Show More Reviews" button
  const hasMoreReviews = await page.evaluate((selector) => {
    const moreButton = document.querySelector(selector);
    return !!moreButton && moreButton.offsetParent !== null;
  }, this.selectors.showMoreReviews);
  
  if (!hasMoreReviews) {
    // If no button, try scrolling to trigger loading
    const didScroll = await this.scrollForMoreReviews(page);
    return didScroll;
  }
  
  // Click the "Show More Reviews" button with human-like behavior
  await page.click(this.selectors.showMoreReviews);
  
  // Random delay after clicking
  await page.waitForTimeout(3000 + Math.random() * 2000);
  
  // Wait for new reviews to load
  await page.waitForFunction((oldCount, selector) => {
    return document.querySelectorAll(selector).length > oldCount;
  }, { timeout: 10000 }, await page.evaluate(selector => document.querySelectorAll(selector).length, this.selectors.reviewContainer), this.selectors.reviewContainer);
  
  return true;
}

async scrollForMoreReviews(page) {
  const previousHeight = await page.evaluate('document.body.scrollHeight');
  
  // Scroll to bottom with human-like behavior
  await page.evaluate(() => {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: 'smooth'
    });
  });
  
  // Wait for potential content loading
  await page.waitForTimeout(2500 + Math.random() * 1500);
  
  // Check if page height increased (indicating new content)
  const newHeight = await page.evaluate('document.body.scrollHeight');
  return newHeight > previousHeight;
}
```

## Google Reviews Strategy

### Overview

Google Reviews has distinct characteristics:

1. Dynamic loading with scroll events
2. Reviews contained in shadow DOM elements
3. More stringent bot detection
4. Nested iframes in some implementations
5. Frequent changes to DOM structure

### Selectors

Google's selectors often change, so we use a structure analysis system:

```javascript
// Default selectors - will be overridden by structure analysis
const googleSelectors = {
  reviewContainer: '.jftiEf',
  reviewerName: '.d4r55',
  userProfile: '.WNxzHc a',
  rating: '.kvMYJc',
  date: '.rsqaWe',
  reviewText: '.wiI7pd',
  moreReviewsButton: '.DU9Pgb a',
  sortDropdown: '.fxNQSd button',
  sortOptions: '.Tlm5Zb',
  sortNewest: 'data-sort-id="newestFirst"',
  expansion: '.review-more-link',
  // Additional selectors that may change
};

// The actual selectors used will be loaded from structure_analysis.json at runtime
```

### Dynamic Selector Analysis

Google Reviews requires dynamic selector analysis:

```javascript
async loadDynamicSelectors() {
  try {
    // Load structure analysis from file
    const analysisData = await fs.readFile(this.config.structure_analysis_path, 'utf8');
    const analysis = JSON.parse(analysisData);
    
    // Override default selectors with analyzed ones
    if (analysis.google && analysis.google.selectors) {
      this.selectors = {
        ...this.selectors,
        ...analysis.google.selectors
      };
      console.log('Loaded dynamic selectors for Google Reviews');
    }
  } catch (error) {
    console.warn('Could not load dynamic selectors, using defaults:', error.message);
  }
}
```

### Navigation Strategy

Google Reviews requires special handling:

```javascript
async navigateToReviews(page, url) {
  // Initial navigation with appropriate delays
  await page.goto(url, {
    waitUntil: 'networkidle2',
    timeout: 60000
  });
  
  // Handle potential cookie consent dialogs
  await this.handleCookieConsent(page);
  
  // Wait for reviews section to load
  await page.waitForSelector(this.selectors.reviewContainer, {
    timeout: 30000
  });
  
  // Sort by date if configured (Google's sort is more complex)
  if (this.config.sort_by_date) {
    // Click sort dropdown
    await page.click(this.selectors.sortDropdown);
    await page.waitForTimeout(1000);
    
    // Click the "newest" option
    const sortOptionSelector = `[${this.selectors.sortNewest}]`;
    await page.waitForSelector(sortOptionSelector);
    await page.click(sortOptionSelector);
    
    // Wait for re-render
    await page.waitForTimeout(2000);
    await page.waitForSelector(this.selectors.reviewContainer, {
      timeout: 30000
    });
  }
  
  // Special Google-specific behaviors to appear human
  await this.randomGoogleUserBehavior(page);
}
```

### Extraction Strategy

Google Reviews requires careful handling of dynamic content:

```javascript
async extractReviews(page) {
  // Ensure all review content is expanded
  await this.expandAllReviews(page);
  
  // Extract visible reviews
  const reviews = await page.evaluate((selectors) => {
    const reviews = [];
    const reviewElements = document.querySelectorAll(selectors.reviewContainer);
    
    for (const element of reviewElements) {
      try {
        // Extract reviewer information
        const reviewerNameEl = element.querySelector(selectors.reviewerName);
        const reviewerName = reviewerNameEl ? reviewerNameEl.textContent.trim() : 'Anonymous';
        
        // Extract rating - Google uses aria-label for rating
        const ratingEl = element.querySelector(selectors.rating);
        const ratingText = ratingEl ? ratingEl.getAttribute('aria-label') : '';
        const ratingMatch = ratingText.match(/(\d+)/);
        const rating = ratingMatch ? parseInt(ratingMatch[1]) : null;
        
        // Extract date
        const dateEl = element.querySelector(selectors.date);
        const dateText = dateEl ? dateEl.textContent.trim() : '';
        
        // Extract review text
        const reviewTextEl = element.querySelector(selectors.reviewText);
        const reviewText = reviewTextEl ? reviewTextEl.textContent.trim() : '';
        
        // Get local guide status if available
        const isLocalGuide = !!element.querySelector('.RfnDt');
        
        reviews.push({
          platform: 'google',
          reviewerName,
          rating,
          date: dateText,
          text: reviewText,
          metadata: {
            isLocalGuide,
            // Other metadata
          }
        });
      } catch (err) {
        console.error('Error extracting review:', err);
      }
    }
    
    return reviews;
  }, this.selectors);
  
  return reviews;
}

async expandAllReviews(page) {
  // Find and click all "More" buttons to expand review text
  const expandCount = await page.evaluate((selector) => {
    const expandButtons = Array.from(document.querySelectorAll(selector));
    expandButtons.forEach(button => button.click());
    return expandButtons.length;
  }, this.selectors.expansion);
  
  if (expandCount > 0) {
    // Wait for expansions to complete
    await page.waitForTimeout(1000);
  }
}
```

### Scroll-Based Loading

Google uses scroll-based loading:

```javascript
async loadMoreReviews(page, maxScrolls = 10) {
  let lastReviewCount = 0;
  let currentScrolls = 0;
  
  while (currentScrolls < maxScrolls) {
    // Get current review count
    const currentReviewCount = await page.evaluate(
      selector => document.querySelectorAll(selector).length,
      this.selectors.reviewContainer
    );
    
    // If no new reviews after last scroll, stop
    if (currentReviewCount === lastReviewCount) {
      break;
    }
    
    lastReviewCount = currentReviewCount;
    
    // Scroll to load more reviews
    await page.evaluate(() => {
      // Find the reviews container
      const container = document.querySelector('.review-dialog-list');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    });
    
    // Wait for potential content loading with human-like delay
    await page.waitForTimeout(2000 + Math.random() * 1000);
    
    currentScrolls++;
  }
  
  return lastReviewCount > 0;
}
```

## Specialized Template Creation

To add a new site strategy, follow this template:

```javascript
// Example implementation for a new review site
class NewSiteStrategy extends PlatformStrategy {
  constructor(config) {
    super(config);
    this.name = 'newsite';
  }
  
  getSelectors() {
    return {
      reviewContainer: '',
      reviewerName: '',
      rating: '',
      date: '',
      reviewText: '',
      pagination: '',
      // Site-specific selectors
    };
  }
  
  async navigateToReviews(page, url) {
    // Site-specific navigation
  }
  
  async extractReviews(page) {
    // Site-specific extraction
  }
  
  async handlePagination(page, currentPage) {
    // Site-specific pagination
  }
  
  async postProcessReviews(reviews) {
    // Site-specific post-processing
  }
}
```

## Related Components

- [Scraper Design](../implementation/scraper_design.md)
- [Data Processing](../implementation/data_processing.md)
- [Anti-Bot Measures](../implementation/anti_bot_measures.md)
