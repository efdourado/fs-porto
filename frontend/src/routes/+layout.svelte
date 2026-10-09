<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import Icon from '$lib/components/Icon.svelte';

  const links = [
    { href: '/', label: 'Buscar', icon: 'search' as const },
    { href: '/contratos', label: 'Contratos', icon: 'doc' as const }
  ];

  // "/contratos/x" também marca "Contratos" como ativo
  $: ativo = (href: string) =>
    href === '/' ? $page.url.pathname === '/' : $page.url.pathname.startsWith(href);
</script>

<!-- Cabeçalho translúcido -->
<header class="sticky top-0 z-40 border-b border-line bg-bg/75 backdrop-blur-xl backdrop-saturate-150">
  <nav class="mx-auto flex h-12 max-w-page items-center justify-between px-5">
    <a href="/" class="flex items-center gap-2 font-display text-[19px] font-semibold tracking-tight">
      <img src="/logo.png" alt="" width="26" height="26" class="h-[26px] w-[26px]" />
      Porto
    </a>

    <ul class="hidden items-center gap-7 sm:flex">
      {#each links as link}
        <li>
          <a
            href={link.href}
            aria-current={ativo(link.href) ? 'page' : undefined}
            class="text-[13px] transition-colors {ativo(link.href) ? 'text-ink' : 'text-muted hover:text-ink'}"
          >
            {link.label}
          </a>
        </li>
      {/each}
    </ul>
  </nav>
</header>

<main class="mx-auto max-w-page px-5 pb-32 sm:pb-24">
  <slot />
</main>

<!-- Barra de abas no celular, no estilo iOS -->
<nav
  class="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-bg/80 backdrop-blur-xl backdrop-saturate-150 sm:hidden"
  style="padding-bottom: env(safe-area-inset-bottom)"
  aria-label="Navegação"
>
  <ul class="grid grid-cols-2">
    {#each links as link}
      <li>
        <a
          href={link.href}
          aria-current={ativo(link.href) ? 'page' : undefined}
          class="flex flex-col items-center gap-0.5 pb-1.5 pt-2 text-[10px] font-medium transition-colors {ativo(link.href) ? 'text-accent' : 'text-muted'}"
        >
          <Icon name={link.icon} size={24} stroke={ativo(link.href) ? 2.1 : 1.75} />
          {link.label}
        </a>
      </li>
    {/each}
  </ul>
</nav>
