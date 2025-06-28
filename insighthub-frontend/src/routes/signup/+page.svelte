<script lang="ts">
  import { SignUpForm, AuthProvider } from '$lib';

  function handleSignUpSuccess(event: CustomEvent) {
    console.log('Sign up successful:', event.detail);
    // Navigation is handled by the SignUpForm component
  }

  function handleSignUpError(event: CustomEvent) {
    console.error('Sign up error:', event.detail.message);
  }
</script>

<svelte:head>
  <title>Sign Up - InsightHub</title>
</svelte:head>

<AuthProvider>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
    <SignUpForm
      redirectTo="/dashboard"
      on:success={handleSignUpSuccess}
      on:error={handleSignUpError}
    />
  </div>
</AuthProvider> 