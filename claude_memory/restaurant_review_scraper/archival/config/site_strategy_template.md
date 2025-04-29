---
title: "Site Strategy Template"
category: "archival/config"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "medium"
components: ["scraper", "site-strategy"]
keywords: ["template", "site-specific", "scraping", "configuration"]
---

# Site Strategy Template

This document provides a template for creating site-specific scraping strategies. When adding a new review site to the scraper, copy this template and replace the placeholders with site-specific information.

## Template Usage

1. Copy this template to create a new document
2. Name it according to the site (e.g., `tripadvisor_strategy.md`, `yelp_strategy.md`)
3. Fill in all sections with site-specific information
4. Update the memory index to include the new strategy document

## Site Strategy: [SITE_NAME]

### Basic Information

- **Site Name**: [Full name of the review site]
- **Base URL**: [Base URL for the site, e.g., https://www.tripadvisor.com]
- **Review URL Pattern**: [Pattern for restaurant review URLs, e.g., /Restaurant_Review-g{location_id}-d{restaurant_id}-Reviews-...]
- **Supported Since**: [Version the site was first supported]
- **Last Updated**: [Date when the strategy was last updated]

### Site Structure

Detail the site's DOM structure for review pages:

```
// Example DOM structure for reviews
<div class="review-container">
  <div class="review-header">
    <div class="reviewer-info">...</div>
    <div class="rating">...</div>
    <div class="review-date">...</div>
  </div>
  <div class="review-content">...</div>
</div>
```

### Selectors

Key CSS selectors for extracting review data:

| Element | Selector | Notes |
|---------|----------|-------|
| Review Container | `.review-container` | Main container for each review |
| Reviewer Name | `.review-container .info_text div` | User who wrote the review |
| Rating | `.review-container .ui_bubble_rating` | Star rating (attribute variation) |
| Date | `.review-container .ratingDate` | Date when review was posted |
| Review Text | `.review-container .reviewText` | Main review content |
| Pagination | `.pageNumbers a` | Navigation between review pages |

### Extraction Logic

```javascript
async function extract[SITE_NAME]Reviews(page) {
  return page.evaluate(() => {
    const reviews = [];
    const reviewElements = document.querySelectorAll('[REVIEW_CONTAINER_SELECTOR]');
    
    for (const element of reviewElements) {
      // Extract reviewer name
      const reviewerNameEl = element.querySelector('[REVIEWER_NAME_SELECTOR]');
      const reviewerName = reviewerNameEl ? reviewerNameEl.textContent.trim() : 'Anonymous';
      
      // Extract rating
      const ratingEl = element.querySelector('[RATING_SELECTOR]');
      const rating = ratingEl ? parseRating(ratingEl) : null;
      
      // Extract date
      const dateEl = element.querySelector('[DATE_SELECTOR]');
      const date = dateEl ? dateEl.textContent.trim() : '';
      
      // Extract review text
      const textEl = element.querySelector('[TEXT_SELECTOR]');
      const text = textEl ? textEl.textContent.trim() : '';
      
      // Additional metadata extraction as needed
      
      reviews.push({
        reviewerName,
        rating,
        date,
        text,
        // Other fields
      });
    }
    
    return reviews;
  });
}

function parseRating(ratingElement) {
  // Site-specific rating extraction logic
  // e.g., converting classes, attributes, or text to a numerical rating
}
```

### Navigation Strategy

How to navigate through review pages:

```javascript
async function navigateReviews(page, config) {
  // Navigate to the initial reviews page
  await page.goto(config.url, { waitUntil: 'networkidle2' });
  
  // Handle cookie consent/popups if needed
  await handleInitialPopups(page);
  
  // Sort by date if required
  await sortByDate(page);
  
  // Implementation of page navigation
  async function goToNextPage() {
    const hasNextPage = await page.evaluate(() => {
      const nextButton = document.querySelector('[NEXT_PAGE_SELECTOR]');
      return nextButton && !nextButton.disabled;
    });
    
    if (!hasNextPage) return false;
    
    await page.click('[NEXT_PAGE_SELECTOR]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    return true;
  }
  
  // Implementation of strategies to load more reviews
  async function loadMoreReviews() {
    // Site-specific logic to load more reviews (e.g., infinite scroll, "load more" button)
  }
  
  return {
    goToNextPage,
    loadMoreReviews
  };
}
```

### Anti-Detection Techniques

Site-specific anti-bot detection countermeasures:

- **Required Headers**: [Any specific headers needed]
- **Cookie Management**: [How to handle cookies]
- **Timing Patterns**: [Specific timing patterns to avoid detection]
- **Action Sequence**: [Specific sequence of actions to mimic human behavior]
- **Known Triggers**: [Actions known to trigger bot detection]

```javascript
async function applyAntiDetectionMeasures(page, config) {
  // Set specific headers if needed
  await page.setExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': config.userAgent,
    // Other headers
  });
  
  // Apply specific cookies if needed
  await page.setCookie(...[
    // Site-specific cookies
  ]);
  
  // Set up page interception for request modification if needed
  await page.setRequestInterception(true);
  page.on('request', request => {
    // Modify request if needed
    // e.g., change headers, block certain requests
    request.continue();
  });
  
  // Add site-specific browser fingerprinting evasion
  await page.evaluateOnNewDocument(() => {
    // Override site-specific fingerprinting methods
  });
}
```

### Error Handling

Common errors and how to handle them:

```javascript
async function handleSiteSpecificErrors(page, error) {
  // Check for site-specific error patterns
  if (error.message.includes('[SPECIFIC_ERROR_PATTERN]')) {
    console.log('Handling site-specific error pattern');
    
    // Recovery strategy
    await page.reload({ waitUntil: 'networkidle2' });
    await page.waitForTimeout(5000); // Wait before continuing
    
    return true; // Error handled
  }
  
  // Other error handling strategies
  
  return false; // Error not handled, will be propagated
}
```

### Date Parsing

How to parse dates from this site:

```javascript
function parseSiteSpecificDate(dateString) {
  // Example patterns:
  // "Reviewed June 5, 2024"
  // "5 days ago"
  // "March 2024"
  
  // Site-specific date parsing logic
  if (dateString.includes('ago')) {
    // Parse relative dates
  } else if (dateString.includes('Reviewed')) {
    // Parse absolute dates with "Reviewed" prefix
  } else {
    // Parse other date formats
  }
  
  // Return standardized date format (YYYY-MM-DD)
}
```

### Known Issues

Document any known issues or limitations with this site strategy:

1. **[Issue description]**: [Impact and workaround]
2. **[Issue description]**: [Impact and workaround]

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | YYYY-MM-DD | Initial implementation |
| 1.1 | YYYY-MM-DD | Updated selectors for site redesign |
| 1.2 | YYYY-MM-DD | Added handling for new popup type |

### Related Components

- [Scraper Design](../implementation/scraper_design.md)
- [Data Processing](../implementation/data_processing.md)
- [Anti-Bot Measures](../implementation/anti_bot_measures.md)
