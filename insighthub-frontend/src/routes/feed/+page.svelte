<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { ContentFeed, ContentFilters } from '$lib';
  import { feedStore, feedFilterStore, feedActions, feedFilterActions, filteredFeedContent } from '$lib/stores/feedStore';
  import type { ContentItem } from '$lib/types';

  let user: any = null;
  let feedContainer: HTMLElement;

  // Subscribe to stores
  $: feed = $feedStore;
  $: filters = $feedFilterStore;
  $: filteredItems = $filteredFeedContent;

  onMount(async () => {
    // Check authentication
    const { data: { user: currentUser } } = await supabase.auth.getUser();
    
    if (!currentUser) {
      goto('/signin');
      return;
    }
    
    user = currentUser;

    // Load initial content and filter options
    await feedActions.loadFilterOptions(true); // Use mock data for demo
    await feedActions.loadContent(20, true); // Use mock data for demo
  });

  // Handle feed interactions
  function handleLoadMore() {
    feedActions.loadMoreContent(20, true); // Use mock data for demo
  }

  function handleItemClick(event: CustomEvent<{ item: ContentItem }>) {
    const { item } = event.detail;
    console.log('Item clicked:', item);
    // Navigate to item detail or open URL
    window.open(item.url, '_blank');
  }

  function handleItemLike(event: CustomEvent<{ item: ContentItem }>) {
    const { item } = event.detail;
    feedActions.updateItemInteraction(item.id, 'like', !item.user_liked);
  }

  function handleItemSave(event: CustomEvent<{ item: ContentItem }>) {
    const { item } = event.detail;
    feedActions.updateItemInteraction(item.id, 'save', !item.user_saved);
  }

  function handleItemShare(event: CustomEvent<{ item: ContentItem }>) {
    const { item } = event.detail;
    feedActions.updateItemInteraction(item.id, 'share', !item.user_shared);
    
    // Share functionality
    if (navigator.share) {
      navigator.share({
        title: item.title,
        text: item.summary,
        url: item.url
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(item.url);
    }
  }

  // Filter handlers
  function handleSourcesChange(event: CustomEvent<{ sources: string[] }>) {
    feedFilterActions.updateSources(event.detail.sources);
  }

  function handleTagsChange(event: CustomEvent<{ tags: string[] }>) {
    feedFilterActions.updateTags(event.detail.tags);
  }

  function handleSortChange(event: CustomEvent<{ sort: string }>) {
    feedFilterActions.updateSort(event.detail.sort as any);
  }

  function handleClearFilters() {
    feedFilterActions.clearFilters();
  }

  function handleRefresh() {
    feedActions.refreshContent(true);
  }
</script>

<svelte:head>
  <title>Content Feed - InsightHub</title>
  <meta name="description" content="Discover and explore curated content from across the web" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Header -->
  <div class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Content Feed</h1>
          {#if feed.total > 0}
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              {filteredItems.length} of {feed.total} items
            </span>
          {/if}
        </div>
        
        <div class="flex items-center space-x-4">
          <button
            on:click={handleRefresh}
            disabled={feed.loading}
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
          >
            <svg class="w-4 h-4 mr-2 {feed.loading ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          
          <a
            href="/dashboard"
            class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Dashboard
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Main content -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <!-- Sidebar with filters -->
      <div class="lg:col-span-1">
        <div class="sticky top-8">
          <ContentFilters
            sources={filters.sources}
            selectedSources={filters.selectedSources}
            tags={filters.tags}
            selectedTags={filters.selectedTags}
            sortBy={filters.sortBy}
            onSourcesChange={(sources) => feedFilterActions.updateSources(sources)}
            onTagsChange={(tags) => feedFilterActions.updateTags(tags)}
            onSortChange={(sort) => feedFilterActions.updateSort(sort as any)}
            onClearFilters={handleClearFilters}
            on:sourcesChange={handleSourcesChange}
            on:tagsChange={handleTagsChange}
            on:sortChange={handleSortChange}
            on:clearFilters={handleClearFilters}
          />

          <!-- Stats -->
          <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Feed Stats</h3>
            <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div class="flex justify-between">
                <span>Total Items:</span>
                <span class="font-medium">{feed.total}</span>
              </div>
              <div class="flex justify-between">
                <span>Filtered:</span>
                <span class="font-medium">{filteredItems.length}</span>
              </div>
              <div class="flex justify-between">
                <span>Sources:</span>
                <span class="font-medium">{filters.sources.length}</span>
              </div>
              <div class="flex justify-between">
                <span>Tags:</span>
                <span class="font-medium">{filters.tags.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Feed content -->
      <div class="lg:col-span-3" bind:this={feedContainer}>
        {#if feed.error}
          <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div class="flex">
              <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Error loading content</h3>
                <p class="mt-1 text-sm text-red-700">{feed.error}</p>
              </div>
            </div>
          </div>
        {/if}

        <ContentFeed
          items={filteredItems}
          loading={feed.loading}
          hasMore={feed.hasMore}
          compact={false}
          onLoadMore={handleLoadMore}
          onItemClick={(item) => handleItemClick(new CustomEvent('click', { detail: { item } }))}
          onItemLike={(item) => handleItemLike(new CustomEvent('like', { detail: { item } }))}
          onItemSave={(item) => handleItemSave(new CustomEvent('save', { detail: { item } }))}
          onItemShare={(item) => handleItemShare(new CustomEvent('share', { detail: { item } }))}
          on:loadMore={handleLoadMore}
          on:itemClick={handleItemClick}
          on:itemLike={handleItemLike}
          on:itemSave={handleItemSave}
          on:itemShare={handleItemShare}
        />
      </div>
    </div>
  </div>
</div>

<style>
  /* Custom scrollbar for the main content area */
  :global(.content-feed) {
    scrollbar-width: thin;
    scrollbar-color: theme('colors.gray.300') theme('colors.gray.100');
  }

  :global(.content-feed::-webkit-scrollbar) {
    width: 8px;
  }

  :global(.content-feed::-webkit-scrollbar-track) {
    @apply bg-gray-100 dark:bg-gray-700;
  }

  :global(.content-feed::-webkit-scrollbar-thumb) {
    @apply bg-gray-300 dark:bg-gray-500 rounded;
  }

  :global(.content-feed::-webkit-scrollbar-thumb:hover) {
    @apply bg-gray-400 dark:bg-gray-400;
  }
</style> 