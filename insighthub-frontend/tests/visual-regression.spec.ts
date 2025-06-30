import { test, expect } from '@playwright/test';

test.describe('Visual Regression Testing', () => {
  
  test('Homepage visual consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('homepage-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Test viewport screenshot for above-the-fold content
    await expect(page).toHaveScreenshot('homepage-viewport.png', {
      animations: 'disabled'
    });
  });

  test('Authentication pages visual consistency', async ({ page }) => {
    // Sign in page
    await page.goto('/signin');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('signin-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Sign up page
    await page.goto('/signup');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('signup-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('Dashboard visual consistency', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Wait for any dynamic content to load
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('dashboard-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('Feed page visual consistency', async ({ page }) => {
    await page.goto('/feed');
    await page.waitForLoadState('networkidle');
    
    // Wait for content to load
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('feed-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('Theme toggle visual consistency', async ({ page }) => {
    await page.goto('/theme');
    await page.waitForLoadState('networkidle');
    
    // Default theme
    await expect(page).toHaveScreenshot('theme-default.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // If there's a theme toggle button, test it
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      await page.waitForTimeout(500); // Wait for theme transition
      
      await expect(page).toHaveScreenshot('theme-toggled.png', {
        fullPage: true,
        animations: 'disabled'
      });
    }
  });

  test('Responsive design visual consistency', async ({ page }) => {
    const viewports = [
      { width: 375, height: 667, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1024, height: 768, name: 'tablet-landscape' },
      { width: 1440, height: 900, name: 'desktop' },
      { width: 1920, height: 1080, name: 'desktop-large' }
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`, {
        animations: 'disabled'
      });
    }
  });

  test('Navigation visual consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test navigation component specifically
    const navigation = page.locator('[data-testid="navigation"]');
    if (await navigation.isVisible()) {
      await expect(navigation).toHaveScreenshot('navigation-component.png', {
        animations: 'disabled'
      });
    }
    
    // Test mobile navigation if it exists
    await page.setViewportSize({ width: 375, height: 667 });
    const mobileNavTrigger = page.locator('[data-testid="mobile-nav-trigger"]');
    if (await mobileNavTrigger.isVisible()) {
      await mobileNavTrigger.click();
      await page.waitForTimeout(300); // Wait for animation
      
      const mobileNav = page.locator('[data-testid="mobile-navigation"]');
      if (await mobileNav.isVisible()) {
        await expect(mobileNav).toHaveScreenshot('mobile-navigation.png', {
          animations: 'disabled'
        });
      }
    }
  });

  test('Form states visual consistency', async ({ page }) => {
    await page.goto('/signin');
    await page.waitForLoadState('networkidle');
    
    // Empty form state
    await expect(page.locator('form')).toHaveScreenshot('form-empty.png', {
      animations: 'disabled'
    });
    
    // Focus states
    const emailInput = page.locator('input[type="email"]');
    if (await emailInput.isVisible()) {
      await emailInput.focus();
      await expect(page.locator('form')).toHaveScreenshot('form-email-focused.png', {
        animations: 'disabled'
      });
      
      // Filled state
      await emailInput.fill('test@example.com');
      await expect(page.locator('form')).toHaveScreenshot('form-email-filled.png', {
        animations: 'disabled'
      });
    }
    
    // Password field focus
    const passwordInput = page.locator('input[type="password"]');
    if (await passwordInput.isVisible()) {
      await passwordInput.focus();
      await expect(page.locator('form')).toHaveScreenshot('form-password-focused.png', {
        animations: 'disabled'
      });
    }
  });

  test('Error states visual consistency', async ({ page }) => {
    await page.goto('/signin');
    await page.waitForLoadState('networkidle');
    
    // Try to trigger validation errors
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(500); // Wait for validation
      
      // Check if error states are visible
      const errorMessages = page.locator('[role="alert"], .error, .invalid');
      if (await errorMessages.first().isVisible()) {
        await expect(page.locator('form')).toHaveScreenshot('form-validation-errors.png', {
          animations: 'disabled'
        });
      }
    }
  });

  test('Loading states visual consistency', async ({ page }) => {
    // Intercept network requests to simulate loading states
    await page.route('**/api/**', route => {
      // Delay the response to capture loading state
      setTimeout(() => route.continue(), 2000);
    });
    
    await page.goto('/dashboard');
    
    // Capture loading state
    await expect(page).toHaveScreenshot('dashboard-loading.png', {
      animations: 'disabled'
    });
    
    // Wait for content to load and capture final state
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('dashboard-loaded.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('Accessibility indicators visual consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test keyboard navigation visibility
    await page.keyboard.press('Tab');
    await expect(page).toHaveScreenshot('keyboard-focus-first-element.png', {
      animations: 'disabled'
    });
    
    await page.keyboard.press('Tab');
    await expect(page).toHaveScreenshot('keyboard-focus-second-element.png', {
      animations: 'disabled'
    });
  });

});

test.describe('Component-Level Visual Testing', () => {
  
  test('Button component variations', async ({ page }) => {
    // This would test an isolated component page if you have one
    // For now, we'll test buttons in context
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const buttons = page.locator('button, [role="button"]');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 5); i++) {
      const button = buttons.nth(i);
      if (await button.isVisible()) {
        await expect(button).toHaveScreenshot(`button-${i}.png`, {
          animations: 'disabled'
        });
        
        // Hover state
        await button.hover();
        await expect(button).toHaveScreenshot(`button-${i}-hover.png`, {
          animations: 'disabled'
        });
      }
    }
  });

  test('Input component variations', async ({ page }) => {
    await page.goto('/signin');
    await page.waitForLoadState('networkidle');
    
    const inputs = page.locator('input');
    const inputCount = await inputs.count();
    
    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      if (await input.isVisible()) {
        // Default state
        await expect(input).toHaveScreenshot(`input-${i}-default.png`, {
          animations: 'disabled'
        });
        
        // Focus state
        await input.focus();
        await expect(input).toHaveScreenshot(`input-${i}-focused.png`, {
          animations: 'disabled'
        });
        
        // With content
        await input.fill('test content');
        await expect(input).toHaveScreenshot(`input-${i}-filled.png`, {
          animations: 'disabled'
        });
        
        await input.clear();
      }
    }
  });
  
}); 