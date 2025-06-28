<script lang="ts">
  import { LoginForm, AuthProvider } from '$lib';
  import { goto } from '$app/navigation';

  function handleLoginSuccess(event: CustomEvent) {
    console.log('Login successful:', event.detail);
    // Navigation is handled by the LoginForm component
  }

  function handleLoginError(event: CustomEvent) {
    console.error('Login error:', event.detail.message);
  }

  function handleForgotPassword(event: CustomEvent) {
    console.log('Forgot password for:', event.detail.email);
    // Navigate to forgot password page
    goto('/forgot-password');
  }
</script>

<svelte:head>
  <title>Sign In - InsightHub</title>
</svelte:head>

<AuthProvider>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
    <LoginForm
      redirectTo="/dashboard"
      on:success={handleLoginSuccess}
      on:error={handleLoginError}
      on:forgotPassword={handleForgotPassword}
    />
  </div>
</AuthProvider> 