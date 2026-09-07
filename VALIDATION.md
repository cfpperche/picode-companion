# Validação

- JavaScript de interface e renderização: `node --check` aprovado.
- HTML: identificadores únicos, âncoras existentes e recursos locais resolvidos.
- Controles: todas as referências de elementos usadas pelos scripts existem no HTML.
- Arquivo do modelo: gzip/base64 decodificado e JSON válido com 146 partes.
- Configuração Vercel: JSON válido e diretório de publicação `public`.
- Renderizador derivado do visualizador C.02 existente, com controle por mouse, toque e teclado, presets, cotas, acabamento e separação de peças.
- Responsividade implementada para desktop, tablet e celular; a revisão desta página não incluiu teste visual automatizado em navegador.
- Publicação: criação aceita pela Vercel em production. Domínio público `https://picode-companion-c02.vercel.app/` respondendo com o HTML correto. Os resultados por recurso estão em `http-verification.json`.
- Consulta de status via API indisponível para o escopo da equipe; verificação realizada diretamente no domínio público. O alias técnico com sufixo de equipe exige login.


## Limites do produto

O site explora um conceito de hardware. Não executa agentes, não abre câmera nem microfone, não coleta cadastros e não constitui especificação final de fabricação.
