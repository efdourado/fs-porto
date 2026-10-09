<script lang="ts">
  // Ícones em traço fino, no estilo SF Symbols
  export let name: 'search' | 'brain' | 'doc' | 'plus' | 'chevron-right' | 'chevron-left' | 'arrow-up' | 'x';
  export let size = 20;
  export let stroke = 1.75;
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width={stroke}
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
  class={$$props.class}
>
  {#if name === 'search'}
    <circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
  {:else if name === 'brain'}
    <!-- cérebro (Lucide, licença ISC) -->
    <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
    <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
    <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4M17.6 6.5a3 3 0 0 0 .4-1.375M6 5.125A3 3 0 0 0 6.4 6.5M3.48 10.9a4 4 0 0 1 .58-.4M19.94 10.5a4 4 0 0 1 .58.4M6 18a4 4 0 0 1-1.97-.52M19.97 17.48A4 4 0 0 1 18 18" />
  {:else if name === 'doc'}
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5M9 13h6M9 17h4" />
  {:else if name === 'plus'}
    <path d="M12 5v14M5 12h14" />
  {:else if name === 'chevron-right'}
    <path d="m9 6 6 6-6 6" />
  {:else if name === 'chevron-left'}
    <path d="m15 6-6 6 6 6" />
  {:else if name === 'arrow-up'}
    <path d="M12 19V5M5 12l7-7 7 7" />
  {:else if name === 'x'}
    <path d="M6 6l12 12M18 6 6 18" />
  {/if}
</svg>
