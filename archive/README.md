# Archive - Arquivos não utilizados

Esta pasta contém arquivos que foram substituídos durante a refatoração mas mantidos para histórico e segurança.

## Arquivos movidos:

### Templates de Backup:
- `automations_list_bck.html` - Backup do template de listagem de automações (versão original funcionando)
- `schema_generator_bck.html` - Backup do template do gerador de schema (versão original funcionando)

### Arquivos Temporários:
- `less_help_temporary.txt` - Output temporário do comando `less` (help)
- `less_help_temporary2.txt` - Output temporário do comando `less` (help)
- `git_log_output.txt` - Output do comando `git log --name-only`

## Motivo da movimentação:
Durante a refatoração do sistema para usar `base.html` e arquivos estáticos organizados, os arquivos originais foram substituídos por versões refatoradas. Os backups foram mantidos para:
- Histórico de desenvolvimento
- Possível rollback se necessário
- Referência para futuras melhorias

## Data da refatoração:
Setembro 2025 - Refatoração completa do sistema para arquitetura modular
