import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		setupFiles: ['src/lib/test-utils/setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'json', 'html', 'lcov'],
			exclude: [
				'node_modules/',
				'src/lib/test-utils/',
				'**/*.d.ts',
				'**/*.config.*',
				'**/coverage/**',
				'**/.svelte-kit/**'
			],
			thresholds: {
				global: {
					branches: 80,
					functions: 80,
					lines: 80,
					statements: 80
				}
			}
		},
		globals: true,
		css: true,
		// Ensure proper DOM environment for Svelte components
		server: {
			deps: {
				inline: ['@testing-library/svelte']
			}
		}
	}
}); 