# 04 · Frontend

Aplicação **SvelteKit** (Svelte 4) com **Tailwind CSS** e **DaisyUI**, em `frontend/`. Roda em modo desenvolvimento com Vite na porta 5173.

## Conceitos rápidos

- **Svelte** compila componentes `.svelte` (HTML + `<script>` + `<style>` no mesmo arquivo) para JavaScript puro. Variáveis comuns são reativas: mudar `x = 1` atualiza a tela.
  - `$: { ... }` é um **bloco reativo**: roda de novo sempre que uma variável usada dentro dele muda.
  - `bind:value={x}` liga um input a uma variável nos dois sentidos.
  - `export let x` declara uma **prop** (parâmetro que o componente pai passa).
  - `{#if}`, `{#each}`, `{@html}` são a sintaxe de template.
- **SvelteKit** adiciona roteamento por pastas: `src/routes/contratos/+page.svelte` vira a URL `/contratos`. `+layout.svelte` envolve todas as páginas.
- **Tailwind** são classes utilitárias (`flex`, `mb-4`, `text-xl`). **DaisyUI** adiciona componentes prontos por classe (`btn`, `card`, `navbar`, `toggle`, `alert`) e temas.

## Estrutura

```
frontend/
├── src/
│   ├── app.html                 # HTML base (lang="pt-BR")
│   ├── app.css                  # só as 3 diretivas do Tailwind
│   ├── routes/
│   │   ├── +layout.svelte       # cabeçalho, menu, tema; envolve todas as páginas
│   │   ├── +page.svelte         # /          página inicial
│   │   ├── contratos/+page.svelte  # /contratos  listagem, busca e modo pergunta
│   │   └── sobre/+page.svelte   # /sobre     texto institucional
│   └── lib/
│       ├── services/
│       │   ├── api.ts           # cliente da API :8000 (axios)
│       │   └── upload-api.ts    # cliente da API :8001 (não usado)
│       └── components/
│           ├── SearchBar.svelte
│           ├── ContratoCard.svelte
│           └── ApiTest.svelte   # não usado
├── tailwind.config.js           # cores, animações e temas DaisyUI
├── vite.config.js               # proxy /api e /upload-api (não usado)
├── svelte.config.js             # adapter-auto
└── package.json
```

`$lib` é um atalho do SvelteKit para `src/lib`.

---

## `src/lib/services/api.ts`

O único ponto de contato do frontend com o backend. Cria uma instância do **axios** com `baseURL: 'http://127.0.0.1:8000'` (fixa no código) e timeout de 10 s.

| Função | Chama | Usada em |
|---|---|---|
| `listarContratos(skip, limit)` | `GET /contratos` | `/contratos` sem busca |
| `buscarContratos(query, limit=5)` | `GET /contratos/busca` | `/contratos` com busca |
| `listarArquivos()` | `GET /contratos/arquivos` | nenhum lugar |
| `askQuestion(question, maxResults=3)` | `POST /llm/ask` (timeout 30 s) | `/contratos` no modo pergunta |

Também exporta as interfaces TypeScript `Contrato`, `SearchResponse` e `LLMResponse`, que espelham os modelos Pydantic do backend.

> O arquivo importa `env` de `$env/dynamic/public`, mas não usa: as URLs estão fixas no código. Trocar de porta exige editar este arquivo.

## `src/lib/services/upload-api.ts`

Cria um axios para `http://localhost:8001` com `Content-Type: multipart/form-data`. **Nenhum componente importa este arquivo**: a tela de upload nunca foi construída.

---

## `src/routes/+layout.svelte`

Envolve todas as páginas (`<slot />` é onde a página entra).

- **Cabeçalho:** `navbar` do DaisyUI com gradiente, logo "ContratusAI", links Início / Contratos / Sobre e, em telas pequenas, um menu dropdown.
- **Tema claro/escuro:** um store `currentTheme`; `toggleTheme()` alterna entre `contratuslight` e `contratusdark`, salva no `localStorage` e aplica com o atributo `data-theme` no `<html>` (é assim que o DaisyUI troca de tema). Os dois temas são definidos em `tailwind.config.js`.

> O `checked` do botão de tema compara com `'britodark'`, um tema que não existe (resquício do nome antigo do projeto). Resultado: o ícone pode não refletir o tema salvo ao recarregar.

## `src/routes/+page.svelte` (`/`)

Página inicial de apresentação: hero com título e `SearchBar`, uma ilustração, três cards de recursos e uma chamada para "Ver Contratos". Animações com `svelte/transition` (`fade`, `fly`) disparadas por `isVisible` 100 ms após montar.

Ao buscar, faz `goto('/contratos?q=...')`. O modo pergunta não está disponível aqui; a página `/contratos` sempre abre com ele desligado.

## `src/routes/contratos/+page.svelte` (`/contratos`)

A página que realmente usa o backend.

**Estado:** `searchQuery`, `isLoading`, `error`, `resultados`, `total`, `currentPage`, `itemsPerPage = 10`, `useLLM` (o toggle "Modo Pergunta") e `llmResponse`.

**Fluxo:**

1. Um bloco reativo `$:` lê `?q=` da URL. Com `q`, chama `performSearch`; sem `q`, chama `loadContratos`. (O `onMount` também chama `loadContratos`, então a lista é buscada duas vezes ao abrir.)
2. `loadContratos(page)` → `listarContratos(skip, 10)`. Mostra paginação se `total > 10`.
3. `performSearch(query)`:
   - modo normal → `buscarContratos` → um `ContratoCard` por chunk, com o score em %;
   - modo pergunta → `askQuestion` → mostra `answer` num balão (`chat-bubble`) com a lista de fontes. A resposta é inserida com `{@html}`, trocando `\n` por `<br>`. O Markdown que o LLM devolve (`**negrito**`, listas) aparece cru.
4. `handleSearch` atualiza a URL com `history.pushState` e busca.

> A listagem mostra **chunks**, não contratos: "Mostrando 1–10 de 132 contratos" são 132 pedaços de 12 contratos.

## `src/routes/sobre/+page.svelte` (`/sobre`)

Página estática: descrição do produto, tecnologias e "Como Funciona" (Upload, Indexação, Consulta, Resultados).

---

## Componentes

### `SearchBar.svelte`

Props: `placeholder`, `value` (com `bind:`). Um `<form>` com input e botão "Buscar". No submit (`on:submit|preventDefault`, que evita recarregar a página), dispara o evento `search` com o texto, via `createEventDispatcher`. Quem usa escuta com `on:search={...}`.

### `ContratoCard.svelte`

Props: `contrato` (`{ arquivo, texto, score? }`) e `expanded`. Mostra o nome do arquivo, um badge `NN% relevante` (score × 100) e o texto cortado em 200 caracteres, com botão "Mostrar mais/menos".

### `ApiTest.svelte`

Chama `GET /` ao montar e mostra o status da API e do Pinecone com badges. **Não é usado em nenhuma página.**

---

## Configuração

- **`tailwind.config.js`:** onde o Tailwind procura classes (`content`), a fonte Inter, as animações `gradient` e `fade-in`, o plugin DaisyUI e os temas `contratuslight` e `contratusdark` (cores `primary`, `secondary`, `base-100`...). É o arquivo central para mudar a cara do app.
- **`vite.config.js`:** define proxies `/api → :8000` e `/upload-api → :8001`. Como `api.ts` usa a URL completa, os proxies não são usados.
- **`svelte.config.js`:** `adapter-auto` (escolhe o adaptador de deploy automaticamente) e `vitePreprocess` (permite TypeScript nos componentes).
- **`postcss.config.js`:** liga Tailwind e Autoprefixer ao pipeline de CSS.

## Comandos

```bash
npm run dev      # servidor de desenvolvimento (hot reload)
npm run build    # build de produção
npm run check    # checagem de tipos (svelte-check)
```
