<script lang="ts">
  import { onMount, afterUpdate } from 'svelte'
  import { user } from '../lib/stores/authStore'
  import { 
    contentStore, 
    contentActions, 
    contentItems, 
    contentLoading, 
    contentError, 
    contentHasMore 
  } from '../lib/stores/contentStore'
  import { testSupabaseConnection } from '$lib/test-supabase.js'
  import { PageLayout, Sidebar } from '$lib'
  import type { User } from '@supabase/supabase-js'
  
  // Lazy import components for better performance
  let ContentFilters: any
  let ViewToggle: any
  let VirtualContentList: any
  let LazyLoad: any
  
  // Performance state
  let compactView = false
  let windowHeight = typeof window !== 'undefined' ? window.innerHeight : 600
  let contentHeight = Math.max(400, windowHeight - 200) // Reserve space for header/nav
  
  // Reactive statements for memoization
  $: itemHeight = compactView ? 120 : 200
  $: hasContent = $contentItems.length > 0
  $: showEmptyState = !$contentLoading && !hasContent && !$contentError
  
  // Load components lazily
  onMount(async () => {
    // Dynamic imports for code splitting
    const [
      { default: ContentFiltersComponent },
      { default: ViewToggleComponent },
      { default: VirtualContentListComponent },
      { default: LazyLoadComponent }
    ] = await Promise.all([
      import('../lib/components/ContentFilters.svelte'),
      import('../lib/components/ViewToggle.svelte'),
      import('../lib/components/VirtualContentList.svelte'),
      import('../lib/components/LazyLoad.svelte')
    ])
    
    ContentFilters = ContentFiltersComponent
    ViewToggle = ViewToggleComponent
    VirtualContentList = VirtualContentListComponent
    LazyLoad = LazyLoadComponent
    
    // Load content when components are ready and user is authenticated
    if ($user) {
      contentActions.loadContent(true)
    }
    
    // Window resize handler for responsive virtual scrolling
    function handleResize() {
      if (typeof window !== 'undefined') {
        windowHeight = window.innerHeight
        contentHeight = Math.max(400, windowHeight - 200)
      }
    }
    
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', handleResize)
      return () => window.removeEventListener('resize', handleResize)
    }
  })
  
  // Memoized event handlers to prevent unnecessary re-renders
  const handleSearch = (event: CustomEvent<{ query: string }>) => {
    contentActions.searchContent(event.detail.query)
  }
  
  const handleFilter = (event: CustomEvent<{ source: string | undefined }>) => {
    contentActions.setFilters({ source: event.detail.source })
  }
  
  const handleSort = (event: CustomEvent<{ sortBy: 'created_at' | 'title' | 'ranking_score', sortOrder: 'asc' | 'desc' }>) => {
    contentActions.setFilters({ 
      sortBy: event.detail.sortBy, 
      sortOrder: event.detail.sortOrder 
    })
  }
  
  const handleClearFilters = () => {
    contentActions.clearFilters()
  }
  
  const handleViewChange = (event: CustomEvent<{ compact: boolean }>) => {
    compactView = event.detail.compact
  }
  
  const handleLoadMore = () => {
    contentActions.loadMore()
  }
  
  const handleItemClick = (event: CustomEvent<{ item: any }>) => {
    // Handle content item click - could navigate to detail page
    console.log('Content item clicked:', event.detail.item)
  }
  
  const handleRefresh = () => {
    contentActions.refreshContent()
  }
  
  // Reload content when user signs in (memoized)
  $: if ($user && !hasContent && !$contentLoading && !$contentError) {
    contentActions.loadContent(true)
  }

  // Test function for Supabase connectivity
  async function runSupabaseTest() {
    console.log('🚀 Running Supabase connectivity test...')
    try {
      const result = await testSupabaseConnection()
      if (result) {
        alert('✅ Supabase test passed! Check console for details.')
      } else {
        alert('❌ Supabase test failed! Check console for details.')
      }
    } catch (error) {
      console.error('Test error:', error)
      alert('❌ Test error! Check console for details.')
    }
  }

  // Sample sidebar sections for demonstration
  const sidebarSections = [
    {
      title: 'Getting Started',
      items: [
        { href: '/feed', label: 'Explore Feed', icon: 'feed' },
        { href: '/signup', label: 'Create Account', icon: 'user' },
        { href: '/dashboard', label: 'Dashboard', icon: 'dashboard', requiresAuth: true }
      ]
    },
    {
      title: 'Features',
      items: [
        { href: '/features/ai', label: 'AI Insights', icon: 'trending' },
        { href: '/features/curation', label: 'Content Curation', icon: 'bookmark' },
        { href: '/features/analytics', label: 'Analytics', icon: 'grid' }
      ]
    }
  ]
</script>

<PageLayout 
	title="Welcome to InsightHub" 
	description="Discover, curate, and share the most valuable insights from across the web"
	showSidebar={true}
	sidebarPosition="left"
	maxWidth="7xl"
>
	<svelte:fragment slot="sidebar">
		<Sidebar sections={sidebarSections} showUserInfo={false} />
	</svelte:fragment>

	<svelte:fragment slot="header">
		<div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 mb-8">
			<h1 class="text-4xl font-bold text-gray-900 mb-4">
				Welcome to InsightHub
			</h1>
			<p class="text-xl text-gray-600 mb-6 max-w-3xl">
				Your intelligent content discovery platform. Find, organize, and share the most valuable insights from across the web with AI-powered recommendations.
			</p>
			<div class="flex flex-wrap gap-4">
				<a 
					href="/feed" 
					class="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
				>
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14-7H5m14 14H5" />
					</svg>
					Explore Feed
				</a>
				<a 
					href="/signup" 
					class="inline-flex items-center px-6 py-3 bg-white text-blue-600 font-medium rounded-lg border border-blue-600 hover:bg-blue-50 transition-colors"
				>
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
					</svg>
					Get Started
				</a>
			</div>
		</div>
	</svelte:fragment>

	<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
		<!-- Feature Cards -->
		<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
				<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
				</svg>
			</div>
			<h3 class="text-lg font-semibold text-gray-900 mb-2">AI-Powered Discovery</h3>
			<p class="text-gray-600">
				Our intelligent algorithms learn from your preferences to surface the most relevant content from thousands of sources.
			</p>
		</div>

		<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
				<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
				</svg>
			</div>
			<h3 class="text-lg font-semibold text-gray-900 mb-2">Smart Curation</h3>
			<p class="text-gray-600">
				Save, organize, and categorize content with intelligent tagging and personalized collections.
			</p>
		</div>

		<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
				<svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
				</svg>
			</div>
			<h3 class="text-lg font-semibold text-gray-900 mb-2">Social Sharing</h3>
			<p class="text-gray-600">
				Share insights with your network and discover what others in your field are reading and discussing.
			</p>
		</div>
	</div>

	<!-- How it Works Section -->
	<div class="bg-gray-50 rounded-lg p-8 mb-12">
		<h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">How InsightHub Works</h2>
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
			<div class="text-center">
				<div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
					<span class="text-white font-bold text-lg">1</span>
				</div>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">Connect Sources</h3>
				<p class="text-gray-600">
					Connect your favorite news sources, blogs, and content platforms to create a unified feed.
				</p>
			</div>
			<div class="text-center">
				<div class="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
					<span class="text-white font-bold text-lg">2</span>
				</div>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h3>
				<p class="text-gray-600">
					Our AI analyzes content quality, relevance, and your reading patterns to personalize recommendations.
				</p>
			</div>
			<div class="text-center">
				<div class="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
					<span class="text-white font-bold text-lg">3</span>
				</div>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">Discover & Share</h3>
				<p class="text-gray-600">
					Discover high-quality insights, save them to collections, and share with your professional network.
				</p>
			</div>
		</div>
	</div>

	<!-- Stats Section -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
		<div class="text-center">
			<div class="text-3xl font-bold text-blue-600 mb-2">10K+</div>
			<div class="text-gray-600">Content Sources</div>
		</div>
		<div class="text-center">
			<div class="text-3xl font-bold text-green-600 mb-2">1M+</div>
			<div class="text-gray-600">Articles Analyzed</div>
		</div>
		<div class="text-center">
			<div class="text-3xl font-bold text-purple-600 mb-2">50K+</div>
			<div class="text-gray-600">Active Users</div>
		</div>
		<div class="text-center">
			<div class="text-3xl font-bold text-orange-600 mb-2">95%</div>
			<div class="text-gray-600">Satisfaction Rate</div>
		</div>
	</div>

	<svelte:fragment slot="actions">
		<div class="text-center">
			<h2 class="text-2xl font-bold text-gray-900 mb-4">Ready to get started?</h2>
			<p class="text-gray-600 mb-6">
				Join thousands of professionals who rely on InsightHub for their daily content discovery.
			</p>
			<div class="flex flex-wrap justify-center gap-4">
				<a 
					href="/signup" 
					class="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
				>
					Start Free Trial
				</a>
				<a 
					href="/demo" 
					class="inline-flex items-center px-8 py-3 bg-white text-gray-700 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
				>
					Watch Demo
				</a>
			</div>
		</div>
	</svelte:fragment>
</PageLayout>

<style>
	/* Custom styles for the home page */
	:global(.hero-gradient) {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}

	/* Smooth animations */
	.grid > div {
		transition: transform 0.2s ease-in-out;
	}

	.grid > div:hover {
		transform: translateY(-2px);
	}

	/* Focus styles for accessibility */
	a:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}
</style>
