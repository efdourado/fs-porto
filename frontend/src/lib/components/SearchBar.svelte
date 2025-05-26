<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let placeholder = 'Buscar em contratos...';
  export let value = '';
  
  const dispatch = createEventDispatcher();
  
  function handleSubmit() {
    dispatch('search', value);
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="w-full">
  <div class="join w-full">
    <input
      type="text"
      bind:value
      placeholder={placeholder}
      class="input input-bordered join-item w-full"
    />
    <button type="submit" class="btn btn-primary join-item">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      Buscar
    </button>
  </div>
</form>
