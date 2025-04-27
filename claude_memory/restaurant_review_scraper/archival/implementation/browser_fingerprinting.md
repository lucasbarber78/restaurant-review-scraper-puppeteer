---
title: "Browser Fingerprinting"
category: "archival/implementation"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
components: ["anti-bot", "browser", "puppeteer"]
keywords: ["fingerprinting", "browser", "detection", "evasion", "stealth", "puppeteer"]
---

# Browser Fingerprinting

## Purpose

This document explains the browser fingerprinting techniques used in the restaurant review scraper to evade detection by anti-bot systems. It covers how the scraper modifies browser fingerprints, simulates human-like behavior, and implements stealth techniques to avoid being identified as an automated tool.

## Browser Fingerprinting Overview

Browser fingerprinting is a technique used by websites to identify and track users based on browser attributes and behavior. Anti-bot systems use fingerprinting to detect and block automated scrapers. Our strategy involves:

1. **Spoofing Browser Properties**: Modifying properties used for fingerprinting
2. **Behavioral Simulation**: Mimicking human browsing patterns
3. **Canvas Fingerprinting Mitigation**: Preventing canvas-based tracking
4. **WebRTC Masking**: Preventing IP leakage through WebRTC
5. **Consistent User Profiles**: Maintaining consistent fingerprints across sessions

## Browser Property Spoofing

The scraper modifies various browser properties to appear more like a regular user:

```javascript
// Navigator properties spoofing
const spoofNavigator = (page) => {
  return page.evaluateOnNewDocument(() => {
    // User agent consistency
    const userAgent = navigator.userAgent;
    
    // Override properties that reveal automation
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false,
    });
    
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en'],
    });
    
    Object.defineProperty(navigator, 'plugins', {
      get: () => {
        // Return spoofed plugins array that matches our user agent
        return [
          {
            name: 'Chrome PDF Plugin',
            description: 'Portable Document Format',
            filename: 'internal-pdf-viewer',
            length: 1,
            item: () => null,
            namedItem: () => null
          },
          {
            name: 'Chrome PDF Viewer',
            description: '',
            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
            length: 1,
            item: () => null,
            namedItem: () => null
          },
          {
            name: 'Native Client',
            description: '',
            filename: 'internal-nacl-plugin',
            length: 1,
            item: () => null,
            namedItem: () => null
          }
        ];
      },
    });
    
    // Spoof platform to match user agent
    const isWindows = userAgent.includes('Windows');
    const isMac = userAgent.includes('Macintosh');
    const isLinux = userAgent.includes('Linux');
    
    if (isWindows) {
      Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32',
      });
    } else if (isMac) {
      Object.defineProperty(navigator, 'platform', {
        get: () => 'MacIntel',
      });
    } else if (isLinux) {
      Object.defineProperty(navigator, 'platform', {
        get: () => 'Linux x86_64',
      });
    }
    
    // Create consistent hardware concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {
      get: () => 8,
    });
    
    // Create consistent device memory
    Object.defineProperty(navigator, 'deviceMemory', {
      get: () => 8,
    });
  });
};
```

## Canvas Fingerprinting Evasion

Canvas fingerprinting is a technique that draws hidden elements to a canvas and uses the unique rendering characteristics as an identifier. Our approach:

```javascript
// Canvas fingerprinting evasion
const spoofCanvas = (page) => {
  return page.evaluateOnNewDocument(() => {
    // Original methods
    const originalGetImageData = HTMLCanvasElement.prototype.toDataURL;
    const originalToBlob = HTMLCanvasElement.prototype.toBlob;
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    
    // Override toDataURL to add slight noise to the canvas
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
      // Check if this canvas is being used for fingerprinting
      const isFingerprintCanvas = this.width === 16 && this.height === 16;
      
      if (isFingerprintCanvas) {
        // Return a consistent but fake fingerprint
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAA" +
               "AAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sJDw4cOCW1/KIAAAAZdEVYdENv" +
               "bW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAAAHElEQVQ4y2NgGAWjYBSMAv5BwHGEgwQFhkEIAJiUCBy/0L9a";
      }
      
      // For non-fingerprinting uses, add very slight noise to the canvas
      if (this.width > 256 && this.height > 256) {
        const context = this.getContext('2d');
        const imageData = context.getImageData(0, 0, this.width, this.height);
        const data = imageData.data;
        
        // Add subtle noise (barely visible to humans)
        for (let i = 0; i < data.length; i += 4) {
          // Only modify 1 in 1000 pixels
          if (Math.random() < 0.001) {
            data[i] = Math.max(0, Math.min(255, data[i] + (Math.random() * 2 - 1)));
            data[i+1] = Math.max(0, Math.min(255, data[i+1] + (Math.random() * 2 - 1)));
            data[i+2] = Math.max(0, Math.min(255, data[i+2] + (Math.random() * 2 - 1)));
          }
        }
        
        context.putImageData(imageData, 0, 0);
      }
      
      return originalGetImageData.apply(this, arguments);
    };
    
    // Similar approach for toBlob
    HTMLCanvasElement.prototype.toBlob = function() {
      // Similar implementation as toDataURL
      return originalToBlob.apply(this, arguments);
    };
    
    // Override getContext to track when the canvas is being used for WebGL
    HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
      const context = originalGetContext.apply(this, arguments);
      
      if (contextType === 'webgl' || contextType === 'experimental-webgl') {
        // Spoof WebGL parameters and renderer
        const originalGetParameter = context.getParameter;
        
        context.getParameter = function(parameter) {
          // UNMASKED_VENDOR_WEBGL and UNMASKED_RENDERER_WEBGL are often used for fingerprinting
          if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
            return 'Google Inc. (Intel)';
          }
          
          if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
            return 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)';
          }
          
          return originalGetParameter.apply(this, arguments);
        };
      }
      
      return context;
    };
  });
};
```

## WebRTC Protection

WebRTC can leak the real IP address even when using a proxy. Our approach:

```javascript
// WebRTC protection
const protectWebRTC = (page) => {
  return page.evaluateOnNewDocument(() => {
    // Modify the RTCPeerConnection to prevent IP leakage
    const originalRTCPeerConnection = window.RTCPeerConnection || 
      window.webkitRTCPeerConnection || 
      window.mozRTCPeerConnection;
    
    if (originalRTCPeerConnection) {
      const newRTCPeerConnection = function(pc_config, pc_constraints) {
        // If no config is provided, create an empty one
        if (!pc_config) {
          pc_config = {};
        }
        
        // Ensure it has an iceServers property
        if (!pc_config.iceServers) {
          pc_config.iceServers = [{ urls: "stun:stun.l.google.com:19302" }];
        }
        
        // Prevent TURN servers which can leak real IP
        pc_config.iceServers = pc_config.iceServers.filter(server => {
          return !(server.urls && typeof server.urls === "string" && 
                  server.urls.startsWith("turn:"));
        });
        
        // Create a sandboxed RTCPeerConnection
        const pc = new originalRTCPeerConnection(pc_config, pc_constraints);
        
        // Override the onicecandidate handler
        const originalOnIceCandidate = pc.onicecandidate;
        Object.defineProperty(pc, 'onicecandidate', {
          get: function() {
            return originalOnIceCandidate;
          },
          set: function(cb) {
            if (!cb) {
              return originalOnIceCandidate = null;
            }
            
            originalOnIceCandidate = function(e) {
              // If there's no candidate or it's a relay type (TURN), allow it
              if (!e.candidate || (e.candidate.candidate && e.candidate.candidate.indexOf('typ relay') !== -1)) {
                cb(e);
              } else {
                // Otherwise, create a modified event with only a null candidate
                const newEvent = new Event('icecandidate');
                newEvent.candidate = null;
                cb(newEvent);
              }
            };
          }
        });
        
        return pc;
      };
      
      // Replace the RTCPeerConnection
      window.RTCPeerConnection = newRTCPeerConnection;
      window.webkitRTCPeerConnection = newRTCPeerConnection;
      window.mozRTCPeerConnection = newRTCPeerConnection;
    }
  });
};
```

## Timezone and Geolocation Handling

Browser geolocation and timezone can reveal inconsistencies with proxy usage:

```javascript
// Timezone and geolocation spoofing
const spoofLocation = (page, config) => {
  // Target timezone and location that matches the proxy IP
  const targetTimezone = config.spoofing.timezone || 'America/New_York';
  const targetLocation = config.spoofing.location || {
    latitude: 40.7128,    // New York City latitude
    longitude: -74.0060,  // New York City longitude
    accuracy: 100         // Accuracy in meters
  };
  
  return page.evaluateOnNewDocument((tzOffset, location) => {
    // Override Date to return consistent timezone
    const originalDate = Date;
    
    // Create a new Date constructor that modifies getTimezoneOffset
    function ModifiedDate(...args) {
      const date = new originalDate(...args);
      
      // Override timezone offset method (minutes from UTC)
      date.getTimezoneOffset = function() {
        return tzOffset;
      };
      
      return date;
    }
    
    // Copy all original Date properties to our modified Date
    for (const prop in originalDate) {
      if (originalDate.hasOwnProperty(prop)) {
        ModifiedDate[prop] = originalDate[prop];
      }
    }
    
    // Replace the Date constructor
    Date = ModifiedDate;
    
    // Override geolocation API
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition = function(success, error, options) {
        success({
          coords: {
            latitude: location.latitude,
            longitude: location.longitude,
            accuracy: location.accuracy,
            altitude: null,
            altitudeAccuracy: null,
            heading: null,
            speed: null
          },
          timestamp: Date.now()
        });
      };
      
      navigator.geolocation.watchPosition = function(success, error, options) {
        success({
          coords: {
            latitude: location.latitude,
            longitude: location.longitude,
            accuracy: location.accuracy,
            altitude: null,
            altitudeAccuracy: null,
            heading: null,
            speed: null
          },
          timestamp: Date.now()
        });
        
        return Math.floor(Math.random() * 10000); // Random watch ID
      };
    }
  }, getTimezoneOffset(targetTimezone), targetLocation);
};

// Helper function to get timezone offset in minutes based on timezone name
function getTimezoneOffset(timezone) {
  const date = new Date();
  const utcDate = new Date(date.toLocaleString('en-US', { timeZone: 'UTC' }));
  const tzDate = new Date(date.toLocaleString('en-US', { timeZone: timezone }));
  return (utcDate.getTime() - tzDate.getTime()) / 60000;
}
```

## Human-Like Behavioral Simulation

Behavioral patterns can reveal automation. Our solution:

```javascript
// Simulate human-like browsing behavior
const simulateHumanBehavior = (page) => {
  return {
    // Realistic mouse movement with acceleration/deceleration
    async moveMouseTo(selector) {
      const element = await page.$(selector);
      if (!element) return;
      
      const box = await element.boundingBox();
      if (!box) return;
      
      // Start from current mouse position or a random point
      const currentMouse = await page.evaluate(() => ({
        x: window.mouseX || Math.random() * window.innerWidth,
        y: window.mouseY || Math.random() * window.innerHeight
      }));
      
      // Target position (random point within the element)
      const targetX = box.x + box.width * (0.3 + Math.random() * 0.4);
      const targetY = box.y + box.height * (0.3 + Math.random() * 0.4);
      
      // Calculate distance
      const distance = Math.sqrt(
        Math.pow(targetX - currentMouse.x, 2) +
        Math.pow(targetY - currentMouse.y, 2)
      );
      
      // Number of steps based on distance (more steps for longer distances)
      const steps = Math.max(10, Math.min(25, Math.floor(distance / 10)));
      
      // Bezier curve control points for natural movement
      const cp1x = currentMouse.x + (targetX - currentMouse.x) * (0.2 + Math.random() * 0.2);
      const cp1y = currentMouse.y + (targetY - currentMouse.y) * (0.3 + Math.random() * 0.6);
      const cp2x = currentMouse.x + (targetX - currentMouse.x) * (0.8 - Math.random() * 0.2);
      const cp2y = currentMouse.y + (targetY - currentMouse.y) * (0.8 - Math.random() * 0.4);
      
      // Move mouse along the path with variable speed
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        
        // Cubic bezier formula
        const x = Math.pow(1 - t, 3) * currentMouse.x +
                3 * Math.pow(1 - t, 2) * t * cp1x +
                3 * (1 - t) * Math.pow(t, 2) * cp2x +
                Math.pow(t, 3) * targetX;
                
        const y = Math.pow(1 - t, 3) * currentMouse.y +
                3 * Math.pow(1 - t, 2) * t * cp1y +
                3 * (1 - t) * Math.pow(t, 2) * cp2y +
                Math.pow(t, 3) * targetY;
        
        // Move to this position
        await page.mouse.move(x, y);
        
        // Variable delay between movements
        if (i < steps) {
          // Slow at start and end, faster in middle (bell curve)
          const delay = 5 + 15 * Math.exp(-Math.pow((t - 0.5) / 0.15, 2));
          await page.waitForTimeout(delay);
        }
      }
      
      // Store final position for next movement
      await page.evaluate(({x, y}) => {
        window.mouseX = x;
        window.mouseY = y;
      }, {x: targetX, y: targetY});
    },
    
    // Natural scrolling with variable speed and occasional stops
    async scrollToElement(selector, options = {}) {
      const { maxStops = 2, scrollBehavior = 'variable' } = options;
      
      const element = await page.$(selector);
      if (!element) return;
      
      const elementPosition = await page.evaluate(el => {
        const rect = el.getBoundingClientRect();
        return {
          top: rect.top + window.scrollY,
          left: rect.left + window.scrollX
        };
      }, element);
      
      // Current scroll position
      const scrollPosition = await page.evaluate(() => ({
        top: window.scrollY,
        left: window.scrollX
      }));
      
      // Calculate distance to scroll
      const scrollDistance = elementPosition.top - scrollPosition.top;
      
      // Determine number of scroll actions based on distance
      const scrollSteps = Math.max(5, Math.min(20, Math.abs(Math.floor(scrollDistance / 200))));
      
      // Random number of stops while scrolling (to look at content)
      const stops = Math.floor(Math.random() * (maxStops + 1));
      const stopPositions = Array.from({length: stops}, () => 
        Math.floor(Math.random() * (scrollSteps - 1)) + 1
      ).sort((a, b) => a - b);
      
      for (let step = 1; step <= scrollSteps; step++) {
        // Calculate scroll amount for this step
        let scrollAmount;
        
        if (scrollBehavior === 'variable') {
          // Variable speed: slower at start and end, faster in the middle
          const progress = step / scrollSteps;
          const speed = 0.5 + Math.sin(progress * Math.PI) * 0.5;
          scrollAmount = (scrollDistance / scrollSteps) * speed;
        } else {
          // Constant speed
          scrollAmount = scrollDistance / scrollSteps;
        }
        
        // Add a tiny bit of randomness to scroll amount (+/- 5%)
        scrollAmount *= 0.95 + Math.random() * 0.1;
        
        // Execute the scroll
        await page.evaluate(distance => {
          window.scrollBy(0, distance);
        }, scrollAmount);
        
        // If this is a stop position, pause to "read" content
        if (stopPositions.includes(step)) {
          // Random pause between 1-4 seconds
          const pauseTime = 1000 + Math.random() * 3000;
          await page.waitForTimeout(pauseTime);
          
          // Occasionally scroll back up slightly (as humans do when reading)
          if (Math.random() < 0.3) {
            await page.evaluate(() => {
              window.scrollBy(0, -50 - Math.random() * 100);
            });
            await page.waitForTimeout(200 + Math.random() * 500);
          }
        } else {
          // Normal delay between scroll steps
          await page.waitForTimeout(50 + Math.random() * 100);
        }
      }
    }
  };
};
```

## Browser Profile Management

To maintain consistent fingerprints across sessions:

```javascript
class BrowserProfileManager {
  constructor(config) {
    this.profiles = new Map();
    this.profilesPath = config.profiles_path || './browser_profiles';
    this.loadProfiles();
  }
  
  loadProfiles() {
    // Load saved profiles from disk
    try {
      const profileData = fs.readFileSync(this.profilesPath, 'utf8');
      const profiles = JSON.parse(profileData);
      
      for (const [key, profile] of Object.entries(profiles)) {
        this.profiles.set(key, profile);
      }
      
      console.log(`Loaded ${this.profiles.size} browser profiles`);
    } catch (error) {
      console.log('No existing profiles found, will create new ones as needed');
      this.profiles = new Map();
    }
  }
  
  saveProfiles() {
    // Save profiles to disk
    const profileData = {};
    
    for (const [key, profile] of this.profiles.entries()) {
      profileData[key] = profile;
    }
    
    fs.writeFileSync(this.profilesPath, JSON.stringify(profileData, null, 2), 'utf8');
    console.log(`Saved ${this.profiles.size} browser profiles`);
  }
  
  getProfileForClient(clientId) {
    // Get existing profile or create a new one
    if (!this.profiles.has(clientId)) {
      this.profiles.set(clientId, this.generateProfile());
      this.saveProfiles();
    }
    
    return this.profiles.get(clientId);
  }
  
  generateProfile() {
    // Generate a realistic browser profile
    const userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    ];
    
    return {
      userAgent: userAgents[Math.floor(Math.random() * userAgents.length)],
      language: 'en-US,en;q=0.9',
      viewport: {
        width: 1920,
        height: 1080
      },
      timezone: 'America/New_York',
      webglVendor: 'Google Inc. (Intel)',
      webglRenderer: 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
      location: {
        latitude: 40.7128, // New York
        longitude: -74.0060,
        accuracy: 100
      }
    };
  }
}
```

## Puppeteer Stealth Integration

The scraper integrates with puppeteer-extra and puppeteer-extra-plugin-stealth:

```javascript
// Set up Puppeteer with stealth plugins
const setupStealthBrowser = async (config, profile) => {
  const puppeteer = require('puppeteer-extra');
  const StealthPlugin = require('puppeteer-extra-plugin-stealth');
  
  // Configure stealth plugin
  puppeteer.use(StealthPlugin());
  
  // Launch browser with custom arguments
  const browser = await puppeteer.launch({
    headless: config.anti_bot_settings.headless_mode,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-infobars',
      '--window-position=0,0',
      '--ignore-certifcate-errors',
      '--ignore-certifcate-errors-spki-list',
      `--window-size=${profile.viewport.width},${profile.viewport.height}`,
      '--user-agent=' + profile.userAgent
    ],
    defaultViewport: null
  });
  
  return browser;
};
```

## Related Components

- [Anti-Bot Measures](anti_bot_measures.md)
- [Proxy Management](proxy_management.md)
- [Scraper Design](scraper_design.md)
