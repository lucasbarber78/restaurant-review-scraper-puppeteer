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
          get: () => originalOnIceCandidate,
          set: function(callback) {
            // Wrap the callback to filter out local IP candidates
            originalOnIceCandidate = function(event) {
              if (event && event.candidate) {
                // Filter out candidates that might reveal local IPs
                if (event.candidate.candidate.indexOf('typ host') !== -1) {
                  // Replace the event with a null event
                  event = Object.assign({}, event, { candidate: null });
                }
              }
              
              if (callback) {
                return callback(event);
              }
            };
          }
        });
        
        return pc;
      };
      
      // Replace the original RTCPeerConnection
      window.RTCPeerConnection = newRTCPeerConnection;
      window.webkitRTCPeerConnection = newRTCPeerConnection;
      window.mozRTCPeerConnection = newRTCPeerConnection;
    }
  });
};
```

## User Profile Management

To maintain consistency across sessions, the scraper uses a profile management system:

```javascript
// User profile management
class BrowserProfileManager {
  constructor(config) {
    this.profiles = config.browser_profiles || [];
    this.currentProfileIndex = 0;
    
    // If no profiles are configured, create a default set
    if (this.profiles.length === 0) {
      this.generateDefaultProfiles();
    }
  }
  
  generateDefaultProfiles() {
    // Generate a set of realistic browser profiles
    const operatingSystems = ['Windows', 'MacOS', 'Linux'];
    const browserVersions = ['90', '91', '92', '93', '94'];
    
    for (const os of operatingSystems) {
      for (const version of browserVersions) {
        this.profiles.push(this.createProfile(os, version));
      }
    }
  }
  
  createProfile(os, browserVersion) {
    const userAgents = {
      'Windows': `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${browserVersion}.0.4472.124 Safari/537.36`,
      'MacOS': `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${browserVersion}.0.4472.124 Safari/537.36`,
      'Linux': `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${browserVersion}.0.4472.124 Safari/537.36`
    };
    
    return {
      userAgent: userAgents[os],
      platform: os === 'Windows' ? 'Win32' : os === 'MacOS' ? 'MacIntel' : 'Linux x86_64',
      screenResolution: {
        width: 1920,
        height: 1080
      },
      viewport: {
        width: 1280,
        height: 800
      },
      language: 'en-US',
      colorDepth: 24,
      deviceMemory: 8,
      hardwareConcurrency: 8,
      timezone: 'America/New_York',
      plugins: [
        'Chrome PDF Plugin',
        'Chrome PDF Viewer',
        'Native Client'
      ]
    };
  }
  
  getNextProfile() {
    const profile = this.profiles[this.currentProfileIndex];
    this.currentProfileIndex = (this.currentProfileIndex + 1) % this.profiles.length;
    return profile;
  }
  
  getProfileForClient(clientId) {
    // Ensure the same client always gets the same profile
    const profileIndex = this.getHashCode(clientId) % this.profiles.length;
    return this.profiles[profileIndex];
  }
  
  getHashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }
  
  applyProfileToPage(page, profile) {
    return Promise.all([
      // Set user agent
      page.setUserAgent(profile.userAgent),
      
      // Set viewport
      page.setViewport({
        width: profile.viewport.width,
        height: profile.viewport.height,
        deviceScaleFactor: 1,
      }),
      
      // Apply browser properties
      page.evaluateOnNewDocument((p) => {
        // Override navigator properties
        Object.defineProperty(navigator, 'platform', { get: () => p.platform });
        Object.defineProperty(navigator, 'userAgent', { get: () => p.userAgent });
        Object.defineProperty(navigator, 'language', { get: () => p.language });
        Object.defineProperty(navigator, 'languages', { get: () => [p.language, 'en'] });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => p.deviceMemory });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => p.hardwareConcurrency });
        
        // Override screen properties
        Object.defineProperty(screen, 'width', { get: () => p.screenResolution.width });
        Object.defineProperty(screen, 'height', { get: () => p.screenResolution.height });
        Object.defineProperty(screen, 'colorDepth', { get: () => p.colorDepth });
        
        // Set timezone
        Object.defineProperty(Intl, 'DateTimeFormat', {
          get: () => function() {
            return { resolvedOptions: () => ({ timeZone: p.timezone }) };
          }
        });
      }, profile)
    ]);
  }
}
```

## Human-Like Behavior Simulation

The scraper simulates human behavior patterns:

```javascript
// Human behavior simulation
const simulateHumanBehavior = async (page) => {
  // Random scrolling
  await randomScrolling(page);
  
  // Random mouse movements
  await randomMouseMovements(page);
  
  // Random pauses
  await randomPauses();
};

// Random scrolling implementation
const randomScrolling = async (page) => {
  // Get page height
  const pageHeight = await page.evaluate(() => document.body.scrollHeight);
  
  // Determine number of scroll steps (more for longer pages)
  const scrollSteps = Math.min(10, Math.max(2, Math.floor(pageHeight / 1000)));
  
  for (let i = 0; i < scrollSteps; i++) {
    // Calculate target position (not perfectly sequential)
    const targetPos = Math.floor((i / scrollSteps) * pageHeight * (0.85 + Math.random() * 0.15));
    
    // Scroll with variable speed
    await page.evaluate((pos) => {
      // Use smooth scroll with variable duration
      const duration = 500 + Math.random() * 1000; // 500-1500ms
      const start = window.scrollY;
      const change = pos - start;
      const startTime = performance.now();
      
      // Easing function for natural movement
      function easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      }
      
      function animateScroll() {
        const currentTime = performance.now();
        const elapsed = currentTime - startTime;
        
        if (elapsed < duration) {
          const progress = elapsed / duration;
          window.scrollTo(0, start + change * easeInOutQuad(progress));
          requestAnimationFrame(animateScroll);
        } else {
          window.scrollTo(0, pos);
        }
      }
      
      animateScroll();
    }, targetPos);
    
    // Wait for scroll to complete with a variable delay
    await page.waitForTimeout(800 + Math.random() * 1200);
    
    // Occasionally scroll back up slightly (like a human reviewing content)
    if (Math.random() < 0.3 && i > 1) {
      const backtrackAmount = Math.floor(Math.random() * 300);
      await page.evaluate((amt) => {
        window.scrollBy(0, -amt);
      }, backtrackAmount);
      
      await page.waitForTimeout(500 + Math.random() * 1000);
    }
  }
};

// Random mouse movements
const randomMouseMovements = async (page) => {
  // Get viewport size
  const viewport = page.viewport();
  
  // Generate random points within the viewport
  const numPoints = 3 + Math.floor(Math.random() * 5);
  const points = [];
  
  for (let i = 0; i < numPoints; i++) {
    points.push({
      x: Math.floor(Math.random() * viewport.width * 0.8) + viewport.width * 0.1,
      y: Math.floor(Math.random() * viewport.height * 0.8) + viewport.height * 0.1
    });
  }
  
  // Move mouse through these points
  for (const point of points) {
    await page.mouse.move(point.x, point.y, { steps: 10 + Math.floor(Math.random() * 15) });
    await page.waitForTimeout(100 + Math.random() * 400);
  }
};

// Random pauses
const randomPauses = async () => {
  // Introduce random pauses to simulate human reading/thinking
  if (Math.random() < 0.7) {
    // 70% chance of a short pause
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
  } else if (Math.random() < 0.3) {
    // 30% chance of a longer pause
    await new Promise(resolve => setTimeout(resolve, 3000 + Math.random() * 5000));
  }
};
```

## Related Components

- [Anti-Bot Measures](anti_bot_measures.md)
- [Proxy Management](proxy_management.md)
- [Scraper Design](scraper_design.md)
