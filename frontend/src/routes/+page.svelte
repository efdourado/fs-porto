<script lang="ts">
  import SearchBar from '$lib/components/SearchBar.svelte';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import { onMount } from 'svelte';
  
  let searchQuery = '';
  let isVisible = false;
  
  onMount(() => {
    // Pequeno atraso para a animação de entrada
    setTimeout(() => {
      isVisible = true;
    }, 100);
  });
  
  function handleSearch(event: CustomEvent<string>) {
    const query = event.detail;
    if (query) {
      goto(`/contratos?q=${encodeURIComponent(query)}`);
    }
  }
</script>

<div class="min-h-[85vh] py-12 px-4">
  {#if isVisible}
    <div class="max-w-6xl mx-auto" in:fade={{ duration: 800, delay: 200 }}>
      <!-- Hero Section com Gradiente Animado -->
      <div class="hero rounded-2xl overflow-hidden bg-gradient-to-br from-primary/5 to-secondary/5 backdrop-blur-sm shadow-lg mb-16">
        <div class="hero-content flex-col lg:flex-row py-12 px-8">
          <!-- Texto Principal -->
          <div class="lg:w-1/2 text-center lg:text-left" in:fly={{ y: 20, duration: 800, delay: 300 }}>
            <h1 class="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              <span class="text-primary">Inteligência</span> para seus <span class="text-secondary">contratos</span>
            </h1>
            <p class="text-lg opacity-90 mb-8 leading-relaxed">
              Encontre informações em contratos imobiliários usando busca semântica avançada.
              Pesquise por conceitos, cláusulas ou detalhes específicos em linguagem natural.
            </p>
            
            <!-- Barra de Pesquisa -->
            <div class="w-full max-w-xl mx-auto lg:mx-0">
              <SearchBar 
                bind:value={searchQuery} 
                placeholder="Ex: Quais são as cláusulas de rescisão? Qual o valor do aluguel?"
                on:search={handleSearch}
              />
            </div>
          </div>
          
          <!-- Ilustração/Imagem -->
          <div class="lg:w-1/2 mt-8 lg:mt-0 flex justify-center" in:fly={{ x: 20, duration: 800, delay: 500 }}>
            <div class="relative w-full max-w-md">
              <div class="absolute -inset-0.5 bg-gradient-to-r from-primary to-secondary rounded-2xl blur opacity-30 animate-pulse"></div>
              <div class="relative bg-base-100 rounded-2xl shadow-xl p-6">
                <div class="h-64 flex items-center justify-center">
                  <svg class="w-48 h-48 text-primary/20" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6H12L10 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6ZM14 16H6V14H14V16ZM18 12H6V10H18V12Z" />
                  </svg>
                </div>
                <div class="space-y-2">
                  <div class="h-2 bg-primary/10 rounded-full"></div>
                  <div class="h-2 bg-primary/10 rounded-full w-5/6"></div>
                  <div class="h-2 bg-primary/10 rounded-full w-4/6"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Features Cards -->
      <h2 class="text-2xl font-bold text-center mb-8" in:fade={{ duration: 800, delay: 600 }}>Recursos Poderosos</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8" in:fade={{ duration: 800, delay: 700 }}>
        <!-- Card 1 -->
        <div class="card bg-base-100 hover:shadow-xl transition-all duration-300 border border-base-200 hover:border-primary/20">
          <div class="card-body items-center text-center">
            <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h2 class="card-title font-bold">Busca Semântica</h2>
            <p class="opacity-75">Encontre informações usando linguagem natural, sem precisar de palavras-chave exatas.</p>
          </div>
        </div>
        
        <!-- Card 2 -->
        <div class="card bg-base-100 hover:shadow-xl transition-all duration-300 border border-base-200 hover:border-primary/20">
          <div class="card-body items-center text-center">
            <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 class="card-title font-bold">Contratos Digitalizados</h2>
            <p class="opacity-75">Acesse rapidamente todos os contratos imobiliários em um só lugar.</p>
          </div>
        </div>
        
        <!-- Card 3 -->
        <div class="card bg-base-100 hover:shadow-xl transition-all duration-300 border border-base-200 hover:border-primary/20">
          <div class="card-body items-center text-center">
            <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 class="card-title font-bold">Resultados Instantâneos</h2>
            <p class="opacity-75">Obtenha respostas rápidas e precisas sobre cláusulas e condições contratuais.</p>
          </div>
        </div>
      </div>
      
      <!-- Call to Action -->
      <div class="mt-16 text-center" in:fade={{ duration: 800, delay: 900 }}>
        <div class="p-8 rounded-2xl bg-gradient-to-r from-primary to-secondary text-white">
          <h2 class="text-2xl font-bold mb-4">Comece a explorar seus contratos agora</h2>
          <p class="mb-6 max-w-2xl mx-auto">Descubra o poder da inteligência artificial aplicada à análise de contratos imobiliários.</p>
          <button class="btn btn-lg bg-white text-primary hover:bg-white/90 border-none" on:click={() => goto('/contratos')}>Ver Contratos</button>
        </div>
      </div>
    </div>
  {/if}
</div>
