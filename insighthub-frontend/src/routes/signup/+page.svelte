<script lang="ts">
  import { authActions, authLoading, authError, isAuthenticated } from '$lib/stores/authStore'
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'

  let email = ''
  let password = ''
  let confirmPassword = ''
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
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
    }

    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your password'
    } else if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
    }

    return Object.keys(errors).length === 0
  }

  async function handleSubmit() {
    if (!validateForm()) return

    loading = true
    const { data, error } = await authActions.signUp(email, password)
    loading = false

    if (error) {
      console.error('Signup error:', error)
    } else if (data?.user) {
      // Check if user needs to confirm email
      if (!data.session) {
        alert('Please check your email to confirm your account!')
      }
      goto('/')
    }
  }
</script>

<svelte:head>
  <title>Sign Up - InsightHub</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <!-- Header -->
    <div>
      <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
        Create your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <a href="/signin" class="font-medium text-blue-600 hover:text-blue-500">
          sign in to your existing account
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
            autocomplete="new-password"
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

        <!-- Confirm Password field -->
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            autocomplete="new-password"
            required
            bind:value={confirmPassword}
            class="mt-1 appearance-none relative block w-full px-3 py-2 border 
                   {errors.confirmPassword ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-blue-500 focus:border-blue-500'}
                   rounded-md focus:outline-none focus:ring-2 focus:z-10 sm:text-sm"
            placeholder="Confirm your password"
            disabled={loading || $authLoading}
          />
          {#if errors.confirmPassword}
            <p class="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
          {/if}
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
            Creating account...
          {:else}
            Create account
          {/if}
        </button>
      </div>

      <!-- Terms notice -->
      <div class="text-center">
        <p class="text-xs text-gray-500">
          By creating an account, you agree to our 
          <a href="/terms" class="text-blue-600 hover:text-blue-500">Terms of Service</a>
          and 
          <a href="/privacy" class="text-blue-600 hover:text-blue-500">Privacy Policy</a>
        </p>
      </div>
    </form>
  </div>
</div> 