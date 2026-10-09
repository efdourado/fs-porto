# 04 · Frontend

Aplicação **SvelteKit** (Svelte 4) com **Tailwind CSS**, em `frontend/`. Roda com Vite na porta 5173. O visual é minimalista, no estilo Apple: fonte do sistema, cinzas neutros, um único azul de destaque e modo escuro automático (segue a configuração do sistema).

## Conceitos rápidos

- **Svelte** compila componentes `.svelte` (HTML + `<script>` + `<style>` no mesmo arquivo) para JavaScript puro. Variáveis comuns são reativas: mudar `x = 1` atualiza a tela.
  - `$: y = f(x)` é uma **declaração reativa**: recalcula sempre que `x` muda.
  - `bind:value={x}` liga um input a uma variável nos dois sentidos.
  - `export let x` declara uma **prop** (parâmetro que o componente pai passa).
  - `{#if}`, `{#each}`, `{@html}` são a sintaxe de template; `in:fade`, `in:fly` são transições.
  - `$page` (de `$app/stores`) é um *store* com a URL atual; o `$` na frente lê o valor e reage a mudanças.
- **SvelteKit** adiciona roteamento por pastas: `src/routes/contratos/+page.svelte` vira `/contratos`. Uma pasta entre colchetes (`[arquivo]`) é um **parâmetro**: `/contratos/qualquer-coisa` cai nela, com `$page.params.arquivo = "qualquer-coisa"`. `+layout.svelte` envolve todas as páginas.
- **Tailwind** são classes utilitárias (`flex`, `mt-4`, `rounded-2xl`). As cores do projeto (`bg-surface`, `text-muted`, `text-accent`...) são definidas em `tailwind.config.js` a partir de variáveis CSS.

## Estrutura

```
frontend/
├── src/
│   ├── app.html                       # HTML base: título, favicon, fonte Inter
│   ├── app.css                        # paleta (claro/escuro), estilos base e do Markdown
│   ├── routes/
│   │   ├── +layout.ts                 # ssr = false (o app roda só no navegador)
│   │   ├── +layout.svelte             # cabeçalho + barra de abas no celular
│   │   ├── +page.svelte               # /                  buscar e perguntar
│   │   └── contratos/
│   │       ├── +page.svelte           # /contratos         biblioteca + upload
│   │       └── [arquivo]/+page.svelte # /contratos/<pdf>   leitura de um contrato
│   └── lib/
│       ├── contratos.ts               # nome do arquivo → nomes legíveis; reflow do texto
│       ├── markdown.ts                # Markdown do LLM → HTML seguro
│       ├── services/
│       │   ├── api.ts                 # API de busca :8000
│       │   └── upload-api.ts          # API de upload :8001
│       └── components/
│           ├── SearchField.svelte     # controle Buscar/Perguntar + campo
│           ├── ResultCard.svelte      # um trecho encontrado na busca
│           ├── Answer.svelte          # resposta do LLM + fontes
│           ├── Avatar.svelte          # imagem redonda dos contratos
│           └── Icon.svelte            # ícones SVG
├── static/                            # logo, favicon, avatar (servidos na raiz: /logo.png)
├── tailwind.config.js                 # fontes, cores, animações
└── package.json
```

`$lib` é um atalho do SvelteKit para `src/lib`.

---

## Design: `app.css` e `tailwind.config.js`

A paleta mora em **variáveis CSS** no `:root`, com valores RGB:

```css
:root { --bg: 255 255 255; --surface: 245 245 247; --ink: 29 29 31; --accent: 0 113 227; ... }
@media (prefers-color-scheme: dark) {
  :root { --bg: 0 0 0; --surface: 28 28 30; --ink: 245 245 247; --accent: 41 151 255; ... }
}
```

O `tailwind.config.js` transforma cada uma em uma cor (`surface: 'rgb(var(--surface) / <alpha-value>)'`). Resultado:

- `bg-surface`, `text-muted`, `text-accent` funcionam em qualquer componente;
- opacidade funciona (`bg-accent/10` = azul a 10%);
- o **modo escuro não exige nenhuma classe `dark:`**: o navegador troca as variáveis e tudo muda junto.

| Token | Uso |
|---|---|
| `bg` | Fundo da página |
| `surface` | Cartões, campos, listas (o cinza claro da Apple, `#f5f5f7`) |
| `elevated` | Elemento sobre `surface` (botão ativo do controle segmentado) |
| `ink` / `muted` | Texto principal / secundário |
| `line` | Bordas finas (já inclui opacidade, por isso é definida à parte em `app.css`) |
| `accent` | Azul de ação |
| `danger` | Erros |

`app.css` também define `.skeleton` (placeholder animado de carregamento) e `.markdown` (tipografia das respostas do LLM).

---

## `src/routes/+layout.svelte` e `+layout.ts`

- **Cabeçalho:** fixo no topo, translúcido (`bg-bg/75 backdrop-blur-xl`): o conteúdo aparece borrado por trás ao rolar. Logo + "Porto" à esquerda; links "Buscar" e "Contratos" à direita (só a partir de `sm`, 640 px).
- **Barra de abas (celular):** abaixo de 640 px os links vão para uma barra fixa embaixo, com ícones, no estilo iOS. `env(safe-area-inset-bottom)` evita a barra de gestos do iPhone.
- **Link ativo:** `ativo(href)` compara com `$page.url.pathname`; `/contratos/x` também marca "Contratos".
- **`+layout.ts`** exporta `ssr = false`: o SvelteKit não renderiza no servidor. Todas as páginas dependem de chamadas à API feitas no navegador, então renderizar no servidor só duplicaria as chamadas.

## `src/routes/+page.svelte` (`/`)

A tela principal: buscar e perguntar.

**A URL é a fonte da verdade.** Enviar uma consulta faz `goto('/?q=...&modo=perguntar')`, e um bloco reativo lê a URL e executa:

```ts
$: consulta = $page.url.searchParams.get('q')?.trim() ?? '';
$: modoUrl = $page.url.searchParams.get('modo') === 'perguntar' ? 'perguntar' : 'buscar';
$: executar(consulta, modoUrl);
```

Vantagens: o botão voltar do navegador funciona, dá para compartilhar o link de uma busca, e recarregar a página refaz a consulta.

**Estados:** `vazio` (título grande e sugestões) → `carregando` (esqueletos) → `pronto` ou `erro`. A variável `chaveAtual` descarta respostas antigas: se você fizer uma segunda pergunta antes de a primeira voltar, a primeira é ignorada quando chegar.

- Modo **Buscar** → `buscarContratos` (8 resultados) → um `ResultCard` por trecho.
- Modo **Perguntar** → `askQuestion` (5 trechos de contexto, timeout de 60 s) → `Answer`.

As sugestões de cada modo foram escolhidas porque funcionam bem com os contratos de exemplo.

## `src/routes/contratos/+page.svelte` (`/contratos`)

A biblioteca. Chama `listarArquivos()` (12 nomes) e transforma cada nome com `descreverContrato` em locatário, locador e código. Mostra uma lista agrupada (estilo Ajustes do iOS), ordenada por nome.

- **Filtro:** filtra na hora, no navegador, ignorando acentos e maiúsculas (`normalize('NFD')` separa as letras dos acentos, que são então removidos).
- **Adicionar:** abre o seletor de arquivo e envia o PDF com `uploadService.enviarContrato`. A API responde **antes** de terminar de indexar (veja `BackgroundTasks` em [03 · Backend](03-backend.md)), então a página consulta `listarArquivos()` a cada 3 s até o novo arquivo aparecer (no máximo 2 minutos).

## `src/routes/contratos/[arquivo]/+page.svelte`

Um contrato. Busca todos os chunks (`listarTrechos`) e oferece duas visões:

- **Documento:** os chunks reunidos num texto contínuo e legível. A junção devolve a quebra de linha que o splitter descartou no corte, usa `removerSobreposicao` (tira a repetição do `chunk_overlap`) e `reflow` (junta as linhas quebradas do PDF em parágrafos e separa títulos em caixa alta).
- **Trechos:** os chunks crus, numerados, com o tamanho em caracteres: exatamente o que está no Pinecone. Útil para entender a indexação.

Os nomes com acento (o arquivo diz "Altos Padroes Construcoes") vêm do próprio texto, com `partesDoTexto`, que procura `LOCADOR:` e `LOCATÁRIO:`.

---

## `src/lib`

### `services/api.ts`

Cliente axios da API de busca (`http://127.0.0.1:8000`, fixo no código).

| Função | Chama | Usada em |
|---|---|---|
| `listarContratos(skip, limit)` | `GET /contratos` | `listarTrechos` |
| `listarTrechos(arquivo)` | `GET /contratos?limit=10000` e filtra | página do contrato |
| `buscarContratos(query, limit=8)` | `GET /contratos/busca` | `/` modo Buscar |
| `listarArquivos()` | `GET /contratos/arquivos` | `/contratos` |
| `askQuestion(question, maxResults=5)` | `POST /llm/ask` | `/` modo Perguntar |

`mensagemDeErro` converte falhas em mensagens legíveis: o `detail` do FastAPI quando existe, ou "a API está rodando na porta 8000?" quando não há resposta.

> `listarTrechos` baixa **todos** os chunks para filtrar um contrato. Com 132 chunks é instantâneo; com milhares, o certo seria um endpoint no backend usando `index.list(prefix=...)`. Bom exercício.

### `services/upload-api.ts`

`enviarContrato(arquivo)` monta um `FormData` com o campo `file` e faz `POST /upload/contrato`. Não define `Content-Type`: com `FormData`, o navegador gera `multipart/form-data` com o *boundary* correto sozinho.

### `contratos.ts`

| Função | O que faz |
|---|---|
| `descreverContrato(arquivo)` | `Contrato_Altos_Padroes_Construcoes_GR340_X_Bruno_Mendes_Oliveira.pdf` → `{ locador: "Altos Padroes Construcoes", codigo: "GR340", locatario: "Bruno Mendes Oliveira" }` |
| `linkContrato(arquivo)` | URL da página do contrato (com `encodeURIComponent`) |
| `reflow(texto)` | Linhas do PDF → blocos `{ titulo, texto }` |
| `removerSobreposicao(anterior, atual)` | Corta do início de `atual` o que já está no fim de `anterior`, só em limite de palavra |
| `partesDoTexto(texto)` | Extrai locador e locatário do texto do contrato |

### `markdown.ts`

`renderMarkdown(texto)`: o LLM responde em Markdown (`**negrito**`, listas, tabelas). `marked` converte para HTML e `DOMPurify` remove qualquer `<script>` ou atributo perigoso antes de o HTML ir para o `{@html}`. Sem o DOMPurify, um texto malicioso dentro de um contrato poderia induzir o LLM a devolver HTML que roda no seu navegador.

### Componentes

| Componente | Props | O que faz |
|---|---|---|
| `SearchField` | `value`, `modo` (ambos com `bind:`), `carregando` | Controle segmentado Buscar/Perguntar + campo com botão de enviar (some quando o campo está vazio). Dispara `submit` e `modo` |
| `ResultCard` | `resultado` | Avatar, locatário, locador, score (similaridade de cosseno) e o trecho com os títulos como rótulos |
| `Answer` | `resposta` | Markdown renderizado + "Trechos consultados" (contratos únicos, com link) |
| `Avatar` | `size` | A imagem `static/avatar.jpg` redonda |
| `Icon` | `name`, `size`, `stroke` | Ícones SVG em traço fino: `search`, `brain`, `doc`, `plus`, `chevron-left/right`, `arrow-up`, `x` |

---

## Comandos

```bash
npm run dev      # servidor de desenvolvimento (hot reload)
npm run check    # checagem de tipos (svelte-check)
npm run build    # build de produção
```
