<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import SearchField from '$lib/components/SearchField.svelte';
  import ResultCard from '$lib/components/ResultCard.svelte';
  import Answer from '$lib/components/Answer.svelte';
  import { contratoService, type Contrato, type LLMResponse } from '$lib/services/api';

  type Modo = 'buscar' | 'perguntar';

  const sugestoes: Record<Modo, string[]> = {
    buscar: ['multa por rescisão', 'reajuste pelo IGP-M', 'garantia e fiador', 'prazo de vigência'],
    perguntar: [
      'Quem é o locador do imóvel da Carla Ferreira Santos?',
      'Como é feito o reajuste do aluguel?',
      'Quais são as obrigações do locatário?'
    ]
  };

  let texto = '';
  let modo: Modo = 'buscar';
  let estado: 'vazio' | 'carregando' | 'pronto' | 'erro' = 'vazio';
  let resultados: Contrato[] = [];
  let resposta: LLMResponse | null = null;
  let erro = '';
  let chaveAtual = '';

  // A URL é a fonte da verdade (?q=...&modo=perguntar): voltar/avançar do navegador e links funcionam
  $: consulta = $page.url.searchParams.get('q')?.trim() ?? '';
  $: modoUrl = ($page.url.searchParams.get('modo') === 'perguntar' ? 'perguntar' : 'buscar') as Modo;
  $: executar(consulta, modoUrl);

  async function executar(q: string, m: Modo) {
    const chave = `${m}|${q}`;
    if (chave === chaveAtual) return;
    chaveAtual = chave;
    modo = m;
    texto = q;

    if (!q) {
      estado = 'vazio';
      return;
    }

    estado = 'carregando';
    erro = '';
    resultados = [];
    resposta = null;

    try {
      if (m === 'perguntar') {
        const r = await contratoService.askQuestion(q);
        if (chave !== chaveAtual) return; // chegou uma consulta mais nova enquanto esperava
        resposta = r;
      } else {
        const r = await contratoService.buscarContratos(q);
        if (chave !== chaveAtual) return;
        resultados = r.resultados;
      }
      estado = 'pronto';
    } catch (e: any) {
      if (chave !== chaveAtual) return;
      erro = e.message;
      estado = 'erro';
    }
  }

  function enviar() {
    const q = texto.trim();
    if (!q) return;
    const params = new URLSearchParams({ q });
    if (modo === 'perguntar') params.set('modo', 'perguntar');
    goto(`/?${params}`, { keepFocus: true, noScroll: true });
  }

  function usarSugestao(s: string) {
    texto = s;
    enviar();
  }

  // Ao trocar de modo com algo digitado, refaz a consulta no modo novo
  function trocouModo() {
    if (texto.trim()) enviar();
  }
</script>

<svelte:head>
  <title>{consulta ? `${consulta} · Porto` : 'Porto'}</title>
</svelte:head>

<section
  class="mx-auto max-w-2xl transition-[padding] duration-500 ease-out {estado === 'vazio' ? 'pt-[14vh] sm:pt-[18vh]' : 'pt-8 sm:pt-12'}"
>
  {#if estado === 'vazio'}
    <div class="mb-10 text-center" in:fade={{ duration: 300 }}>
      <h1 class="font-display text-[40px] font-semibold leading-[1.08] tracking-[-0.03em] sm:text-[56px]">
        Seus contratos,<br /><span class="text-muted">em uma pergunta.</span>
      </h1>
      <p class="mx-auto mt-5 max-w-md text-[17px] text-muted sm:text-[19px]">
        Encontre cláusulas pelo significado ou pergunte e receba a resposta com as fontes.
      </p>
    </div>
  {/if}

  <SearchField bind:value={texto} bind:modo carregando={estado === 'carregando'} on:submit={enviar} on:modo={trocouModo} />

  {#if estado === 'vazio'}
    <ul class="mt-6 flex flex-wrap justify-center gap-2" in:fade={{ duration: 300, delay: 100 }}>
      {#each sugestoes[modo] as s (s)}
        <li>
          <button
            type="button"
            on:click={() => usarSugestao(s)}
            class="rounded-full border border-line px-3.5 py-1.5 text-[13px] text-muted transition-colors hover:border-transparent hover:bg-surface hover:text-ink"
          >
            {s}
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</section>

<section class="mx-auto mt-10 max-w-2xl" aria-live="polite">
  {#if estado === 'carregando'}
    {#if modo === 'perguntar'}
      <div class="rounded-3xl bg-surface p-6 sm:p-8" in:fade={{ duration: 200 }}>
        <p class="mb-6 flex items-center gap-1 text-[13px] font-medium text-muted">
          Lendo os contratos
          <span class="animate-pulse-dot">.</span><span class="animate-pulse-dot [animation-delay:0.2s]">.</span><span class="animate-pulse-dot [animation-delay:0.4s]">.</span>
        </p>
        <div class="space-y-3">
          <div class="skeleton h-4 w-11/12"></div>
          <div class="skeleton h-4 w-full"></div>
          <div class="skeleton h-4 w-4/5"></div>
          <div class="skeleton h-4 w-2/3"></div>
        </div>
      </div>
    {:else}
      <div class="space-y-3" in:fade={{ duration: 200 }}>
        {#each [0, 1, 2] as _}
          <div class="rounded-2xl bg-surface p-6">
            <div class="flex items-center gap-3">
              <div class="skeleton h-9 w-9 rounded-full"></div>
              <div class="flex-1 space-y-2">
                <div class="skeleton h-3.5 w-1/3"></div>
                <div class="skeleton h-3 w-1/4"></div>
              </div>
            </div>
            <div class="mt-5 space-y-2">
              <div class="skeleton h-3.5 w-full"></div>
              <div class="skeleton h-3.5 w-5/6"></div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {:else if estado === 'erro'}
    <p class="rounded-2xl bg-danger/10 px-5 py-4 text-[15px] text-danger" in:fade>{erro}</p>
  {:else if estado === 'pronto'}
    {#if resposta}
      <div in:fly={{ y: 12, duration: 400 }}>
        <Answer {resposta} />
      </div>
    {:else if resultados.length}
      <p class="mb-4 px-1 text-[13px] text-muted" in:fade>
        {resultados.length} {resultados.length === 1 ? 'trecho' : 'trechos'} mais próximos de “{consulta}”
      </p>
      <ul class="space-y-3">
        {#each resultados as resultado, i}
          <li in:fly={{ y: 12, duration: 400, delay: i * 40 }}>
            <ResultCard {resultado} />
          </li>
        {/each}
      </ul>
    {:else}
      <p class="py-12 text-center text-muted" in:fade>Nada encontrado para “{consulta}”.</p>
    {/if}
  {/if}
</section>
