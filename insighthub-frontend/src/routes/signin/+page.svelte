<script lang="ts">
  import { authActions, authLoading, isAuthenticated } from '$lib/stores/authStore'
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'

  let email = ''
  let password = ''
  let loading = false
  let errors: Record<string, string> = {}

  // Redirect if already authenticated
  onMount(() => {
    const unsubscribe = isAuthenticated.subscribe(isAuth => {
      if (isAuth) {
        goto('/')
      }
    })
    return unsubscribe
  })

  function validateForm() {
    errors = {}
    
    if (!email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address'
    }

    if (!password) {
      errors.password = 'Password is required'
    }

    return Object.keys(errors).length === 0
  }

  async function handleSubmit() {
    if (!validateForm()) return

    loading = true
    const { data, error } = await authActions.signIn(email, password)
    loading = false

    if (error) {
      console.error('Signin error:', error)
    } else if (data?.user) {
      goto('/')
    }
  }
</script>

<svelte:head>
  <title>Sign In - InsightHub</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <!-- Header -->
    <div>
      <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
        Sign in to your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <a href="/signup" class="font-medium text-blue-600 hover:text-blue-500">
          create a new account
        </a>
      </p>
    </div>

    <!-- Form -->
    <form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
      <div class="space-y-4">
        <!-- Email field -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autocomplete="email"
            required
            bind:value={email}
            class="mt-1 appearance-none relative block w-full px-3 py-2 border 
                   {errors.email ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-blue-500 focus:border-blue-500'}
                   rounded-md focus:outline-none focus:ring-2 focus:z-10 sm:text-sm"
            placeholder="Enter your email"
            disabled={loading || $authLoading}
          />
          {#if errors.email}
            <p class="mt-1 text-sm text-red-600">{errors.email}</p>
          {/if}
        </div>

        <!-- Password field -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autocomplete="current-password"
            required
            bind:value={password}
            class="mt-1 appearance-none relative block w-full px-3 py-2 border 
                   {errors.password ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-blue-500 focus:border-blue-500'}
                   rounded-md focus:outline-none focus:ring-2 focus:z-10 sm:text-sm"
            placeholder="Enter your password"
            disabled={loading || $authLoading}
          />
          {#if errors.password}
            <p class="mt-1 text-sm text-red-600">{errors.password}</p>
          {/if}
        </div>
      </div>

      <!-- Remember me and forgot password -->
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <input
            id="remember-me"
            name="remember-me"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="remember-me" class="ml-2 block text-sm text-gray-900">
            Remember me
          </label>
        </div>

        <div class="text-sm">
          <a href="/forgot-password" class="font-medium text-blue-600 hover:text-blue-500">
            Forgot your password?
          </a>
        </div>
      </div>

      <!-- Submit button -->
      <div>
        <button
          type="submit"
          disabled={loading || $authLoading}
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white 
                 {loading || $authLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}
                 focus:outline-none transition-colors duration-200"
        >
          {#if loading || $authLoading}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Signing in...
          {:else}
            Sign in
          {/if}
        </button>
      </div>
    </form>
  </div>
</div> 