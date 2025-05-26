<script lang="ts">
  import type { Contrato } from '$lib/services/api';
  
  export let contrato: Contrato;
  export let expanded = false;
</script>

<div class="card bg-base-100 shadow-xl mb-4 hover:shadow-2xl transition-shadow duration-300">
  <div class="card-body">
    <h2 class="card-title flex justify-between">
      <span>{contrato.arquivo}</span>
      {#if contrato.score !== undefined}
        <span class="badge badge-primary">{(contrato.score * 100).toFixed(0)}% relevante</span>
      {/if}
    </h2>
    
    <div class="mt-2">
      {#if expanded || contrato.texto.length < 200}
        <p class="whitespace-pre-line">{contrato.texto}</p>
      {:else}
        <p class="whitespace-pre-line">{contrato.texto.substring(0, 200)}...</p>
      {/if}
    </div>
    
    <div class="card-actions justify-end mt-4">
      <button class="btn btn-sm" on:click={() => expanded = !expanded}>
        {expanded ? 'Mostrar menos' : 'Mostrar mais'}
      </button>
    </div>
  </div>
</div>
