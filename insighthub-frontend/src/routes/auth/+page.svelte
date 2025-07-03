<script lang="ts">
  import { supabase } from '$lib/supabaseClient';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let isLogin = true;
  let email = '';
  let password = '';
  let loading = false;
  let errorMessage = '';

  onMount(() => {
    supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        goto('/'); // Redirect to home if already logged in
      }
    });
  });

  async function handleAuth() {
    loading = true;
    errorMessage = '';

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        goto('/');
      } else {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;

        if (data.user) {
          // Create profile entry for new user
          const { error: profileError } = await supabase.from('profiles').insert({
            id: data.user.id,
            interest_vector: {}, // Initialize with empty object
            interests: [] // Initialize with empty array
          });
          if (profileError) throw profileError;
        }
        alert('Check your email for the login link!');
        isLogin = true; // Switch to login after successful sign-up
      }
    } catch (error: any) {
      errorMessage = error.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-100 p-4">
  <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-lg">
    <h1 class="mb-6 text-center text-3xl font-bold text-gray-800">
      {isLogin ? 'Login' : 'Sign Up'}
    </h1>

    <form on:submit|preventDefault={handleAuth} class="space-y-6">
      <div>
        <label for="email" class="mb-2 block text-sm font-medium text-gray-700">Email</label>
        <input
          type="email"
          id="email"
          bind:value={email}
          required
          class="w-full rounded-md border border-gray-300 p-3 focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
          placeholder="your.email@example.com"
        />
      </div>

      <div>
        <label for="password" class="mb-2 block text-sm font-medium text-gray-700">Password</label>
        <input
          type="password"
          id="password"
          bind:value={password}
          required
          class="w-full rounded-md border border-gray-300 p-3 focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
          placeholder="••••••••"
        />
      </div>

      {#if errorMessage}
        <p class="text-center text-red-500">{errorMessage}</p>
      {/if}

      <button
        type="submit"
        disabled={loading}
        class="w-full rounded-md bg-blue-600 p-3 text-lg font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 disabled:opacity-50"
      >
        {loading ? 'Loading...' : isLogin ? 'Login' : 'Sign Up'}
      </button>
    </form>

    <p class="mt-6 text-center text-sm text-gray-600">
      {isLogin ? "Don't have an account?" : 'Already have an account?'}
      <button on:click={() => (isLogin = !isLogin)} class="font-medium text-blue-600 hover:underline"
        >{isLogin ? 'Sign Up' : 'Login'}</button
      >
    </p>
  </div>
</div>
