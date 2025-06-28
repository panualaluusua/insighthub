import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
	test('home page should be accessible', async ({ page }) => {
		await page.goto('/');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('sign in page should be accessible', async ({ page }) => {
		await page.goto('/signin');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('sign up page should be accessible', async ({ page }) => {
		await page.goto('/signup');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('feed page should be accessible', async ({ page }) => {
		await page.goto('/feed');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('dashboard page should be accessible', async ({ page }) => {
		await page.goto('/dashboard');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
	});

	test('should support keyboard navigation', async ({ page }) => {
		await page.goto('/');
		
		// Test tab order
		await page.keyboard.press('Tab');
		await expect(page.locator(':focus')).toBeVisible();
		
		// Test navigation with keyboard
		await page.keyboard.press('Tab');
		await page.keyboard.press('Tab');
		await page.keyboard.press('Enter');
		
		// Should navigate somewhere
		await expect(page).toHaveURL(/\/(signin|signup|feed|discover)/);
	});

	test('should have proper heading hierarchy', async ({ page }) => {
		await page.goto('/');
		
		// Check for h1
		const h1Elements = await page.locator('h1').count();
		expect(h1Elements).toBeGreaterThanOrEqual(1);
		
		// Check heading order (h1 -> h2 -> h3, etc.)
		const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
		let previousLevel = 0;
		
		for (const heading of headings) {
			const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
			const currentLevel = parseInt(tagName.charAt(1));
			
			// Heading levels should not skip (e.g., h1 -> h3 is not allowed)
			if (previousLevel > 0) {
				expect(currentLevel).toBeLessThanOrEqual(previousLevel + 1);
			}
			
			previousLevel = currentLevel;
		}
	});

	test('should have proper alt text for images', async ({ page }) => {
		await page.goto('/');
		
		const images = await page.locator('img').all();
		
		for (const img of images) {
			const alt = await img.getAttribute('alt');
			const role = await img.getAttribute('role');
			
			// Images should have alt text or be decorative
			if (role !== 'presentation' && role !== 'none') {
				expect(alt).toBeTruthy();
				expect(alt).not.toBe('');
			}
		}
	});

	test('should have proper form labels', async ({ page }) => {
		await page.goto('/signin');
		
		const inputs = await page.locator('input[type="email"], input[type="password"], input[type="text"]').all();
		
		for (const input of inputs) {
			const id = await input.getAttribute('id');
			const ariaLabel = await input.getAttribute('aria-label');
			const ariaLabelledBy = await input.getAttribute('aria-labelledby');
			
			// Input should have a label, aria-label, or aria-labelledby
			if (id) {
				const label = page.locator(`label[for="${id}"]`);
				const hasLabel = await label.count() > 0;
				expect(hasLabel || ariaLabel || ariaLabelledBy).toBeTruthy();
			} else {
				expect(ariaLabel || ariaLabelledBy).toBeTruthy();
			}
		}
	});

	test('should have sufficient color contrast', async ({ page }) => {
		await page.goto('/');
		
		const accessibilityScanResults = await new AxeBuilder({ page })
			.withTags(['wcag2aa'])
			.include('.text-gray-600, .text-gray-500, .text-blue-600')
			.analyze();
		
		// Check for color contrast violations
		const contrastViolations = accessibilityScanResults.violations.filter(
			violation => violation.id === 'color-contrast'
		);
		
		expect(contrastViolations).toEqual([]);
	});

	test('should handle focus management', async ({ page }) => {
		await page.goto('/');
		
		// Test that focus is visible
		await page.keyboard.press('Tab');
		const focusedElement = page.locator(':focus');
		await expect(focusedElement).toBeVisible();
		
		// Check that focus outline is visible
		const outline = await focusedElement.evaluate(el => {
			const styles = window.getComputedStyle(el);
			return styles.outline || styles.boxShadow;
		});
		
		expect(outline).not.toBe('none');
		expect(outline).not.toBe('');
	});

	test('should support screen reader announcements', async ({ page }) => {
		await page.goto('/signin');
		
		// Check for live regions
		const liveRegions = await page.locator('[aria-live]').count();
		
		// Fill form with invalid data to trigger error messages
		await page.fill('input[name="email"]', 'invalid-email');
		await page.fill('input[name="password"]', '123');
		await page.click('button[type="submit"]');
		
		// Error messages should be announced
		const errorMessages = await page.locator('[role="alert"], [aria-live="polite"], [aria-live="assertive"]').count();
		expect(errorMessages).toBeGreaterThan(0);
	});

	test('should work with high contrast mode', async ({ page, browser }) => {
		// Simulate high contrast mode
		const context = await browser.newContext({
			colorScheme: 'dark',
			forcedColors: 'active'
		});
		
		const newPage = await context.newPage();
		await newPage.goto('/');
		
		const accessibilityScanResults = await new AxeBuilder({ page: newPage })
			.withTags(['wcag2aa'])
			.analyze();
		
		expect(accessibilityScanResults.violations).toEqual([]);
		
		await context.close();
	});

	test('should work with reduced motion', async ({ page, browser }) => {
		// Simulate reduced motion preference
		const context = await browser.newContext({
			reducedMotion: 'reduce'
		});
		
		const newPage = await context.newPage();
		await newPage.goto('/');
		
		// Check that animations are disabled or reduced
		const animatedElements = await newPage.locator('[class*="animate"], [class*="transition"]').all();
		
		for (const element of animatedElements) {
			const animationDuration = await element.evaluate(el => {
				const styles = window.getComputedStyle(el);
				return styles.animationDuration;
			});
			
			// Animation should be disabled or very short
			expect(animationDuration === '0s' || animationDuration === '0.01s').toBeTruthy();
		}
		
		await context.close();
	});
}); 