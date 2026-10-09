<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Icon from './Icon.svelte';

  export let value = '';
  export let modo: 'buscar' | 'perguntar' = 'buscar';
  export let carregando = false;

  const dispatch = createEventDispatcher<{ submit: void; modo: void }>();
  let input: HTMLInputElement;

  const modos = [
    { id: 'buscar' as const, label: 'Buscar' },
    { id: 'perguntar' as const, label: 'Perguntar' }
  ];

  $: placeholder = modo === 'perguntar' ? 'Pergunte sobre os contratos' : 'Buscar nos contratos';

  function trocarModo(novo: typeof modo) {
    if (novo === modo) return;
    modo = novo;
    dispatch('modo');
    input?.focus();
  }

  export function focar() {
    input?.focus();
  }
</script>

<div class="flex flex-col items-center gap-4">
  <!-- Controle segmentado -->
  <div class="inline-flex rounded-full bg-surface p-1" role="tablist" aria-label="Modo">
    {#each modos as m}
      <button
        type="button"
        role="tab"
        aria-selected={modo === m.id}
        on:click={() => trocarModo(m.id)}
        class="rounded-full px-4 py-1.5 text-[13px] font-medium transition-all duration-200
          {modo === m.id ? 'bg-elevated text-ink shadow-[0_1px_3px_rgba(0,0,0,0.12)]' : 'text-muted hover:text-ink'}"
      >
        {m.label}
      </button>
    {/each}
  </div>

  <form on:submit|preventDefault={() => dispatch('submit')} class="w-full">
    <label class="group flex h-14 w-full items-center gap-3 rounded-2xl bg-surface pl-4 pr-2 transition-shadow focus-within:shadow-[0_0_0_4px_rgb(var(--accent)/0.15)]">
      <span class="text-muted">
        <Icon name={modo === 'perguntar' ? 'brain' : 'search'} size={20} />
      </span>
      <input
        bind:this={input}
        bind:value
        {placeholder}
        type="search"
        enterkeyhint={modo === 'perguntar' ? 'send' : 'search'}
        autocomplete="off"
        class="h-full min-w-0 flex-1 bg-transparent text-[17px] outline-none placeholder:text-muted [&::-webkit-search-cancel-button]:hidden"
        style="outline: none"
      />
      <button
        type="submit"
        disabled={!value.trim() || carregando}
        aria-label={modo === 'perguntar' ? 'Perguntar' : 'Buscar'}
        class="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-accent text-white transition-all duration-200 disabled:scale-90 disabled:opacity-0"
      >
        <Icon name="arrow-up" size={18} stroke={2.25} />
      </button>
    </label>
  </form>
</div>
