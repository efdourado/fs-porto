<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fade, fly, slide } from 'svelte/transition';
  import Avatar from '$lib/components/Avatar.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import { contratoService } from '$lib/services/api';
  import { uploadService } from '$lib/services/upload-api';
  import { descreverContrato, linkContrato, type InfoContrato } from '$lib/contratos';

  let contratos: InfoContrato[] = [];
  let carregando = true;
  let erro = '';
  let filtro = '';

  // Upload
  let seletor: HTMLInputElement;
  let aviso: { tipo: 'progresso' | 'ok' | 'erro'; texto: string } | null = null;
  let espera: ReturnType<typeof setInterval> | undefined;

  $: termo = normalizar(filtro);
  $: visiveis = contratos.filter((c) =>
    normalizar(`${c.locatario} ${c.locador} ${c.codigo}`).includes(termo)
  );

  // Ignora acentos e maiúsculas no filtro
  function normalizar(s: string) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
  }

  async function carregar() {
    try {
      const arquivos = await contratoService.listarArquivos();
      contratos = arquivos
        .map(descreverContrato)
        .sort((a, b) => a.locatario.localeCompare(b.locatario, 'pt-BR'));
      erro = '';
    } catch (e: any) {
      erro = e.message;
    } finally {
      carregando = false;
    }
  }

  async function enviar(event: Event) {
    const arquivo = (event.target as HTMLInputElement).files?.[0];
    seletor.value = '';
    if (!arquivo) return;

    aviso = { tipo: 'progresso', texto: `Enviando ${arquivo.name}` };
    try {
      const { arquivo: nome } = await uploadService.enviarContrato(arquivo);
      aviso = { tipo: 'progresso', texto: 'Lendo e indexando o contrato' };
      aguardarIndexacao(nome);
    } catch (e: any) {
      aviso = { tipo: 'erro', texto: e.message };
    }
  }

  // A indexação roda em segundo plano no servidor: consulta a lista até o arquivo aparecer
  function aguardarIndexacao(nome: string) {
    let tentativas = 0;
    clearInterval(espera);
    espera = setInterval(async () => {
      tentativas++;
      const arquivos = await contratoService.listarArquivos().catch((): string[] => []);
      if (arquivos.includes(nome)) {
        clearInterval(espera);
        await carregar();
        aviso = { tipo: 'ok', texto: `${descreverContrato(nome).locatario} foi adicionado.` };
        setTimeout(() => (aviso = null), 4000);
      } else if (tentativas >= 40) {
        clearInterval(espera);
        aviso = { tipo: 'erro', texto: 'O contrato foi enviado, mas a indexação está demorando. Veja o terminal da API de upload.' };
      }
    }, 3000);
  }

  onMount(carregar);
  onDestroy(() => clearInterval(espera));
</script>

<svelte:head>
  <title>Contratos · Porto</title>
</svelte:head>

<div class="mx-auto max-w-2xl pt-10 sm:pt-16">
  <header class="flex items-end justify-between gap-4">
    <div>
      <h1 class="font-display text-[34px] font-semibold leading-tight tracking-[-0.025em] sm:text-[40px]">Contratos</h1>
      <p class="mt-1 text-[15px] text-muted">
        {#if carregando}&nbsp;{:else}{contratos.length} {contratos.length === 1 ? 'contrato indexado' : 'contratos indexados'}{/if}
      </p>
    </div>

    <button
      type="button"
      on:click={() => seletor.click()}
      disabled={aviso?.tipo === 'progresso'}
      class="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-accent px-4 py-2 text-[15px] font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
    >
      <Icon name="plus" size={18} stroke={2.25} />
      Adicionar
    </button>
    <input bind:this={seletor} type="file" accept="application/pdf,.pdf" class="hidden" on:change={enviar} />
  </header>

  {#if aviso}
    <div
      transition:slide={{ duration: 250 }}
      class="mt-6 flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px]
        {aviso.tipo === 'erro' ? 'bg-danger/10 text-danger' : aviso.tipo === 'ok' ? 'bg-accent/10 text-accent' : 'bg-surface text-ink'}"
    >
      {#if aviso.tipo === 'progresso'}
        <span class="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-muted/30 border-t-accent"></span>
      {/if}
      <span class="flex-1">{aviso.texto}</span>
      {#if aviso.tipo !== 'progresso'}
        <button type="button" on:click={() => (aviso = null)} aria-label="Fechar" class="opacity-60 hover:opacity-100">
          <Icon name="x" size={16} />
        </button>
      {/if}
    </div>
  {/if}

  <label class="mt-8 flex h-10 items-center gap-2 rounded-xl bg-surface px-3 text-muted">
    <Icon name="search" size={16} />
    <input
      bind:value={filtro}
      type="search"
      placeholder="Filtrar por nome, empresa ou código"
      class="h-full min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-muted"
      style="outline: none"
    />
  </label>

  <div class="mt-6">
    {#if carregando}
      <div class="overflow-hidden rounded-2xl bg-surface">
        {#each Array(6) as _}
          <div class="flex items-center gap-4 px-4 py-3.5">
            <div class="skeleton h-10 w-10 rounded-full"></div>
            <div class="flex-1 space-y-2">
              <div class="skeleton h-3.5 w-2/5"></div>
              <div class="skeleton h-3 w-1/3"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else if erro}
      <p class="rounded-2xl bg-danger/10 px-5 py-4 text-[15px] text-danger" in:fade>{erro}</p>
    {:else if contratos.length === 0}
      <div class="py-16 text-center" in:fade>
        <p class="text-[17px] font-medium">Nenhum contrato ainda</p>
        <p class="mt-1 text-[15px] text-muted">Adicione um PDF para começar.</p>
      </div>
    {:else if visiveis.length === 0}
      <p class="py-12 text-center text-muted" in:fade>Nenhum contrato corresponde a “{filtro}”.</p>
    {:else}
      <!-- Lista agrupada, no estilo dos Ajustes do iOS -->
      <ul class="overflow-hidden rounded-2xl bg-surface" in:fade={{ duration: 200 }}>
        {#each visiveis as c, i (c.arquivo)}
          <li in:fly={{ y: 6, duration: 300, delay: Math.min(i, 12) * 25 }}>
            <a href={linkContrato(c.arquivo)} class="group flex items-center gap-4 px-4 transition-colors hover:bg-line">
              <Avatar size={40} />
              <div class="flex min-w-0 flex-1 items-center gap-3 py-3.5 {i > 0 ? 'border-t border-line' : ''}">
                <div class="min-w-0 flex-1">
                  <p class="truncate text-[17px]">{c.locatario}</p>
                  {#if c.locador}
                    <p class="truncate text-[13px] text-muted">{c.locador}</p>
                  {/if}
                </div>
                {#if c.codigo}
                  <span class="hidden shrink-0 rounded-md bg-line px-1.5 py-0.5 font-mono text-[12px] text-muted sm:inline">{c.codigo}</span>
                {/if}
                <Icon name="chevron-right" size={18} class="shrink-0 text-muted/60" />
              </div>
            </a>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</div>
