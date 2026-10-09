<script lang="ts">
  import type { LLMResponse } from '$lib/services/api';
  import { renderMarkdown } from '$lib/markdown';
  import { descreverContrato, linkContrato } from '$lib/contratos';
  import Icon from './Icon.svelte';

  export let resposta: LLMResponse;

  $: html = renderMarkdown(resposta.answer);
  // Um mesmo contrato pode aparecer em vários trechos; mostra cada um só uma vez
  $: fontes = [...new Set(resposta.sources.map((s) => s.filename).filter(Boolean))] as string[];
</script>

<article class="rounded-3xl bg-surface p-6 sm:p-8">
  <p class="mb-5 flex items-center gap-2 text-[13px] font-medium text-muted">
    <Icon name="brain" size={16} />
    Resposta
  </p>

  <div class="markdown">
    {@html html}
  </div>

  {#if fontes.length}
    <div class="mt-8 border-t border-line pt-5">
      <p class="mb-3 text-[13px] font-medium text-muted">Trechos consultados</p>
      <ul class="flex flex-wrap gap-2">
        {#each fontes as arquivo}
          <li>
            <a
              href={linkContrato(arquivo)}
              class="inline-flex items-center rounded-full bg-elevated px-3 py-1.5 text-[13px] transition-colors hover:text-accent"
            >
              {descreverContrato(arquivo).locatario}
            </a>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</article>
