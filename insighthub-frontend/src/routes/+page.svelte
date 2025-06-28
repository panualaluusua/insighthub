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
</script>

<svelte:head>
  <title>InsightHub - Discover Content That Matters</title>
  <meta name="description" content="Discover personalized content from Reddit, YouTube, and more sources curated by AI.">
  
  <!-- Preload critical resources -->
  <link rel="preload" href="/api/content" as="fetch" crossorigin>
  <link rel="dns-prefetch" href="https://bzbpdysqouhbsorffats.supabase.co">
</svelte:head>

{#if $user}
  <!-- Authenticated Content Feed -->
  <div class="min-h-screen bg-gray-50">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-4 py-4">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-center gap-4">
            <h1 class="text-2xl font-bold text-gray-900">Your Content Feed</h1>
            <button
              on:click={handleRefresh}
              class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              disabled={$contentLoading}
            >
              <svg class="w-4 h-4 {$contentLoading ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
          
          <!-- View Toggle (Lazy Loaded) -->
          {#if ViewToggle}
            <ViewToggle compact={compactView} on:viewChange={handleViewChange} />
          {/if}
        </div>
        
        <!-- Filters Section (Lazy Loaded) -->
        {#if ContentFilters}
          <div class="mt-4">
            <ContentFilters
              on:search={handleSearch}
              on:filter={handleFilter}
              on:sort={handleSort}
              on:clear={handleClearFilters}
            />
          </div>
        {/if}
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="max-w-6xl mx-auto px-4 py-6">
      {#if $contentError}
        <!-- Error State -->
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div class="text-red-600 mb-2">
            <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-red-900 mb-2">Error Loading Content</h3>
          <p class="text-red-700 mb-4">{$contentError}</p>
          <button
            on:click={handleRefresh}
            class="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
          </button>
        </div>
        
      {:else if showEmptyState}
        <!-- Empty State -->
        <div class="text-center py-12">
          <div class="text-gray-400 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">No Content Yet</h3>
          <p class="text-gray-600 mb-4 max-w-md mx-auto">
            We're still collecting personalized content for you. Check back soon or try adjusting your filters.
          </p>
          <button
            on:click={handleRefresh}
            class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Now
          </button>
        </div>
        
      {:else if hasContent && VirtualContentList}
        <!-- Virtual Content List for Performance -->
        <div class="bg-white rounded-lg shadow-sm border">
          <VirtualContentList
            items={$contentItems}
            {itemHeight}
            {compactView}
            containerHeight={contentHeight}
            on:loadMore={handleLoadMore}
            on:itemClick={handleItemClick}
          />
        </div>
        
        <!-- Loading indicator for more content -->
        {#if $contentLoading && hasContent}
          <div class="text-center py-6">
            <div class="inline-flex items-center gap-2 text-gray-600">
              <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Loading more content...</span>
            </div>
          </div>
        {/if}
        
      {:else if $contentLoading}
        <!-- Initial Loading State with Skeletons -->
        <div class="space-y-4">
          {#each Array(5) as _, i}
            <div class="bg-white rounded-lg border p-4 animate-pulse">
              <div class="flex gap-4">
                <div class="flex-shrink-0 w-12 h-12 bg-gray-200 rounded"></div>
                <div class="flex-1 space-y-2">
                  <div class="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div class="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div class="h-16 bg-gray-200 rounded w-full"></div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
  
{:else}
  <!-- Landing Page for Non-Authenticated Users -->
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <div class="max-w-4xl mx-auto px-4 py-16 text-center">
      <h1 class="text-5xl font-bold text-gray-900 mb-6 leading-tight">
        Discover Content That <span class="text-blue-600">Matters</span>
      </h1>
      <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        AI-powered content discovery from Reddit, YouTube, and more. 
        Get personalized feeds that match your interests perfectly.
      </p>
      
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <a 
          href="/signup" 
          class="inline-flex items-center justify-center px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
        >
          Get Started
        </a>
        <a 
          href="/signin" 
          class="inline-flex items-center justify-center px-8 py-3 bg-white text-blue-600 text-lg font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
        >
          Sign In
        </a>
      </div>
      
      <!-- Feature Cards with Lazy Loading -->
      {#if LazyLoad}
        <LazyLoad>
          <div class="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div class="text-blue-600 mb-4">
                <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">AI-Powered Ranking</h3>
              <p class="text-gray-600">Smart algorithms curate content based on your interests and engagement patterns.</p>
            </div>
            
            <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div class="text-purple-600 mb-4">
                <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">Multi-Source</h3>
              <p class="text-gray-600">Aggregate content from Reddit, YouTube, and other platforms in one unified feed.</p>
            </div>
            
            <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div class="text-green-600 mb-4">
                <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">Daily Updates</h3>
              <p class="text-gray-600">Fresh content delivered daily with efficient batch processing for optimal performance.</p>
            </div>
          </div>
        </LazyLoad>
      {/if}
    </div>
  </div>
{/if}
