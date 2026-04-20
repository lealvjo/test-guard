# Utilitários Front-end

Este diretório concentra funções compartilhadas para evitar duplicação entre páginas e modais.

## Arquivos

- `json-utils.js`
  - `parseJsonText(text, options)`: faz parse seguro de JSON.
  - `formatJsonText(text, options)`: formata JSON com identação.
  - `options.allowComments = true`: permite limpar comentários antes do parse.

- `notifications.js`
  - `showToastNotification(message, type)`
  - `showToastNotification(title, message, type)`
  - Usa `#toastContainer` quando existir.
  - Faz fallback para toast flutuante no `body` quando `#toastContainer` não existir.

## Ordem recomendada de scripts

Quando a página depender desses utilitários, carregue primeiro:

1. `json-utils.js` (se usar parse/format compartilhado)
2. `notifications.js` (se usar toast compartilhado)
3. script da página/modal

## Objetivo

Manter os scripts menores, com comportamento consistente e manutenção mais simples.
