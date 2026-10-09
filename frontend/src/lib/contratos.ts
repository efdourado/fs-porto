export interface InfoContrato {
  arquivo: string;
  locatario: string;
  locador: string;
  codigo: string;
}

/**
 * Extrai as partes legíveis do nome do arquivo.
 * "Contrato_Altos_Padroes_Construcoes_GR340_X_Bruno_Mendes_Oliveira.pdf"
 *   → locador "Altos Padroes Construcoes", código "GR340", locatário "Bruno Mendes Oliveira"
 * Arquivos fora desse padrão viram só o nome, sem locador nem código.
 */
export function descreverContrato(arquivo: string): InfoContrato {
  const base = arquivo
    .replace(/\.pdf$/i, '')
    .replace(/^Contrato_/i, '')
    .replace(/_final$/i, '');

  const [esquerda, direita] = base.split('_X_');
  if (!direita) {
    return { arquivo, locatario: base.replace(/_/g, ' '), locador: '', codigo: '' };
  }

  const partes = esquerda.split('_');
  const codigo = /^[A-Z]{2}\d+$/.test(partes[partes.length - 1]) ? partes.pop()! : '';

  return {
    arquivo,
    locatario: direita.replace(/_/g, ' '),
    locador: partes.join(' '),
    codigo
  };
}

export function linkContrato(arquivo: string): string {
  return `/contratos/${encodeURIComponent(arquivo)}`;
}

export interface Bloco {
  titulo: boolean;
  texto: string;
}

/**
 * O texto extraído do PDF mantém as quebras de linha da página.
 * Junta as linhas em parágrafos e separa títulos em caixa alta ("RESCISÃO", "FORO").
 */
export function reflow(texto: string): Bloco[] {
  const blocos: Bloco[] = [];
  let paragrafo = '';
  const linhas = texto.split('\n').map((l) => l.trim()).filter(Boolean);

  for (const linha of linhas) {
    const ehTitulo =
      linha.length <= 60 && linha === linha.toUpperCase() && /\p{Lu}/u.test(linha) && !/[.,;:]$/.test(linha);
    if (ehTitulo) {
      if (paragrafo) blocos.push({ titulo: false, texto: paragrafo });
      paragrafo = '';
      blocos.push({ titulo: true, texto: linha });
    } else {
      paragrafo = paragrafo ? `${paragrafo} ${linha}` : linha;
    }
  }
  if (paragrafo) blocos.push({ titulo: false, texto: paragrafo });
  return blocos;
}

/**
 * Chunks vizinhos compartilham até 50 caracteres (o chunk_overlap do processamento).
 * Remove do início do chunk atual o trecho que já apareceu no fim do anterior.
 */
export function removerSobreposicao(anterior: string, atual: string): string {
  for (let k = Math.min(80, anterior.length, atual.length); k >= 8; k--) {
    // Só aceita se o corte cair entre palavras, para não colar pedaços de palavras
    const fimDePalavra = k === atual.length || /\s/.test(atual[k]);
    if (fimDePalavra && anterior.endsWith(atual.slice(0, k))) return atual.slice(k);
  }
  return atual;
}

// Nomes reais (com acentos) a partir do texto do contrato: "LOCADOR: Altos Padrões Construções, ..."
export function partesDoTexto(texto: string): { locador?: string; locatario?: string } {
  const achar = (rotulo: string) => texto.match(new RegExp(`${rotulo}:\\s*([^,\\n]+)`))?.[1]?.trim();
  return { locador: achar('LOCADOR'), locatario: achar('LOCATÁRIO') };
}
