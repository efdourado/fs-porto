<script>
  import '../app.css';
  import { writable } from 'svelte/store';
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  
  // Store global para controlar a visibilidade do status da API
  export const showApiStatus = writable(false);
  
  // Store para controlar o tema atual
  export const currentTheme = writable('contratuslight');
  
  // Função para alternar o tema entre claro e escuro
  function toggleTheme() {
    currentTheme.update(theme => {
      const newTheme = theme === 'contratusdark' ? 'contratuslight' : 'contratusdark';
      localStorage.setItem('contratus-theme', newTheme);
      document.documentElement.setAttribute('data-theme', newTheme);
      return newTheme;
    });
  }
  
  // Carregar o tema salvo no localStorage ao montar o componente
  onMount(() => {
    const savedTheme = localStorage.getItem('contratus-theme') || 'contratuslight';
    document.documentElement.setAttribute('data-theme', savedTheme);
    currentTheme.set(savedTheme);
  });
  
  function toggleApiStatus() {
    showApiStatus.update(value => {
      const newValue = !value;
      console.log('Toggle API Status:', newValue);
      return newValue;
    });
  }
</script>

<div class="min-h-screen flex flex-col bg-base-100 animate-fade-in">
  <header class="sticky top-0 z-50">
    <div class="navbar bg-gradient-to-r from-primary to-secondary text-primary-content shadow-lg">
      <div class="navbar-start">
        <div class="dropdown">
          <label tabindex="0" class="btn btn-ghost lg:hidden hover:bg-primary/20 transition-all duration-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </label>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow-lg bg-base-100 rounded-xl w-52 text-base-content">
            <li><a href="/" class="font-medium hover:text-primary transition-colors duration-300">Início</a></li>
            <li><a href="/contratos" class="font-medium hover:text-primary transition-colors duration-300">Contratos</a></li>
            <li><a href="/sobre" class="font-medium hover:text-primary transition-colors duration-300">Sobre</a></li>
          </ul>
        </div>
        <a href="/" class="btn btn-ghost normal-case text-xl font-bold tracking-tight hover:bg-primary/20 transition-all duration-300">
          <span class="text-white">Contratus</span><span class="text-accent">AI</span>
        </a>
      </div>
      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><a href="/" class="font-medium hover:bg-primary/20 transition-colors duration-300">Início</a></li>
          <li><a href="/contratos" class="font-medium hover:bg-primary/20 transition-colors duration-300">Contratos</a></li>
          <li><a href="/sobre" class="font-medium hover:bg-primary/20 transition-colors duration-300">Sobre</a></li>
        </ul>
      </div>
      <div class="navbar-end">
        <label class="swap swap-rotate btn btn-circle btn-ghost hover:bg-primary/20 transition-all duration-300">
          <!-- Controle do tema com checked baseado no estado atual -->
          <input 
            type="checkbox" 
            class="theme-controller" 
            on:change={toggleTheme} 
            checked={$currentTheme === 'britodark'} 
          />
          <!-- Ícone do sol (modo claro) -->
          <svg class="swap-on fill-current w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" />
          </svg>
          <!-- Ícone da lua (modo escuro) -->
          <svg class="swap-off fill-current w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" />
          </svg>
        </label>
      </div>
    </div>
  </header>

  <main class="flex-grow container mx-auto px-4 py-8" transition:fade={{ duration: 300 }}>
    <slot />
  </main>

  <footer class="p-6 bg-gradient-to-r from-base-200 to-base-300 text-base-content">
    <div class="footer-content container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
      <div class="flex items-center">
        <span class="font-bold text-primary mr-2">Contratus AI</span>
        <p>Copyright © 2025 - Todos os direitos reservados</p>
      </div>
      
      <div class="flex space-x-4">
        <a href="/" class="link link-hover hover:text-primary transition-colors duration-300">Política de Privacidade</a>
        <a href="/" class="link link-hover hover:text-primary transition-colors duration-300">Termos de Uso</a>
        
        <!-- Botão discreto para mostrar/ocultar status da API -->
        <button 
          class="btn btn-sm btn-ghost hover:bg-base-300 transition-all duration-300" 
          on:click={toggleApiStatus} 
          title="Mostrar/ocultar status da API"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span class="text-xs ml-1">API</span>
        </button>
      </div>
    </div>
  </footer>
</div>
