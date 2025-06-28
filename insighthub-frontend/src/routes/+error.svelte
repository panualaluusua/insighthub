<script lang="ts">
  export let error: Error;
  export let status: number;
</script>

<div class="min-h-screen flex flex-col items-center justify-center bg-red-50 text-red-900">
  <div class="text-6xl font-bold mb-4">{status}</div>
  <h1 class="text-2xl font-semibold mb-2">Something went wrong</h1>
  <p class="mb-4">{error?.message || 'An unexpected error occurred.'}</p>
  <a href="/" class="text-blue-600 underline">Go back home</a>
</div> 