---
title: "API Overview"
category: "api"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "medium"
tags: ["api", "integration", "endpoints", "fastapi"]
related_documents:
  - "claude_memory/restaurant_review_scraper/core/architecture.md"
  - "claude_memory/restaurant_review_scraper/core/requirements.md"
---

# API Overview

## Introduction

The Restaurant Review Scraper includes a REST API component that enables programmatic access to scraper functionality and data. This document provides a comprehensive overview of the API architecture, endpoints, and usage.

## API Architecture

The API is built using FastAPI, a modern, high-performance web framework for building APIs with Python. The architecture follows RESTful principles and includes:

- OpenAPI/Swagger documentation
- Pydantic model validation
- Proper HTTP status codes
- Authentication and authorization
- Structured error responses

### Component Diagram

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│  API Gateway   ├────►│ API Endpoints  ├────►│  Core Scraper  │
│                │     │                │     │                │
└────────────────┘     └──────┬─────────┘     └────────────────┘
                              │
                      ┌───────┴─────────┐
                      │                 │
                      │  Data Storage   │
                      │                 │
                      └─────────────────┘
```

## Endpoints

The API provides the following endpoint categories:

### Scraper Control Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scrape` | POST | Start a new scraping job |
| `/api/v1/scrape/{job_id}` | GET | Get status of a running job |
| `/api/v1/scrape/{job_id}` | DELETE | Cancel a running job |
| `/api/v1/scrape/batch` | POST | Start multiple scraping jobs |

### Data Access Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/reviews` | GET | Query and filter review data |
| `/api/v1/reviews/{review_id}` | GET | Get a specific review by ID |
| `/api/v1/restaurants` | GET | Query restaurant information |
| `/api/v1/restaurants/{restaurant_id}` | GET | Get a specific restaurant by ID |
| `/api/v1/export` | POST | Generate and download data exports |

### Configuration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/config` | GET | List available configurations |
| `/api/v1/config` | POST | Create a new configuration |
| `/api/v1/config/{config_id}` | GET | Get a specific configuration |
| `/api/v1/config/{config_id}` | PUT | Update a configuration |
| `/api/v1/config/{config_id}` | DELETE | Delete a configuration |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/users` | GET | List API users (admin only) |
| `/api/v1/admin/stats` | GET | Get API usage statistics |
| `/api/v1/admin/logs` | GET | Access API and scraper logs |

## Authentication

The API supports multiple authentication methods:

1. **API Key Authentication**
   - Provide your API key in the `X-API-Key` header
   - Used for programmatic access

2. **OAuth2 Authentication**
   - JWT token-based authentication
   - Required for admin endpoints
   - Supports role-based access control

3. **Basic Authentication**
   - Username/password authentication
   - For development/testing only

## Request Examples

### Starting a Scraping Job

```json
POST /api/v1/scrape
Content-Type: application/json
X-API-Key: your_api_key

{
  "restaurant_name": "Sample Restaurant",
  "urls": {
    "tripadvisor": "https://www.tripadvisor.com/Restaurant_Review-...",
    "yelp": "https://www.yelp.com/biz/...",
    "google": "https://www.google.com/maps/place/..."
  },
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-04-27"
  },
  "options": {
    "max_reviews": 100,
    "platforms": ["tripadvisor", "yelp", "google"],
    "anti_bot_settings": {
      "enable_stealth": true,
      "enable_proxy_rotation": false
    }
  }
}
```

### Querying Reviews

```
GET /api/v1/reviews?restaurant=Sample+Restaurant&min_rating=4&platform=tripadvisor&limit=50&offset=0
X-API-Key: your_api_key
```

## Response Format

All API responses follow a standardized format:

```json
{
  "success": true,
  "data": { 
    // Response data here
  },
  "metadata": {
    "timestamp": "2025-04-27T12:34:56Z",
    "request_id": "req_1234567890"
  }
}
```

For error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if available
    }
  },
  "metadata": {
    "timestamp": "2025-04-27T12:34:56Z",
    "request_id": "req_1234567890"
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- Free tier: 100 requests per hour
- Basic tier: 1,000 requests per hour
- Premium tier: 10,000 requests per hour

Rate limit headers are included in all responses:

```
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 995
X-Rate-Limit-Reset: 1619523600
```

## Webhooks

The API supports webhooks for asynchronous notifications:

1. **Job Completion Webhook**
   - Notifies when a scraping job completes
   - Includes job summary and result location

2. **New Review Webhook**
   - Notifies when new reviews are detected
   - Can be filtered by rating, platform, etc.

3. **Error Notification Webhook**
   - Notifies of critical errors during scraping

## Error Codes

Common error codes you may encounter:

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request validation failed |
| `AUTHENTICATION_ERROR` | Invalid or missing API key |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `SCRAPER_ERROR` | Error in the scraping operation |
| `CONFIGURATION_ERROR` | Invalid configuration |

## Security Considerations

The API implements several security measures:

1. **SSL/TLS Encryption**
   - All API traffic is encrypted using HTTPS

2. **API Key Security**
   - Keys can be rotated regularly
   - Per-key rate limiting and permissions

3. **Input Validation**
   - All inputs are strictly validated
   - Protection against injection attacks

4. **Rate Limiting**
   - Protection against brute force attacks
   - Prevents service abuse

## Integration Examples

### Python Client Example

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.restaurant-review-scraper.com/api/v1"

def start_scraping_job(restaurant_name, urls, date_range):
    endpoint = f"{BASE_URL}/scrape"
    headers = {"X-API-Key": API_KEY}
    
    payload = {
        "restaurant_name": restaurant_name,
        "urls": urls,
        "date_range": date_range,
        "options": {
            "platforms": ["tripadvisor", "yelp", "google"]
        }
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()

def get_job_status(job_id):
    endpoint = f"{BASE_URL}/scrape/{job_id}"
    headers = {"X-API-Key": API_KEY}
    
    response = requests.get(endpoint, headers=headers)
    return response.json()
```

### JavaScript Client Example

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.restaurant-review-scraper.com/api/v1';

async function startScrapingJob(restaurantName, urls, dateRange) {
  try {
    const response = await axios.post(
      `${BASE_URL}/scrape`,
      {
        restaurant_name: restaurantName,
        urls: urls,
        date_range: dateRange,
        options: {
          platforms: ['tripadvisor', 'yelp', 'google']
        }
      },
      {
        headers: { 'X-API-Key': API_KEY }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
}

async function getJobStatus(jobId) {
  try {
    const response = await axios.get(
      `${BASE_URL}/scrape/${jobId}`,
      {
        headers: { 'X-API-Key': API_KEY }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
}
```

## Related Documents

- [System Architecture](../../core/architecture.md)
- [Project Requirements](../../core/requirements.md)
