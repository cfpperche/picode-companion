# PiCode Companion — Product studio

Página em português para explorar o protótipo PiCode Companion C.02, inspirada na navegação de produto do DayRing. Site estático, sem dependências de produção, preparado para Vercel.

## Conteúdo

- Modelo 3D C.02 original, 146 partes, 59.788 triângulos.
- Design, vista explodida com controle de separação, eletrônica e ficha técnica.
- Rotação por mouse, toque e teclado; vistas predefinidas, zoom e cotas.
- Seleção de componentes e simulação do obturador físico.
- Três estudos de acabamento, mantendo a geometria do protótipo.
- Contexto do produto, interações planejadas e etapas de desenvolvimento.
- Links reais para o repositório PiCode e para fabricantes.

## Estrutura

`public/index.html` é a página. `public/styles.css` contém o layout responsivo. `public/viewer.js` renderiza as malhas WebGL; `public/app.js` controla a interface. `public/assets/companion-c02.b64` contém o JSON de geometria codificado em gzip/base64. As posições usam milímetros e precisão de 0,01 mm no formato de visualização.

O modelo é um estudo de integração, sem liberação para fabricação. Não se apresentam funcionalidades planejadas como já implementadas. A tela não se conecta a agentes reais nem captura câmera, microfone ou dados pessoais.

## Publicação na Vercel

`vercel.json` aponta para `public/`; não é necessário instalar pacotes nem executar build. O projeto pode ser importado na Vercel com framework **Other**, output directory **public** e build command vazio. Para publicar com Vercel CLI autenticada, execute `vercel --prod` na raiz.

Para servir localmente: `python3 -m http.server 8080 --directory public`. O servidor HTTP é necessário para carregar a geometria; abrir o HTML por `file://` não funciona.

## Navegadores

WebGL 1 e DecompressionStream (gzip). Navegadores modernos que fornecem essas APIs. Erros de carregamento e indisponibilidade de WebGL são informados no palco. As demais informações da página permanecem em HTML.

## Referências

Veja `BENCHMARKS.md` para a pesquisa, decisões de adaptação e fontes. Nenhuma imagem, fonte, código ou marca dos benchmarks foi incorporada ao projeto.

## Publicação

- Site público: https://picode-companion-c02.vercel.app/
- Projeto: `picode-companion-c02`
- Implantação criada: `dpl_4x8E5AiXjUGavxpmfbzWYh4sduGE`
- Painel: https://vercel.com/cfpperches-projects/picode-companion-c02

A criação foi feita pelo conector Vercel com os arquivos completos, com target production. O domínio público foi confirmado via HTTP e o HTML servido corresponde exatamente ao arquivo local. Resultados de conferência estão em `http-verification.json`.

O alias técnico com sufixo de equipe exige login; use o domínio público acima para compartilhar. A API de consulta de status recusou o escopo da equipe, por isso a validação da publicação se baseia no conteúdo servido, sem afirmar um estado de build consultado via API.
