import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Authentication Flow', () => {
	test.beforeEach(async ({ page }) => {
		// Start from the home page
		await page.goto('/');
	});

	test('should navigate to sign in page', async ({ page }) => {
		await page.click('text=Sign In');
		await expect(page).toHaveURL('/signin');
		await expect(page.locator('h1')).toContainText('Sign In');
	});

	test('should navigate to sign up page', async ({ page }) => {
		await page.click('text=Sign Up');
		await expect(page).toHaveURL('/signup');
		await expect(page.locator('h1')).toContainText('Create Account');
	});

	test('should display sign in form correctly', async ({ page }) => {
		await page.goto('/signin');
		
		// Check form elements
		await expect(page.locator('input[name="email"]')).toBeVisible();
		await expect(page.locator('input[name="password"]')).toBeVisible();
		await expect(page.locator('button[type="submit"]')).toBeVisible();
		
		// Check social login buttons
		await expect(page.locator('text=Continue with Google')).toBeVisible();
		await expect(page.locator('text=Continue with GitHub')).toBeVisible();
		
		// Check forgot password link
		await expect(page.locator('text=Forgot your password?')).toBeVisible();
	});

	test('should display sign up form correctly', async ({ page }) => {
		await page.goto('/signup');
		
		// Check form elements
		await expect(page.locator('input[name="email"]')).toBeVisible();
		await expect(page.locator('input[name="password"]')).toBeVisible();
		await expect(page.locator('input[name="confirmPassword"]')).toBeVisible();
		await expect(page.locator('input[type="checkbox"]')).toBeVisible();
		await expect(page.locator('button[type="submit"]')).toBeVisible();
		
		// Check social login buttons
		await expect(page.locator('text=Continue with Google')).toBeVisible();
		await expect(page.locator('text=Continue with GitHub')).toBeVisible();
	});

	test('should validate sign in form', async ({ page }) => {
		await page.goto('/signin');
		
		// Try to submit empty form
		await page.click('button[type="submit"]');
		
		// Should show validation errors
		await expect(page.locator('text=Email is required')).toBeVisible();
		await expect(page.locator('text=Password is required')).toBeVisible();
	});

	test('should validate sign up form', async ({ page }) => {
		await page.goto('/signup');
		
		// Try to submit empty form
		await page.click('button[type="submit"]');
		
		// Should show validation errors
		await expect(page.locator('text=Email is required')).toBeVisible();
		await expect(page.locator('text=Password is required')).toBeVisible();
	});

	test('should validate password strength on sign up', async ({ page }) => {
		await page.goto('/signup');
		
		const passwordInput = page.locator('input[name="password"]');
		
		// Test weak password
		await passwordInput.fill('123');
		await expect(page.locator('text=Weak')).toBeVisible();
		
		// Test medium password
		await passwordInput.fill('password123');
		await expect(page.locator('text=Medium')).toBeVisible();
		
		// Test strong password
		await passwordInput.fill('StrongP@ssw0rd!');
		await expect(page.locator('text=Strong')).toBeVisible();
	});

	test('should validate password confirmation', async ({ page }) => {
		await page.goto('/signup');
		
		await page.fill('input[name="password"]', 'password123');
		await page.fill('input[name="confirmPassword"]', 'different');
		await page.click('button[type="submit"]');
		
		await expect(page.locator('text=Passwords do not match')).toBeVisible();
	});

	test('should require terms acceptance on sign up', async ({ page }) => {
		await page.goto('/signup');
		
		await page.fill('input[name="email"]', 'test@example.com');
		await page.fill('input[name="password"]', 'StrongP@ssw0rd!');
		await page.fill('input[name="confirmPassword"]', 'StrongP@ssw0rd!');
		
		// Don't check terms checkbox
		await page.click('button[type="submit"]');
		
		await expect(page.locator('text=You must accept the terms')).toBeVisible();
	});

	test('should handle forgot password flow', async ({ page }) => {
		await page.goto('/signin');
		
		await page.click('text=Forgot your password?');
		
		// Should show forgot password form
		await expect(page.locator('text=Reset Password')).toBeVisible();
		await expect(page.locator('input[name="email"]')).toBeVisible();
		await expect(page.locator('button[type="submit"]')).toBeVisible();
	});

	test('should navigate between auth pages', async ({ page }) => {
		await page.goto('/signin');
		
		// Go to sign up
		await page.click('text=Create one');
		await expect(page).toHaveURL('/signup');
		
		// Go back to sign in
		await page.click('text=Sign in');
		await expect(page).toHaveURL('/signin');
	});

	test('should be accessible', async ({ page }) => {
		await page.goto('/signin');
		
		const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
		expect(accessibilityScanResults.violations).toEqual([]);
		
		await page.goto('/signup');
		
		const signupAccessibilityResults = await new AxeBuilder({ page }).analyze();
		expect(signupAccessibilityResults.violations).toEqual([]);
	});

	test('should work on mobile viewports', async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 667 });
		
		await page.goto('/signin');
		
		// Check mobile layout
		await expect(page.locator('input[name="email"]')).toBeVisible();
		await expect(page.locator('input[name="password"]')).toBeVisible();
		await expect(page.locator('button[type="submit"]')).toBeVisible();
		
		// Check that form is properly sized
		const form = page.locator('form');
		const boundingBox = await form.boundingBox();
		expect(boundingBox?.width).toBeLessThanOrEqual(375);
	});

	test('should handle keyboard navigation', async ({ page }) => {
		await page.goto('/signin');
		
		// Tab through form elements
		await page.keyboard.press('Tab'); // Email input
		await expect(page.locator('input[name="email"]')).toBeFocused();
		
		await page.keyboard.press('Tab'); // Password input
		await expect(page.locator('input[name="password"]')).toBeFocused();
		
		await page.keyboard.press('Tab'); // Submit button
		await expect(page.locator('button[type="submit"]')).toBeFocused();
		
		// Should be able to submit with Enter
		await page.keyboard.press('Enter');
	});
}); 