<script lang="ts">
  import { page } from '$app/stores';
  import { fade } from 'svelte/transition';
  import Avatar from '$lib/components/Avatar.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import { contratoService, type Contrato } from '$lib/services/api';
  import { descreverContrato, partesDoTexto, reflow, removerSobreposicao } from '$lib/contratos';

  // [arquivo] na pasta vira um parâmetro da rota: /contratos/<nome do arquivo>
  $: arquivo = $page.params.arquivo;

  let trechos: Contrato[] = [];
  let carregando = true;
  let erro = '';
  let visao: 'documento' | 'trechos' = 'documento';

  $: carregar(arquivo);

  async function carregar(nome: string) {
    carregando = true;
    erro = '';
    try {
      trechos = await contratoService.listarTrechos(nome);
      if (!trechos.length) erro = 'Este contrato não está no índice.';
    } catch (e: any) {
      erro = e.message;
    } finally {
      carregando = false;
    }
  }

  // Documento contínuo: junta os chunks tirando a sobreposição entre vizinhos.
  // O splitter corta nas quebras de linha e as descarta, então a junção devolve uma quebra de linha.
  $: documento = trechos.reduce(
    (texto, t, i) => (i === 0 ? t.texto : `${texto}\n${removerSobreposicao(trechos[i - 1].texto, t.texto)}`),
    ''
  );

  // Nome do arquivo como base; o texto do contrato traz os nomes com acentos
  $: info = { ...descreverContrato(arquivo), ...partesDoTexto(documento) };
</script>

<svelte:head>
  <title>{info.locatario} · Porto</title>
</svelte:head>

<article class="mx-auto max-w-2xl pt-6 sm:pt-10">
  <a href="/contratos" class="-ml-1.5 inline-flex items-center text-[15px] text-accent hover:underline">
    <Icon name="chevron-left" size={20} />
    Contratos
  </a>

  <header class="mt-8 flex items-center gap-4">
    <Avatar size={56} />
    <div class="min-w-0">
      <h1 class="font-display text-[28px] font-semibold leading-tight tracking-[-0.02em] sm:text-[34px]">{info.locatario}</h1>
      {#if info.locador}
        <p class="mt-0.5 text-[15px] text-muted">{info.locador}{info.codigo ? ` · ${info.codigo}` : ''}</p>
      {/if}
    </div>
  </header>

  {#if !erro}
    <div class="mt-10 flex justify-center">
      <div class="inline-flex rounded-full bg-surface p-1" role="tablist" aria-label="Visualização">
        {#each [{ id: 'documento', label: 'Documento' }, { id: 'trechos', label: `Trechos${carregando ? '' : ` · ${trechos.length}`}` }] as v}
          <button
            type="button"
            role="tab"
            aria-selected={visao === v.id}
            on:click={() => (visao = v.id === 'trechos' ? 'trechos' : 'documento')}
            class="rounded-full px-4 py-1.5 text-[13px] font-medium transition-all duration-200
              {visao === v.id ? 'bg-elevated text-ink shadow-[0_1px_3px_rgba(0,0,0,0.12)]' : 'text-muted hover:text-ink'}"
          >
            {v.label}
          </button>
        {/each}
      </div>
    </div>
  {/if}

  <section class="mt-10">
    {#if carregando}
      <div class="space-y-3">
        {#each [100, 94, 97, 70, 100, 88, 96, 60] as largura}
          <div class="skeleton h-4" style="width: {largura}%"></div>
        {/each}
      </div>
    {:else if erro}
      <p class="rounded-2xl bg-danger/10 px-5 py-4 text-[15px] text-danger" in:fade>{erro}</p>
    {:else if visao === 'documento'}
      <div class="space-y-5" in:fade={{ duration: 200 }}>
        {#each reflow(documento) as bloco}
          {#if bloco.titulo}
            <h2 class="pt-4 text-[13px] font-semibold uppercase tracking-[0.06em] text-muted first:pt-0">{bloco.texto}</h2>
          {:else}
            <p class="text-[17px] leading-[1.65]">{bloco.texto}</p>
          {/if}
        {/each}
      </div>
    {:else}
      <p class="mb-8 text-[15px] text-muted" in:fade={{ duration: 200 }}>
        Os pedaços exatamente como estão no Pinecone. Cada um tem até 500 caracteres e repete até 50 do anterior para não perder contexto.
      </p>
      <ol class="space-y-3" in:fade={{ duration: 200 }}>
        {#each trechos as trecho, i}
          <li class="rounded-2xl bg-surface p-5">
            <p class="mb-2 text-[12px] font-medium tabular-nums text-muted">Trecho {String(i + 1).padStart(2, '0')} · {trecho.texto.length} caracteres</p>
            <p class="whitespace-pre-line font-mono text-[13px] leading-relaxed text-ink/85">{trecho.texto}</p>
          </li>
        {/each}
      </ol>
    {/if}
  </section>
</article>
