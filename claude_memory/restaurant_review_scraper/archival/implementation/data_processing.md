---
title: "Data Processing"
category: "archival/implementation"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
components: ["data", "processing", "extraction", "analysis"]
keywords: ["data", "reviews", "extraction", "cleaning", "sentiment", "categorization", "CSV", "export"]
---

# Data Processing

## Purpose

This document details how review data is extracted, processed, cleaned, and transformed within the restaurant review scraper. It covers the entire pipeline from raw HTML extraction to final CSV output, including text processing, categorization, and sentiment analysis.

## Data Extraction Overview

The data extraction process converts raw HTML from review sites into structured data through several stages:

1. **HTML Parsing**: Extract relevant DOM elements containing review information
2. **Data Normalization**: Convert platform-specific formats to a unified schema
3. **Text Cleaning**: Remove irrelevant content and standardize formatting
4. **Metadata Extraction**: Capture dates, ratings, reviewer names, etc.
5. **Enrichment**: Add categorization and sentiment analysis
6. **Export**: Format data for CSV export

## Review Data Model

Each review is represented by a standardized data model:

```javascript
const reviewSchema = {
  platform: String,         // "tripadvisor", "yelp", "google"
  restaurantName: String,   // Name of the restaurant
  reviewerName: String,     // Name of the reviewer
  rating: Number,           // Star rating (1-5)
  date: String,             // Original date format from platform
  standardizedDate: String, // Normalized date (YYYY-MM-DD)
  text: String,             // Full review text
  category: String,         // Automatically classified category
  sentiment: String,        // "positive", "neutral", "negative"
  metadata: {
    // Platform-specific additional data
    replyText: String,      // Restaurant's reply (if any)
    replyDate: String,      // Date of restaurant's reply
    helpful: Number,        // Number of helpful votes
    // Other metadata fields as available
  }
};
```

## Platform-Specific Extraction

Each platform requires specialized extraction techniques:

### TripAdvisor Extraction

```javascript
async function extractTripAdvisorReviews(page) {
  return page.evaluate(() => {
    const reviews = [];
    const reviewElements = document.querySelectorAll('.review-container');
    
    for (const element of reviewElements) {
      // Extract detailed review data from specific selectors
      const reviewerNameEl = element.querySelector('.info_text div');
      const ratingEl = element.querySelector('.ui_bubble_rating');
      const dateEl = element.querySelector('.ratingDate');
      const textEl = element.querySelector('.reviewText');
      
      // Process and normalize the data
      // Add to reviews array
    }
    
    return reviews;
  });
}
```

### Yelp Extraction

```javascript
async function extractYelpReviews(page) {
  return page.evaluate(() => {
    const reviews = [];
    const reviewElements = document.querySelectorAll('ul.undefined li .review');
    
    for (const element of reviewElements) {
      // Yelp-specific extraction logic
      // Extract and normalize data
    }
    
    return reviews;
  });
}
```

### Google Reviews Extraction

```javascript
async function extractGoogleReviews(page) {
  return page.evaluate(() => {
    const reviews = [];
    const reviewElements = document.querySelectorAll('.jftiEf');
    
    for (const element of reviewElements) {
      // Google-specific extraction logic
      // Extract and normalize data
    }
    
    return reviews;
  });
}
```

## Data Cleaning

Data cleaning is applied to the raw extraction results:

1. **HTML Removal**: Strip any HTML tags from review text
2. **Special Character Handling**: Normalize special characters and emoji
3. **Whitespace Normalization**: Remove excess whitespace and normalize line breaks
4. **Text Truncation Detection**: Detect and handle truncated reviews with "read more" links
5. **Date Parsing**: Convert various date formats to a standardized date format

```javascript
function cleanReviewText(text) {
  if (!text) return '';
  
  // Remove HTML tags
  let cleaned = text.replace(/<[^>]*>/g, '');
  
  // Normalize whitespace
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  
  // Handle special characters
  cleaned = cleaned.normalize('NFC');
  
  return cleaned;
}

function parseDate(dateText, platform) {
  // Platform-specific date parsing logic
  // Returns a standardized YYYY-MM-DD format
}
```

## Review Categorization

The automatic categorization system works by:

1. Analyzing review text for key terms and phrases
2. Matching against predefined category keywords
3. Using NLP techniques to identify themes
4. Assigning the most relevant category or categories

Main review categories:

1. Food Quality
2. Service
3. Atmosphere/Environment
4. Pricing
5. Cleanliness
6. Wait Times
7. Product Availability

```javascript
function categorizeReview(reviewText) {
  const categories = {
    foodQuality: ['food', 'taste', 'flavor', 'delicious', 'menu', 'dish', 'meal'],
    service: ['service', 'staff', 'waiter', 'waitress', 'server', 'friendly', 'attentive'],
    atmosphere: ['atmosphere', 'ambiance', 'decor', 'noise', 'music', 'comfortable', 'setting'],
    pricing: ['price', 'expensive', 'cheap', 'value', 'worth', 'overpriced', 'affordable'],
    cleanliness: ['clean', 'dirty', 'hygiene', 'sanitary', 'spotless', 'filthy'],
    waitTimes: ['wait', 'long', 'quick', 'slow', 'fast', 'promptly', 'delay'],
    availability: ['available', 'sold out', 'menu item', 'run out', 'special', 'seasonal']
  };
  
  // Simplified example - actual implementation uses more sophisticated NLP
  let scores = {};
  for (const [category, keywords] of Object.entries(categories)) {
    scores[category] = keywords.reduce((score, word) => {
      return score + (reviewText.toLowerCase().includes(word.toLowerCase()) ? 1 : 0);
    }, 0);
  }
  
  // Return the category with the highest score
  return Object.keys(scores).reduce((a, b) => scores[a] > scores[b] ? a : b);
}
```

## Sentiment Analysis

Sentiment analysis classifies reviews as positive, neutral, or negative:

1. **Basic Approach**: Lexicon-based analysis with positive/negative word counting
2. **Enhanced Approach**: Machine learning model trained on restaurant reviews
3. **Hybrid Approach**: Combined rule-based and ML approach for better accuracy

```javascript
function analyzeSentiment(reviewText, rating) {
  // If we have a star rating, use it as a strong signal
  if (rating >= 4) return 'positive';
  if (rating <= 2) return 'negative';
  
  // For mid-range ratings or missing ratings, analyze the text
  // Simplified example - actual implementation uses more sophisticated NLP
  const positiveWords = ['great', 'excellent', 'good', 'delicious', 'amazing', 'love', 'perfect', 'wonderful'];
  const negativeWords = ['bad', 'terrible', 'poor', 'disappointing', 'awful', 'rude', 'slow', 'overpriced'];
  
  const words = reviewText.toLowerCase().split(/\W+/);
  
  let positiveScore = words.reduce((count, word) => 
    count + (positiveWords.includes(word) ? 1 : 0), 0);
  
  let negativeScore = words.reduce((count, word) => 
    count + (negativeWords.includes(word) ? 1 : 0), 0);
  
  if (positiveScore > negativeScore * 1.5) return 'positive';
  if (negativeScore > positiveScore * 1.5) return 'negative';
  return 'neutral';
}
```

## CSV Export

The processed review data is exported to CSV files with the following steps:

1. **Format Conversion**: Convert JavaScript objects to CSV-compatible format
2. **Metadata Preparation**: Ensure consistent headers and field organization
3. **File Organization**: Group exports by client and platform as needed
4. **File Writing**: Write to the configured file path with proper encoding

```javascript
function exportToCSV(reviews, filePath) {
  // Define CSV header row
  const header = [
    'Platform', 'Restaurant Name', 'Reviewer Name', 
    'Rating', 'Date', 'Standardized Date', 
    'Text', 'Category', 'Sentiment'
  ];
  
  // Convert each review to a row
  const rows = reviews.map(review => [
    review.platform,
    review.restaurantName,
    review.reviewerName,
    review.rating,
    review.date,
    review.standardizedDate,
    review.text,
    review.category,
    review.sentiment
  ]);
  
  // Combine header and rows
  const csvContent = [header, ...rows]
    .map(row => row.map(field => {
      // Properly escape fields with quotes if they contain commas
      if (typeof field === 'string' && (field.includes(',') || field.includes('"'))) {
        return `"${field.replace(/"/g, '""')}"`;
      }
      return field;
    }).join(','))
    .join('\n');
  
  // Write to file
  fs.writeFileSync(filePath, csvContent, 'utf8');
}
```

## Multi-Client Data Handling

For multi-client scenarios, the system:

1. Organizes data in separate directories for each client
2. Uses the client ID from `clients.json` for directory naming
3. Maintains separate CSV files for each client
4. Applies client-specific filtering based on configuration

## Related Components

- [Scraper Design](scraper_design.md)
- [Anti-Bot Measures](anti_bot_measures.md)
- [Site-Specific Scraping Strategies](../config/site_strategies.md)
