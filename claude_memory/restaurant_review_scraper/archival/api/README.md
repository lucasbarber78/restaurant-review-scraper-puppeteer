---
title: "API Documentation"
category: "archival/api"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "medium"
components: ["api", "documentation", "integration"]
keywords: ["api", "endpoints", "integration", "fastapi", "rest"]
---

# API Documentation

This directory contains documentation for the Restaurant Review Scraper's API interfaces. It covers both internal APIs used by the application components and external APIs for integration with other systems.

## Purpose

The API documentation serves to:

1. Define the interfaces between system components
2. Document REST API endpoints for external integration
3. Provide usage examples for API consumers
4. Explain authentication and security measures
5. Define data models and schemas

## Directory Structure

```
api/
├── README.md                # This file
├── rest_api.md              # REST API documentation
├── internal_apis.md         # Internal component APIs
├── authentication.md        # Authentication and security
├── data_models.md           # API data models and schemas
├── client_integration.md    # Client integration guidelines
├── rate_limiting.md         # API rate limiting guidelines
└── versioning.md            # API versioning strategy
```

## How to Use This Section

### For API Consumers

If you are integrating with the scraper's REST API:

1. Start with [rest_api.md](rest_api.md) to understand available endpoints
2. Read [authentication.md](authentication.md) to learn how to authenticate
3. Check [data_models.md](data_models.md) for response formats
4. Follow [client_integration.md](client_integration.md) for best practices
5. Be aware of [rate_limiting.md](rate_limiting.md) to avoid throttling

### For Developers

If you are developing or modifying the scraper:

1. Refer to [internal_apis.md](internal_apis.md) for component interfaces
2. Follow the API design patterns described in this documentation
3. Update API documentation when making interface changes
4. Adhere to the [versioning.md](versioning.md) guidelines for API changes

## REST API Overview

The scraper provides a REST API for integration with other systems:

### Key Endpoints

- `GET /api/v1/clients`: List configured restaurant clients
- `GET /api/v1/clients/{client_id}/reviews`: Get reviews for a specific client
- `POST /api/v1/scrape`: Trigger a new scraping job
- `GET /api/v1/jobs/{job_id}`: Get scraping job status
- `GET /api/v1/stats`: Get system statistics and metrics

### Authentication Methods

The API supports the following authentication methods:

- API Key authentication (X-API-Key header)
- JWT token authentication (Bearer token)
- Basic authentication (for development only)

### Response Formats

All API endpoints return JSON responses with consistent formatting:

```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 25,
    "total": 100
  }
}
```

Error responses follow a standard format:

```json
{
  "status": "error",
  "error": {
    "code": "resource_not_found",
    "message": "The requested resource was not found",
    "details": { ... }
  }
}
```

## Internal APIs

The internal APIs document the interfaces between components:

- Scraper Core API
- Data Processing API
- Proxy Management API
- Client Management API
- Storage API

These interfaces define how the components interact and exchange data within the application.

## API Design Principles

The API design follows these principles:

1. **RESTful**: Resources are represented by URLs, operations by HTTP methods
2. **Versioned**: All API endpoints include a version in the URL path
3. **Consistent**: Consistent naming, formatting, and error handling
4. **Secure**: Authentication and authorization for all endpoints
5. **Documented**: OpenAPI/Swagger documentation for all endpoints
6. **Paginated**: Collection endpoints support pagination
7. **Filtered**: Collection endpoints support filtering
8. **Rate-limited**: Prevents abuse through rate limiting

## OpenAPI Documentation

The full API specification is available in OpenAPI format:

- Swagger UI: `/api/docs` when the service is running
- OpenAPI JSON: `/api/openapi.json`

## API Versioning

API versions are managed according to the following guidelines:

- Major version changes (v1 → v2) for breaking changes
- Minor version changes for backward-compatible additions
- Deprecated endpoints are marked with `Deprecated` header
- Multiple API versions may be supported simultaneously during transitions

## Rate Limiting

API requests are subject to rate limiting:

- 100 requests per minute per IP address
- 1000 requests per day per authenticated client
- Special limits apply to resource-intensive operations
- Rate limit headers (`X-RateLimit-*`) included in responses

## Client Libraries

Official client libraries for the API:

- Python: `restaurant-scraper-client`
- JavaScript: `restaurant-scraper-js-client`
- PHP: `restaurant-scraper-php`

## Related Sections

- [Implementation Documentation](../implementation/README.md): Technical implementation details
- [Configuration Documentation](../config/README.md): Configuration and customization
