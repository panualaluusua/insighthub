<script lang="ts">
  // No script needed for static showcase
</script>

<svelte:head>
  <title>InsightHub Theme Showcase</title>
</svelte:head>

<div class="max-w-3xl mx-auto py-12 px-4">
  <h1 class="text-3xl font-bold mb-8">InsightHub Theme Showcase</h1>

  <section class="mb-12">
    <h2 class="text-xl font-semibold mb-4">Primary Color Palette</h2>
    <div class="grid grid-cols-5 gap-4">
      {#each [50,100,200,300,400,500,600,700,800,900] as shade}
        <div class="flex flex-col items-center">
          <div class={`w-16 h-16 rounded-lg bg-primary-${shade} border`}></div>
          <span class="mt-2 text-sm">primary-{shade}</span>
        </div>
      {/each}
    </div>
  </section>

  <section class="mb-12">
    <h2 class="text-xl font-semibold mb-4">Font Family</h2>
    <p class="font-sans text-lg">This is the default sans-serif font: Inter, system-ui, -apple-system, sans-serif.</p>
  </section>

  <section class="mb-12">
    <h2 class="text-xl font-semibold mb-4">Buttons</h2>
    <div class="flex gap-4">
      <button class="btn-primary">Primary Button</button>
      <button class="btn-secondary">Secondary Button</button>
    </div>
  </section>

  <section>
    <h2 class="text-xl font-semibold mb-4">Form Input</h2>
    <input class="form-input" placeholder="Form input example" />
  </section>
</div> 