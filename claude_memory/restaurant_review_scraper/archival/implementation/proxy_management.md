---
title: "Proxy Management"
category: "archival/implementation"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
components: ["proxy", "networking", "anti-bot"]
keywords: ["proxy", "rotation", "IP", "blocking", "detection", "avoidance"]
---

# Proxy Management

## Purpose

This document details the proxy management system used in the restaurant review scraper. It explains how the scraper uses proxy rotation to avoid IP-based blocking, configures proxy connections, and handles proxy-related errors.

## Proxy System Overview

The proxy management system provides the following capabilities:

1. **Proxy Rotation**: Changing IP addresses to prevent detection and blocking
2. **Request Distribution**: Spreading requests across multiple proxies
3. **Proxy Health Monitoring**: Tracking proxy performance and errors
4. **Automatic Failover**: Switching to alternative proxies when errors occur
5. **Proxy Configuration**: Setting up and managing proxy connections with Puppeteer

## Proxy Configuration

Proxies are configured in the `config.yaml` file under the proxy_settings section:

```yaml
proxy_settings:
  enable_proxy_rotation: true
  proxy_type: "http"  # http, socks4, or socks5
  proxies:
    - host: "proxy1.example.com"
      port: 8080
      username: "user1"
      password: "pass1"
    - host: "proxy2.example.com"
      port: 8080
      username: "user2"
      password: "pass2"
  # More proxy configuration options...
  rotation_strategy: "round-robin"  # round-robin, random, error-based
  max_consecutive_requests: 10      # Max requests before rotating
  error_threshold: 3                # Number of errors before marking proxy as unhealthy
  health_check_url: "https://httpbin.org/ip"  # URL to test proxy health
```

## Proxy Integration with Puppeteer

Puppeteer is configured to use proxies through launch arguments:

```javascript
const setupProxyForBrowser = async (proxyInfo) => {
  const args = [
    `--proxy-server=${proxyInfo.type}://${proxyInfo.host}:${proxyInfo.port}`
  ];
  
  // Launch browser with proxy configuration
  const browser = await puppeteer.launch({
    headless: config.anti_bot_settings.headless_mode,
    args: [
      ...args,
      // Other browser arguments
    ]
  });
  
  // If proxy requires authentication
  if (proxyInfo.username && proxyInfo.password) {
    const page = await browser.newPage();
    await page.authenticate({
      username: proxyInfo.username,
      password: proxyInfo.password
    });
  }
  
  return browser;
};
```

## Proxy Rotation Strategies

The system supports multiple rotation strategies:

### Round-Robin Strategy

Cycles through the list of proxies sequentially:

```javascript
class RoundRobinRotationStrategy {
  constructor(proxies) {
    this.proxies = proxies;
    this.currentIndex = 0;
  }
  
  getNextProxy() {
    const proxy = this.proxies[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % this.proxies.length;
    return proxy;
  }
}
```

### Random Strategy

Selects proxies randomly from the available pool:

```javascript
class RandomRotationStrategy {
  constructor(proxies) {
    this.proxies = proxies;
  }
  
  getNextProxy() {
    const randomIndex = Math.floor(Math.random() * this.proxies.length);
    return this.proxies[randomIndex];
  }
}
```

### Error-Based Strategy

Avoids proxies that have recently encountered errors:

```javascript
class ErrorBasedRotationStrategy {
  constructor(proxies, errorThreshold = 3) {
    this.proxies = proxies;
    this.errorCounts = new Map();
    this.errorThreshold = errorThreshold;
    
    // Initialize error counts
    proxies.forEach(proxy => {
      this.errorCounts.set(this.getProxyKey(proxy), 0);
    });
  }
  
  getProxyKey(proxy) {
    return `${proxy.host}:${proxy.port}`;
  }
  
  reportError(proxy) {
    const key = this.getProxyKey(proxy);
    const currentErrors = this.errorCounts.get(key) || 0;
    this.errorCounts.set(key, currentErrors + 1);
  }
  
  isProxyHealthy(proxy) {
    const key = this.getProxyKey(proxy);
    return (this.errorCounts.get(key) || 0) < this.errorThreshold;
  }
  
  getHealthyProxies() {
    return this.proxies.filter(proxy => this.isProxyHealthy(proxy));
  }
  
  getNextProxy() {
    const healthyProxies = this.getHealthyProxies();
    
    // If no healthy proxies, reset error counts and use all proxies
    if (healthyProxies.length === 0) {
      this.proxies.forEach(proxy => {
        this.errorCounts.set(this.getProxyKey(proxy), 0);
      });
      return this.proxies[0];
    }
    
    // Otherwise, return a random healthy proxy
    const randomIndex = Math.floor(Math.random() * healthyProxies.length);
    return healthyProxies[randomIndex];
  }
}
```

## Proxy Health Monitoring

The system monitors proxy health by:

1. Tracking errors associated with each proxy
2. Performing periodic health checks against a known endpoint
3. Marking proxies as unhealthy when they exceed error thresholds
4. Restoring proxies to the active pool after a cooling period

```javascript
class ProxyHealthMonitor {
  constructor(proxies, config) {
    this.proxies = proxies;
    this.healthCheckUrl = config.health_check_url || 'https://httpbin.org/ip';
    this.errorThreshold = config.error_threshold || 3;
    this.cooldownPeriod = config.cooldown_period || 300000; // 5 minutes in ms
    
    this.proxyStatus = new Map();
    this.initializeProxyStatus();
  }
  
  initializeProxyStatus() {
    this.proxies.forEach(proxy => {
      this.proxyStatus.set(this.getProxyKey(proxy), {
        healthy: true,
        errorCount: 0,
        lastError: null,
        cooldownUntil: null
      });
    });
  }
  
  getProxyKey(proxy) {
    return `${proxy.host}:${proxy.port}`;
  }
  
  async checkProxyHealth(proxy) {
    const browser = await setupProxyForBrowser(proxy);
    
    try {
      const page = await browser.newPage();
      const response = await page.goto(this.healthCheckUrl, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });
      
      await browser.close();
      
      return response.status() === 200;
    } catch (error) {
      console.error(`Health check failed for proxy ${proxy.host}:${proxy.port}`, error);
      await browser.close();
      return false;
    }
  }
  
  async performHealthChecks() {
    console.log('Performing health checks on all proxies...');
    
    for (const proxy of this.proxies) {
      const key = this.getProxyKey(proxy);
      const status = this.proxyStatus.get(key);
      
      // Skip proxies in cooldown
      if (status.cooldownUntil && status.cooldownUntil > Date.now()) {
        continue;
      }
      
      const isHealthy = await this.checkProxyHealth(proxy);
      
      status.healthy = isHealthy;
      if (isHealthy) {
        status.errorCount = 0;
        status.cooldownUntil = null;
      }
      
      this.proxyStatus.set(key, status);
    }
  }
  
  reportError(proxy, error) {
    const key = this.getProxyKey(proxy);
    const status = this.proxyStatus.get(key) || {
      healthy: true,
      errorCount: 0,
      lastError: null,
      cooldownUntil: null
    };
    
    status.errorCount += 1;
    status.lastError = error;
    
    if (status.errorCount >= this.errorThreshold) {
      status.healthy = false;
      status.cooldownUntil = Date.now() + this.cooldownPeriod;
    }
    
    this.proxyStatus.set(key, status);
  }
  
  getHealthyProxies() {
    return this.proxies.filter(proxy => {
      const key = this.getProxyKey(proxy);
      const status = this.proxyStatus.get(key);
      
      if (!status) return true;
      
      // If in cooldown period, consider unhealthy
      if (status.cooldownUntil && status.cooldownUntil > Date.now()) {
        return false;
      }
      
      return status.healthy;
    });
  }
}
```

## Error Handling for Proxy Issues

The scraper implements comprehensive error handling for proxy-related issues:

```javascript
async function handleScraping(platform, config, proxyManager) {
  const proxy = proxyManager.getNextProxy();
  let browser;
  
  try {
    browser = await setupProxyForBrowser(proxy);
    const page = await browser.newPage();
    
    // Scraping implementation
    
    await browser.close();
    // Success - reset error count or report success
    proxyManager.reportSuccess(proxy);
    
  } catch (error) {
    if (browser) {
      await browser.close();
    }
    
    // Determine if the error is proxy-related
    const isProxyError = [
      'net::ERR_PROXY_CONNECTION_FAILED',
      'net::ERR_TUNNEL_CONNECTION_FAILED',
      'net::ERR_PROXY_AUTH_UNSUPPORTED',
      // Other proxy error signatures
    ].some(signature => error.message.includes(signature));
    
    if (isProxyError) {
      console.error(`Proxy error with ${proxy.host}:${proxy.port}:`, error.message);
      proxyManager.reportError(proxy, error);
      
      // Retry with a different proxy if available
      const healthyProxies = proxyManager.getHealthyProxies();
      if (healthyProxies.length > 0) {
        console.log('Retrying with a different proxy...');
        return handleScraping(platform, config, proxyManager);
      }
    }
    
    // Handle other errors
    throw error;
  }
}
```

## Related Components

- [Anti-Bot Measures](anti_bot_measures.md)
- [Browser Fingerprinting](browser_fingerprinting.md)
- [Scraper Design](scraper_design.md)
