import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
	plugins: [
		sveltekit(),
		VitePWA({
			registerType: 'autoUpdate',
			includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
			manifest: {
				name: 'InsightHub',
				short_name: 'InsightHub',
				description: 'AI-powered content discovery from Reddit, YouTube, and more',
				theme_color: '#3b82f6',
				background_color: '#ffffff',
				display: 'standalone',
				orientation: 'portrait',
				scope: '/',
				start_url: '/',
				icons: [
					{
						src: 'pwa-192x192.png',
						sizes: '192x192',
						type: 'image/png'
					},
					{
						src: 'pwa-512x512.png',
						sizes: '512x512',
						type: 'image/png'
					}
				]
			},
			workbox: {
				cleanupOutdatedCaches: true,
				skipWaiting: true,
				clientsClaim: true,
				runtimeCaching: [
					{
						urlPattern: /^https:\/\/bzbpdysqouhbsorffats\.supabase\.co\/rest\/v1\//,
						handler: 'NetworkFirst',
						options: {
							cacheName: 'supabase-api',
							expiration: {
								maxEntries: 50,
								maxAgeSeconds: 60 * 5 // 5 minutes
							},
							networkTimeoutSeconds: 5
						}
					},
					{
						urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
						handler: 'CacheFirst',
						options: {
							cacheName: 'images',
							expiration: {
								maxEntries: 100,
								maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
							}
						}
					}
				]
			}
		})
	],
	
	// Build optimizations
	build: {
		target: 'esnext',
		minify: 'terser',
		cssMinify: true,
		terserOptions: {
			compress: {
				drop_console: true,
				drop_debugger: true,
				pure_funcs: ['console.log', 'console.info', 'console.debug']
			},
			mangle: true
		},
		rollupOptions: {
			output: {
				// Better chunk naming for caching
				chunkFileNames: 'chunks/[name].[hash].js',
				entryFileNames: 'entries/[name].[hash].js',
				assetFileNames: 'assets/[name].[hash].[ext]',
				// Optimize chunk sizing
				manualChunks(id) {
					// Create separate chunks for large dependencies
					if (id.includes('node_modules')) {
						if (id.includes('@supabase')) {
							return 'vendor-supabase'
						}
						if (id.includes('svelte')) {
							return 'vendor-svelte'
						}
						return 'vendor'
					}
				}
			}
		}
	},
	
	// Development optimizations
	server: {
		port: 5174,
		host: true,
		fs: {
			strict: false
		}
	},
	
	// Dependency optimization
	optimizeDeps: {
		include: [
			'@supabase/supabase-js'
		],
		exclude: ['@sveltejs/kit', '@sveltejs/vite-plugin-svelte']
	},
	
	// CSS optimization
	css: {
		devSourcemap: true
	},
	
	// Enable tree-shaking for ES modules
	esbuild: {
		treeShaking: true,
		drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : []
	}
});
