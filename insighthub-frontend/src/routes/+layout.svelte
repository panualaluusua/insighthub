<script lang="ts">
  import '../app.css'
  import { onMount } from 'svelte'
  import { authActions, authLoading, authError } from '$lib/stores/authStore'

  // Initialize auth store when app starts
  onMount(() => {
    const cleanup = authActions.init()
    
    // Cleanup auth listener when component is destroyed
    return () => {
      if (cleanup) cleanup()
    }
  })
</script>

<!-- Global loading state -->
{#if $authLoading}
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Loading...</p>
    </div>
  </div>
{:else}
  <!-- Global error notification -->
  {#if $authError}
    <div class="fixed top-4 right-4 z-50 max-w-sm">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm text-red-800">{$authError}</p>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              type="button"
              class="inline-flex text-red-400 hover:text-red-600 focus:outline-none"
              on:click={authActions.clearError}
            >
              <span class="sr-only">Close</span>
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Main app content -->
  <main class="min-h-screen bg-gray-50">
    <slot />
  </main>
{/if} 