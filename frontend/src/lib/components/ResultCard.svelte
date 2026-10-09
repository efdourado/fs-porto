<script lang="ts">
  import type { Contrato } from '$lib/services/api';
  import { descreverContrato, linkContrato, reflow } from '$lib/contratos';
  import Avatar from './Avatar.svelte';
  import Icon from './Icon.svelte';

  export let resultado: Contrato;

  $: info = descreverContrato(resultado.arquivo);
  $: blocos = reflow(resultado.texto);
  // Títulos do trecho ("RESCISÃO", "FORO") viram rótulos; o resto vira um parágrafo corrido
  $: titulos = blocos.filter((b) => b.titulo).map((b) => b.texto);
  $: corpo = blocos.filter((b) => !b.titulo).map((b) => b.texto).join(' ');
</script>

<a
  href={linkContrato(resultado.arquivo)}
  class="group block rounded-2xl bg-surface p-5 transition-colors hover:bg-surface/60 sm:p-6"
>
  <div class="flex items-center gap-3">
    <Avatar size={36} />
    <div class="min-w-0 flex-1">
      <p class="truncate text-[15px] font-semibold">{info.locatario}</p>
      {#if info.locador}
        <p class="truncate text-[13px] text-muted">{info.locador}{info.codigo ? ` · ${info.codigo}` : ''}</p>
      {/if}
    </div>
    {#if resultado.score}
      <span class="shrink-0 text-[13px] tabular-nums text-muted" title="Similaridade de cosseno">
        {resultado.score.toFixed(2)}
      </span>
    {/if}
    <Icon name="chevron-right" size={18} class="shrink-0 text-muted transition-transform group-hover:translate-x-0.5" />
  </div>

  {#if titulos.length}
    <p class="mt-4 text-[11px] font-semibold uppercase tracking-[0.08em] text-muted">{titulos.join(' · ')}</p>
  {/if}
  <p class="{titulos.length ? 'mt-1.5' : 'mt-4'} line-clamp-3 text-[15px] leading-relaxed text-ink/80">{corpo}</p>
</a>
