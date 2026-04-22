# Contexto de Continuidade (Cursor/AI)

Este arquivo resume o estado atual do projeto para retomar o trabalho em outra máquina sem perder o contexto.

## Visão Geral

- Projeto: `test-guard`
- Stack principal: Flask + templates + JavaScript modular em `static/js`.
- Objetivo recente: refatoração incremental do front para estrutura modular, mantendo comportamento.
- Status de estabilidade: suíte de testes verde durante as mudanças (`pytest` com 123 testes passando).

## Padrões Definidos

- Responder e trabalhar em português.
- Evitar JavaScript inline em templates.
- Estrutura de modal no `templates` e lógica no `static/js/modals`.
- Reuso de utilitários em `static/js/utils` (evitar duplicação).
- Refatoração incremental (mudanças pequenas e verificáveis).
- Erros de validação de entrada devem ser `400` (não `500`).
- Após mudanças relevantes: rodar `pytest` e lint dos arquivos alterados.

## Regra do Cursor Versionada

Foi criada a regra:

- `.cursor/rules/project-standards.mdc`

Ela aplica automaticamente os padrões acima em qualquer máquina que abrir este repo no Cursor.

## Refatorações Front-end Já Concluídas

### Extração de scripts inline para arquivos JS

- `templates/contracts_list.html` -> `static/js/pages/contracts-list.js`
- `templates/register_automation.html` -> `static/js/pages/register-automation.js`
- `templates/schema_generator.html` -> `static/js/pages/schema-generator.js`
- `templates/automations_list.html` -> `static/js/pages/automations-list.js`
- `templates/index.html` -> `static/js/pages/index.js`
- `templates/execution_dashboard.html` -> `static/js/pages/execution-dashboard.js`
- `templates/contracts_dashboard.html` -> `static/js/pages/contracts-dashboard.js`
- `templates/register_contract.html` -> `static/js/pages/register-contract.js`
- `templates/validation_modal.html` -> `static/js/modals/validation-modal.js`
- `templates/junit_report.html` -> `static/js/pages/junit-report.js`

### Modais modularizadas

- `static/js/modals/add-contract-modal.js`
- `static/js/modals/edit-contract-modal.js`
- `static/js/modals/validation-modal.js`
- `static/js/modals/history-modal.js`
- `static/js/modals/curl-modal.js`
- `static/js/modals/automation-report-docs-modal.js`

### Padronização de modais para templates

- cURL:
  - criada `templates/curl_modal.html`
  - `validation_modal.html` inclui `curl_modal.html`
  - removido `static/curl_modal.html` (não usado)
- Histórico:
  - criada `templates/history_modal.html`
  - `validation_modal.html` inclui `history_modal.html`

## Utilitários Compartilhados

- `static/js/utils/notifications.js`
  - função: `showToastNotification(...)`
  - suporta formato curto (`mensagem`, `tipo`) e longo (`titulo`, `mensagem`, `tipo`)
- `static/js/utils/json-utils.js`
  - `parseJsonText(...)`
  - `formatJsonText(...)`
- `static/js/utils/README.md` com instruções de uso e ordem de carregamento.

## Melhorias de Documentação API no Front

### Modal de validação de contratos

- Modal de docs API agora mostra:
  - exemplos de request por linguagem (Python/JS/TS/Java/.NET/cURL)
  - exemplos de retorno:
    - sucesso (`200`)
    - erro de validação (`400`)

### Tela de automações cadastradas

- Adicionado botão discreto por card (`📘`) para abrir documentação API da automação.
- Nova modal para "Gerar relatórios para esta automação" com:
  - exemplos de request para `POST /report` por linguagem
  - exemplos de retorno:
    - sucesso (`201`)
    - erro de validação (`400`)
    - não encontrado (`404`)

## Arquivos-Chave Alterados Recentemente

- `templates/validation_modal.html`
- `templates/automations_list.html`
- `templates/contracts_list.html`
- `templates/register_automation.html`
- `templates/register_contract.html`
- `templates/curl_modal.html`
- `templates/history_modal.html`
- `static/js/modals/validation-modal.js`
- `static/js/modals/curl-modal.js`
- `static/js/modals/history-modal.js`
- `static/js/modals/add-contract-modal.js`
- `static/js/modals/edit-contract-modal.js`
- `static/js/modals/automation-report-docs-modal.js`
- `static/js/pages/automations-list.js`
- `static/js/pages/register-automation.js`
- `static/js/pages/register-contract.js`
- `static/js/utils/notifications.js`
- `static/js/utils/json-utils.js`
- `.cursor/rules/project-standards.mdc`

## Como Retomar em Outra Máquina

1. Dar `git pull`.
2. Abrir o projeto no Cursor.
3. Abrir este arquivo (`docs/ai-context.md`) e `.cursor/rules/project-standards.mdc`.
4. Iniciar o chat com algo como:
   - "Continue a partir do contexto em `docs/ai-context.md`, mantendo os padrões do `.cursor/rules/project-standards.mdc`."

