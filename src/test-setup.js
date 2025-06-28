import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock IntersectionObserver for components that use it (like VirtualList and ContentFeed)
global.IntersectionObserver = vi.fn(() => ({
	observe: vi.fn(),
	disconnect: vi.fn(),
	unobserve: vi.fn(),
}));

// Mock ResizeObserver for responsive components
global.ResizeObserver = vi.fn(() => ({
	observe: vi.fn(),
	disconnect: vi.fn(),
	unobserve: vi.fn(),
}));

// Mock matchMedia for responsive design tests
Object.defineProperty(window, 'matchMedia', {
	writable: true,
	value: vi.fn().mockImplementation(query => ({
		matches: false,
		media: query,
		onchange: null,
		addListener: vi.fn(), // deprecated
		removeListener: vi.fn(), // deprecated
		addEventListener: vi.fn(),
		removeEventListener: vi.fn(),
		dispatchEvent: vi.fn(),
	})),
});

// Mock scrollTo for components with scroll behavior
global.scrollTo = vi.fn();

// Mock fetch for API calls in tests
global.fetch = vi.fn();

// Setup DOM environment
beforeEach(() => {
	// Clear all mocks before each test
	vi.clearAllMocks();
	
	// Reset DOM
	document.body.innerHTML = '';
	
	// Reset fetch mock
	fetch.mockClear();
}); 