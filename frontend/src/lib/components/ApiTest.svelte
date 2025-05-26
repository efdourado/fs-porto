<script>
  import { onMount } from 'svelte';
  import api from '$lib/services/api';
  
  let status = 'API Status';
  let apiStatus = 'verificando';
  let pineconeStatus = 'verificando';
  let isLoading = true;
  let error = null;
  
  onMount(async () => {
    try {
      const response = await api.get('/');
      apiStatus = response.data.status;
      pineconeStatus = response.data.pinecone_status;
      isLoading = false;
    } catch (err) {
      apiStatus = 'offline';
      pineconeStatus = 'erro';
      error = err.message || 'Erro ao conectar com a API';
      isLoading = false;
    }
  });
</script>

<div class="card bg-base-100 shadow-xl w-full max-w-md mx-auto mt-4">
  <div class="card-body">
    <h2 class="card-title">{status}</h2>
    
    {#if isLoading}
      <div class="flex justify-center my-4">
        <span class="loading loading-spinner loading-md text-primary"></span>
      </div>
      <p class="text-center text-sm text-gray-600">Verificando status...</p>
    {:else}
      {#if error}
        <div class="alert alert-error shadow-lg my-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      {:else}
        <div class="alert alert-success shadow-lg my-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Sistema funcionando normalmente</span>
        </div>
        
        <div class="grid grid-cols-2 gap-2 my-3">
          <div class="stat-box p-2 bg-base-200 rounded-lg">
            <p class="text-xs font-semibold">API Status</p>
            <p class="text-sm">
              <span class:badge-success={apiStatus === 'online'} class:badge-warning={apiStatus === 'degradado'} class:badge-error={apiStatus !== 'online' && apiStatus !== 'degradado'} class="badge">
                {apiStatus}
              </span>
            </p>
          </div>
          <div class="stat-box p-2 bg-base-200 rounded-lg">
            <p class="text-xs font-semibold">Pinecone Status</p>
            <p class="text-sm">
              <span class:badge-success={pineconeStatus === 'conectado'} class:badge-warning={pineconeStatus === 'reconectado'} class:badge-error={pineconeStatus !== 'conectado' && pineconeStatus !== 'reconectado'} class="badge">
                {pineconeStatus}
              </span>
            </p>
          </div>
        </div>
      {/if}
    {/if}
    
    <div class="card-actions justify-end">
      <a href="/contratos" class="btn btn-primary">Ver Contratos</a>
    </div>
  </div>
</div>
