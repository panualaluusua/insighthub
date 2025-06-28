import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Navigation Components', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
	});

	test('should display main navigation correctly', async ({ page }) => {
		// Check logo
		await expect(page.locator('text=InsightHub')).toBeVisible();
		
		// Check navigation links
		await expect(page.locator('text=Home')).toBeVisible();
		await expect(page.locator('text=Feed')).toBeVisible();
		await expect(page.locator('text=Discover')).toBeVisible();
		
		// Check auth buttons
		await expect(page.locator('text=Sign In')).toBeVisible();
		await expect(page.locator('text=Sign Up')).toBeVisible();
	});

	test('should handle mobile navigation', async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 667 });
		
		// Mobile menu button should be visible
		const menuButton = page.locator('[aria-label="Toggle mobile menu"]');
		await expect(menuButton).toBeVisible();
		
		// Navigation links should be hidden initially
		await expect(page.locator('nav ul')).not.toBeVisible();
		
		// Click menu button to open mobile menu
		await menuButton.click();
		await expect(page.locator('nav ul')).toBeVisible();
		
		// Click again to close
		await menuButton.click();
		await expect(page.locator('nav ul')).not.toBeVisible();
	});

	test('should highlight active navigation item', async ({ page }) => {
		// Home should be active by default
		const homeLink = page.locator('a[href="/"]');
		await expect(homeLink).toHaveClass(/active/);
		
		// Navigate to feed
		await page.click('text=Feed');
		await expect(page).toHaveURL('/feed');
		
		const feedLink = page.locator('a[href="/feed"]');
		await expect(feedLink).toHaveClass(/active/);
	});

	test('should display sidebar correctly', async ({ page }) => {
		// Check main sections
		await expect(page.locator('text=Main')).toBeVisible();
		await expect(page.locator('text=Personal')).toBeVisible();
		await expect(page.locator('text=Discover')).toBeVisible();
		
		// Check quick actions
		await expect(page.locator('text=Search')).toBeVisible();
		await expect(page.locator('text=Create Post')).toBeVisible();
		await expect(page.locator('text=Notifications')).toBeVisible();
	});

	test('should handle sidebar collapse/expand', async ({ page }) => {
		const collapseButton = page.locator('[aria-label="Toggle sidebar"]');
		
		if (await collapseButton.isVisible()) {
			// Test collapse
			await collapseButton.click();
			await expect(page.locator('aside')).toHaveClass(/collapsed/);
			
			// Test expand
			await collapseButton.click();
			await expect(page.locator('aside')).not.toHaveClass(/collapsed/);
		}
	});

	test('should display footer correctly', async ({ page }) => {
		// Scroll to footer
		await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
		
		// Check company info
		await expect(page.locator('text=InsightHub')).toBeVisible();
		await expect(page.locator('text=Discover, curate, and share')).toBeVisible();
		
		// Check footer sections
		await expect(page.locator('text=Product')).toBeVisible();
		await expect(page.locator('text=Company')).toBeVisible();
		await expect(page.locator('text=Resources')).toBeVisible();
		await expect(page.locator('text=Legal')).toBeVisible();
		
		// Check social links
		await expect(page.locator('a[href*="twitter.com"]')).toBeVisible();
		await expect(page.locator('a[href*="github.com"]')).toBeVisible();
		await expect(page.locator('a[href*="linkedin.com"]')).toBeVisible();
		
		// Check newsletter signup
		await expect(page.locator('input[type="email"]')).toBeVisible();
		await expect(page.locator('button[type="submit"]')).toBeVisible();
	});

	test('should handle newsletter signup', async ({ page }) => {
		await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
		
		const emailInput = page.locator('input[type="email"]');
		const submitButton = page.locator('button[type="submit"]');
		
		// Test empty email
		await submitButton.click();
		await expect(page.locator('text=Please enter a valid email')).toBeVisible();
		
		// Test valid email
		await emailInput.fill('test@example.com');
		await submitButton.click();
		await expect(page.locator('text=Thank you for subscribing!')).toBeVisible();
	});

	test('should be accessible', async ({ page }) => {
		const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('should handle keyboard navigation', async ({ page }) => {
		// Tab through navigation elements
		await page.keyboard.press('Tab'); // Skip to main content link
		await page.keyboard.press('Tab'); // Logo
		await page.keyboard.press('Tab'); // Home link
		await expect(page.locator('a[href="/"]')).toBeFocused();
		
		await page.keyboard.press('Tab'); // Feed link
		await expect(page.locator('a[href="/feed"]')).toBeFocused();
		
		await page.keyboard.press('Tab'); // Discover link
		await expect(page.locator('a[href="/discover"]')).toBeFocused();
		
		// Should be able to navigate with Enter
		await page.keyboard.press('Enter');
		await expect(page).toHaveURL('/discover');
	});

	test('should handle responsive design breakpoints', async ({ page }) => {
		// Test desktop layout
		await page.setViewportSize({ width: 1200, height: 800 });
		await expect(page.locator('nav ul')).toBeVisible();
		
		// Test tablet layout
		await page.setViewportSize({ width: 768, height: 1024 });
		await expect(page.locator('nav ul')).toBeVisible();
		
		// Test mobile layout
		await page.setViewportSize({ width: 375, height: 667 });
		await expect(page.locator('[aria-label="Toggle mobile menu"]')).toBeVisible();
	});

	test('should handle scroll behavior', async ({ page }) => {
		// Test sticky navigation
		await page.evaluate(() => window.scrollTo(0, 500));
		
		const nav = page.locator('nav');
		await expect(nav).toHaveClass(/sticky/);
		
		// Test scroll to top
		const logoLink = page.locator('a[href="/"]');
		await logoLink.click();
		
		const scrollPosition = await page.evaluate(() => window.pageYOffset);
		expect(scrollPosition).toBe(0);
	});

	test('should handle external links correctly', async ({ page }) => {
		await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
		
		// Check external links have proper attributes
		const twitterLink = page.locator('a[href*="twitter.com"]');
		await expect(twitterLink).toHaveAttribute('target', '_blank');
		await expect(twitterLink).toHaveAttribute('rel', 'noopener noreferrer');
		
		const githubLink = page.locator('a[href*="github.com"]');
		await expect(githubLink).toHaveAttribute('target', '_blank');
		await expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
	});
}); 