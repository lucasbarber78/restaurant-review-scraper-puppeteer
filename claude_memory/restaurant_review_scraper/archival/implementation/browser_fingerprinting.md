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
               "AAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sJDw4cOCW1/KIAAAAZdEVYdENv" +
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
          set: function(handler) {
            // Create wrapper for the handler that filters out IP addresses
            const iceHandler = function(event) {
              if (event && event.candidate && event.candidate.candidate) {
                // Filter out candidates containing private IPs
                if (!/192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|10\./.test(event.candidate.candidate)) {
                  handler(event);
                } else {
                  // Create a new event without the candidate
                  const newEvent = new Event('icecandidate');
                  newEvent.candidate = null;
                  handler(newEvent);
                }
              } else {
                handler(event);
              }
            };
            
            originalOnIceCandidate = iceHandler;
          }
        });
        
        return pc;
      };
      
      // Replace the original RTCPeerConnection
      window.RTCPeerConnection = newRTCPeerConnection;
      if (window.webkitRTCPeerConnection) {
        window.webkitRTCPeerConnection = newRTCPeerConnection;
      }
      if (window.mozRTCPeerConnection) {
        window.mozRTCPeerConnection = newRTCPeerConnection;
      }
    }
  });
};
```

## Human Behavior Simulation

To evade behavioral detection, the scraper simulates human browsing patterns:

### Mouse Movement Simulation

```javascript
// Simulate realistic mouse movements
const simulateMouseMovement = async (page, targetSelector) => {
  await page.evaluate((selector) => {
    // Get target element
    const target = document.querySelector(selector);
    if (!target) return;
    
    const rect = target.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    // Current mouse position (assume center of viewport)
    let currentX = window.innerWidth / 2;
    let currentY = window.innerHeight / 2;
    
    // Calculate distance
    const distance = Math.sqrt(
      Math.pow(centerX - currentX, 2) + 
      Math.pow(centerY - currentY, 2)
    );
    
    // More points for longer distances
    const numPoints = Math.max(10, Math.min(25, Math.floor(distance / 10)));
    
    // Bezier curve control points (add some randomness)
    const cp1x = currentX + (centerX - currentX) * (0.2 + Math.random() * 0.2);
    const cp1y = currentY + (centerY - currentY) * (0.2 + Math.random() * 0.2);
    const cp2x = currentX + (centerX - currentX) * (0.8 - Math.random() * 0.2);
    const cp2y = currentY + (centerY - currentY) * (0.8 - Math.random() * 0.2);
    
    // Generate points along a bezier curve
    const points = [];
    for (let i = 0; i <= numPoints; i++) {
      const t = i / numPoints;
      
      // Bezier curve formula
      const x = Math.pow(1-t, 3) * currentX + 
                3 * Math.pow(1-t, 2) * t * cp1x + 
                3 * (1-t) * Math.pow(t, 2) * cp2x + 
                Math.pow(t, 3) * centerX;
                
      const y = Math.pow(1-t, 3) * currentY + 
                3 * Math.pow(1-t, 2) * t * cp1y + 
                3 * (1-t) * Math.pow(t, 2) * cp2y + 
                Math.pow(t, 3) * centerY;
                
      points.push({ x, y });
    }
    
    // Dispatch mouse events
    points.forEach(({ x, y }) => {
      const event = new MouseEvent('mousemove', {
        bubbles: true,
        cancelable: true,
        view: window,
        clientX: x,
        clientY: y
      });
      document.elementFromPoint(x, y)?.dispatchEvent(event);
    });
    
    // Hover over target
    const hoverEvent = new MouseEvent('mouseover', {
      bubbles: true,
      cancelable: true,
      view: window,
      clientX: centerX,
      clientY: centerY
    });
    target.dispatchEvent(hoverEvent);
  }, targetSelector);
};
```

### Natural Scrolling Patterns

```javascript
// Simulate human-like scrolling
const simulateHumanScrolling = async (page, scrollDistance) => {
  await page.evaluate((distance) => {
    return new Promise((resolve) => {
      // Start position
      let position = 0;
      const scrollSteps = Math.max(5, Math.floor(Math.abs(distance) / 100));
      const scrollTime = 500 + Math.random() * 1000; // 500-1500ms
      const interval = scrollTime / scrollSteps;
      
      // Sometimes scroll in small steps (like a human)
      let scrollPattern = [];
      
      if (Math.random() < 0.7) {
        // Smooth scroll with occasional pause
        for (let i = 0; i < scrollSteps; i++) {
          const progress = i / (scrollSteps - 1);
          const easeInOut = progress < 0.5
            ? 2 * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 2) / 2;
          
          const step = Math.round(distance * easeInOut) - position;
          position += step;
          scrollPattern.push({ step, delay: interval });
          
          // Random pause in scrolling (10% chance)
          if (Math.random() < 0.1 && i < scrollSteps - 2) {
            scrollPattern.push({ step: 0, delay: 300 + Math.random() * 700 });
          }
        }
      } else {
        // Continuous smooth scroll
        for (let i = 0; i < scrollSteps; i++) {
          const progress = i / (scrollSteps - 1);
          // Use easing function to simulate natural acceleration/deceleration
          const easeInOut = progress < 0.5
            ? 2 * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 2) / 2;
          
          const step = Math.round(distance * easeInOut) - position;
          position += step;
          scrollPattern.push({ step, delay: interval });
        }
      }
      
      // Execute the scroll pattern
      let patternIndex = 0;
      
      function executeNextScroll() {
        if (patternIndex >= scrollPattern.length) {
          resolve();
          return;
        }
        
        const { step, delay } = scrollPattern[patternIndex++];
        window.scrollBy(0, step);
        
        setTimeout(executeNextScroll, delay);
      }
      
      executeNextScroll();
    });
  }, scrollDistance);
};
```

## Timing Pattern Simulation

Humans don't perform actions at consistent intervals. Our system uses variable timing:

```javascript
// Generate human-like delay
const humanDelay = (actionType) => {
  const base = {
    click: 200,
    type: 50,
    scroll: 300,
    navigation: 1200,
    thinking: 2000
  }[actionType] || 500;
  
  // Add randomization with Gaussian distribution
  // Box-Muller transform for normal distribution
  const u1 = Math.random();
  const u2 = Math.random();
  const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  
  // Mean of base, standard deviation of base/4
  const delay = base + (z0 * base / 4);
  
  // Ensure minimum delay of base/2
  return Math.max(base / 2, delay);
};
```

## Advanced Fingerprinting Defenses

For sites with sophisticated anti-bot systems, we implement additional defenses:

```javascript
// Advanced stealth plugins
const setupAdvancedStealth = async (page) => {
  // Mask Puppeteer evaluation
  await page.evaluateOnNewDocument(() => {
    // Hide that we're evaluating scripts
    const originalEval = window.eval;
    window.eval = function(...args) {
      if (args[0] && typeof args[0] === 'string') {
        const lowerCaseStr = args[0].toLowerCase();
        
        // Detect fingerprinting scripts
        if (lowerCaseStr.includes('selenium') || 
            lowerCaseStr.includes('webdriver') || 
            lowerCaseStr.includes('puppeteer') ||
            lowerCaseStr.includes('automation')) {
          // Return false for detection scripts
          return false;
        }
      }
      return originalEval.apply(this, args);
    };
  });
  
  // Prevent notification detection
  await page.evaluateOnNewDocument(() => {
    // Override permission query API
    const originalQuery = Notification.requestPermission;
    Notification.requestPermission = function() {
      return Promise.resolve('default');
    };
    
    // Force permission state to be 'default'
    if (navigator.permissions) {
      const originalQuery = navigator.permissions.query;
      navigator.permissions.query = function(options) {
        if (options.name === 'notifications') {
          return Promise.resolve({ state: 'default', onchange: null });
        }
        return originalQuery.apply(this, arguments);
      };
    }
  });
  
  // Handle timezone consistency
  await page.evaluateOnNewDocument(() => {
    // Use a consistent timezone offset
    const originalDate = Date;
    const timezone = -4; // EDT, adjust based on your proxy location
    
    // Override Date to use consistent timezone
    Date = class extends originalDate {
      constructor(...args) {
        super(...args);
        if (args.length === 0) {
          this.d = new originalDate();
        } else {
          this.d = new originalDate(...args);
        }
      }
      
      getTimezoneOffset() {
        return timezone * 60;
      }
    };
    
    // Copy all original Date properties
    Object.getOwnPropertyNames(originalDate).forEach(prop => {
      if (prop !== 'prototype') {
        Date[prop] = originalDate[prop];
      }
    });
    
    // Override prototype methods
    Object.getOwnPropertyNames(originalDate.prototype).forEach(prop => {
      if (prop !== 'constructor' && prop !== 'getTimezoneOffset') {
        Date.prototype[prop] = function(...args) {
          return this.d[prop](...args);
        };
      }
    });
  });
};
```

## Related Components

- [Anti-Bot Measures](anti_bot_measures.md)
- [Proxy Management](proxy_management.md)
- [Scraper Design](scraper_design.md)
- [Site-Specific Scraping Strategies](../config/site_strategies.md)
