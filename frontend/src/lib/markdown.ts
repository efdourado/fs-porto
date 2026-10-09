import { marked } from 'marked';
import DOMPurify from 'dompurify';

/**
 * Converte o Markdown devolvido pelo LLM em HTML seguro.
 * O DOMPurify remove qualquer script ou atributo perigoso antes de o HTML ir para o {@html}.
 */
export function renderMarkdown(texto: string): string {
  const html = marked.parse(texto, { async: false, gfm: true, breaks: true });
  return DOMPurify.sanitize(html);
}
