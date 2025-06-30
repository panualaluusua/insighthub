import { test, expect } from '@playwright/test';

interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
  tti: number; // Time to Interactive
}

test.describe('Performance Monitoring', () => {
  
  test('Core Web Vitals - Homepage', async ({ page }) => {
    // Start measuring performance
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get Core Web Vitals using the Performance API
    const metrics = await page.evaluate(() => {
      return new Promise<PerformanceMetrics>((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const metrics: Partial<PerformanceMetrics> = {};

          entries.forEach((entry) => {
            if (entry.entryType === 'largest-contentful-paint') {
              metrics.lcp = entry.startTime;
            }
            if (entry.entryType === 'first-input') {
              metrics.fid = (entry as any).processingStart - entry.startTime;
            }
            if (entry.entryType === 'layout-shift' && !(entry as any).hadRecentInput) {
              metrics.cls = (metrics.cls || 0) + (entry as any).value;
            }
          });

          // Get other metrics from Navigation Timing API
          const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
          if (navigation) {
            metrics.ttfb = navigation.responseStart - navigation.fetchStart;
            metrics.tti = navigation.loadEventEnd - navigation.fetchStart;
          }

          // Get FCP from Paint Timing API
          const paintEntries = performance.getEntriesByType('paint');
          const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
          if (fcp) {
            metrics.fcp = fcp.startTime;
          }

          resolve(metrics as PerformanceMetrics);
        });

        observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });

        // Fallback timeout
        setTimeout(() => {
          const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
          const paintEntries = performance.getEntriesByType('paint');
          const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');

          resolve({
            fcp: fcp?.startTime || 0,
            lcp: 0, // Will be captured by observer if available
            fid: 0, // Will be captured by observer if available
            cls: 0, // Will be captured by observer if available
            ttfb: navigation ? navigation.responseStart - navigation.fetchStart : 0,
            tti: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0
          });
        }, 5000);
      });
    });

    // Assert performance budgets (based on Lighthouse CI config)
    expect(metrics.fcp).toBeLessThan(1800); // FCP under 1.8s
    expect(metrics.lcp).toBeLessThan(2500); // LCP under 2.5s
    expect(metrics.fid).toBeLessThan(100); // FID under 100ms
    expect(metrics.cls).toBeLessThan(0.1); // CLS under 0.1
    expect(metrics.ttfb).toBeLessThan(600); // TTFB under 600ms

    console.log('Homepage Performance Metrics:', metrics);
  });

  test('Core Web Vitals - Dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');
      const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');

      return {
        fcp: fcp?.startTime || 0,
        ttfb: navigation ? navigation.responseStart - navigation.fetchStart : 0,
        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.fetchStart : 0,
        loadComplete: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0
      };
    });

    // Dashboard-specific performance budgets
    expect(metrics.fcp).toBeLessThan(2000); // Slightly more lenient for dashboard
    expect(metrics.ttfb).toBeLessThan(800);
    expect(metrics.domContentLoaded).toBeLessThan(3000);
    expect(metrics.loadComplete).toBeLessThan(5000);

    console.log('Dashboard Performance Metrics:', metrics);
  });

  test('Bundle Size Analysis', async ({ page }) => {
    // Measure network resources
    const responses: Array<{ url: string; size: number; type: string }> = [];
    
    page.on('response', async (response) => {
      const url = response.url();
      const headers = response.headers();
      const contentLength = headers['content-length'];
      
      // Track JS, CSS, and other resources
      if (url.includes('.js') || url.includes('.css') || url.includes('.woff') || url.includes('.png')) {
        responses.push({
          url,
          size: contentLength ? parseInt(contentLength) : 0,
          type: url.includes('.js') ? 'script' : 
                url.includes('.css') ? 'stylesheet' : 
                url.includes('.woff') ? 'font' : 'other'
        });
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Analyze bundle sizes
    const scriptSize = responses.filter(r => r.type === 'script').reduce((sum, r) => sum + r.size, 0);
    const styleSize = responses.filter(r => r.type === 'stylesheet').reduce((sum, r) => sum + r.size, 0);
    const fontSize = responses.filter(r => r.type === 'font').reduce((sum, r) => sum + r.size, 0);
    const otherSize = responses.filter(r => r.type === 'other').reduce((sum, r) => sum + r.size, 0);

    // Assert bundle size budgets (from Lighthouse CI config)
    expect(scriptSize).toBeLessThan(500000); // 500KB for scripts
    expect(styleSize).toBeLessThan(100000); // 100KB for stylesheets
    expect(fontSize).toBeLessThan(100000); // 100KB for fonts
    expect(responses.filter(r => r.type === 'script').length).toBeLessThan(20); // Max 20 script files

    console.log('Bundle Analysis:', {
      scriptSize: `${(scriptSize / 1024).toFixed(2)}KB`,
      styleSize: `${(styleSize / 1024).toFixed(2)}KB`,
      fontSize: `${(fontSize / 1024).toFixed(2)}KB`,
      otherSize: `${(otherSize / 1024).toFixed(2)}KB`,
      scriptCount: responses.filter(r => r.type === 'script').length
    });
  });

  test('Memory Usage Monitoring', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Measure memory usage
    const memoryInfo = await page.evaluate(() => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        return {
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit
        };
      }
      return null;
    });

    if (memoryInfo) {
      // Assert memory usage is reasonable (under 50MB for basic page)
      expect(memoryInfo.usedJSHeapSize).toBeLessThan(50 * 1024 * 1024);
      
      // Memory usage should be less than 80% of total available
      const memoryUsageRatio = memoryInfo.usedJSHeapSize / memoryInfo.totalJSHeapSize;
      expect(memoryUsageRatio).toBeLessThan(0.8);

      console.log('Memory Usage:', {
        used: `${(memoryInfo.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB`,
        total: `${(memoryInfo.totalJSHeapSize / 1024 / 1024).toFixed(2)}MB`,
        limit: `${(memoryInfo.jsHeapSizeLimit / 1024 / 1024).toFixed(2)}MB`,
        usageRatio: `${(memoryUsageRatio * 100).toFixed(1)}%`
      });
    }
  });

  test('Interactive Performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Test button click responsiveness
    const button = page.locator('button').first();
    if (await button.isVisible()) {
      const startTime = Date.now();
      await button.click();
      const endTime = Date.now();
      const responseTime = endTime - startTime;

      // Button should respond within 100ms
      expect(responseTime).toBeLessThan(100);
      
      console.log('Button Response Time:', `${responseTime}ms`);
    }

    // Test scroll performance
    const scrollStartTime = Date.now();
    await page.evaluate(() => {
      window.scrollTo(0, 1000);
    });
    await page.waitForTimeout(100); // Let scroll animation finish
    const scrollEndTime = Date.now();
    const scrollResponseTime = scrollEndTime - scrollStartTime;

    // Scroll should be smooth (under 200ms for animation)
    expect(scrollResponseTime).toBeLessThan(200);
    
    console.log('Scroll Performance:', `${scrollResponseTime}ms`);
  });

  test('Network Performance', async ({ page }) => {
    const requestTimes: Array<{ url: string; duration: number }> = [];
    
    page.on('response', async (response) => {
      const request = response.request();
      const timing = response.request().timing();
      if (timing) {
        const duration = timing.responseEnd - timing.requestStart;
        requestTimes.push({
          url: response.url(),
          duration
        });
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Analyze request performance
    const averageRequestTime = requestTimes.reduce((sum, req) => sum + req.duration, 0) / requestTimes.length;
    const slowRequests = requestTimes.filter(req => req.duration > 1000);

    // Network performance assertions
    expect(averageRequestTime).toBeLessThan(500); // Average request under 500ms
    expect(slowRequests.length).toBeLessThan(3); // Max 3 slow requests

    console.log('Network Performance:', {
      totalRequests: requestTimes.length,
      averageTime: `${averageRequestTime.toFixed(2)}ms`,
      slowRequests: slowRequests.length,
      slowestRequest: requestTimes.reduce((max, req) => req.duration > max.duration ? req : max, { url: '', duration: 0 })
    });
  });

  test('Mobile Performance', async ({ page }) => {
    // Simulate mobile device with slower CPU
    await page.emulate({
      viewport: { width: 375, height: 667 },
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    });

    // Throttle CPU to simulate slower mobile device
    const client = await page.context().newCDPSession(page);
    await client.send('Emulation.setCPUThrottlingRate', { rate: 6 });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const mobileMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');
      const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');

      return {
        fcp: fcp?.startTime || 0,
        ttfb: navigation ? navigation.responseStart - navigation.fetchStart : 0,
        loadComplete: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0
      };
    });

    // Mobile performance budgets (more lenient)
    expect(mobileMetrics.fcp).toBeLessThan(2200); // Mobile FCP under 2.2s
    expect(mobileMetrics.ttfb).toBeLessThan(800); // TTFB under 800ms
    expect(mobileMetrics.loadComplete).toBeLessThan(6000); // Load complete under 6s

    console.log('Mobile Performance Metrics:', mobileMetrics);
  });
}); 