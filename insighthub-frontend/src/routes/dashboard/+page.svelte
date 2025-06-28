<script lang="ts">
  import { AuthProvider } from '$lib';
  import { onMount } from 'svelte';
  import { supabase } from '$lib/supabaseClient';
  import { goto } from '$app/navigation';

  let user: any = null;
  let loading = true;

  onMount(async () => {
    // Get current session
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      goto('/signin');
      return;
    }

    user = session.user;
    loading = false;

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_OUT' || !session) {
        goto('/signin');
      } else {
        user = session.user;
      }
    });

    return () => subscription.unsubscribe();
  });

  async function handleSignOut() {
    await supabase.auth.signOut();
  }
</script>

<svelte:head>
  <title>Dashboard - InsightHub</title>
</svelte:head>

<AuthProvider>
  {#if loading}
    <div class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading dashboard...</p>
      </div>
    </div>
  {:else if user}
    <div class="min-h-screen bg-gray-50">
      <!-- Header -->
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center py-6">
            <div class="flex items-center">
              <h1 class="text-2xl font-bold text-gray-900">InsightHub Dashboard</h1>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-gray-700">Welcome, {user.email}</span>
              <button
                on:click={handleSignOut}
                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Welcome Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-2">Welcome to InsightHub!</h3>
              <p class="text-gray-600">
                You have successfully signed in to your account. This is your personal dashboard where you can manage your content and preferences.
              </p>
            </div>
          </div>

          <!-- User Info Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Account Information</h3>
              <dl class="space-y-2">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Email</dt>
                  <dd class="text-sm text-gray-900">{user.email}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">User ID</dt>
                  <dd class="text-sm text-gray-900 font-mono">{user.id}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Email Confirmed</dt>
                  <dd class="text-sm text-gray-900">
                    {user.email_confirmed_at ? 'Yes' : 'Pending confirmation'}
                  </dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Last Sign In</dt>
                  <dd class="text-sm text-gray-900">
                    {user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleString() : 'N/A'}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <!-- Quick Actions Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
              <div class="space-y-3">
                <a
                  href="/"
                  class="block w-full text-left px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Browse Content
                </a>
                <button
                  class="block w-full text-left px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  disabled
                >
                  Manage Preferences (Coming Soon)
                </button>
                <button
                  class="block w-full text-left px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  disabled
                >
                  View Analytics (Coming Soon)
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Content Section -->
        <div class="mt-8">
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-xl font-semibold text-gray-900">Recent Activity</h2>
            </div>
            <div class="p-6">
              <div class="text-center py-12">
                <div class="mx-auto h-12 w-12 text-gray-400">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="mt-2 text-sm font-medium text-gray-900">No activity yet</h3>
                <p class="mt-1 text-sm text-gray-500">
                  Start browsing content to see your activity here.
                </p>
                <div class="mt-6">
                  <a
                    href="/"
                    class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Browse Content
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  {/if}
</AuthProvider> 