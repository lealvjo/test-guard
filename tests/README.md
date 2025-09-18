# Testes Unitários e de Integração - Test Guard

Este projeto inclui uma suíte completa de testes unitários e de integração para o backend.

## Estrutura dos Testes

```
tests/
├── conftest.py              # Configurações e fixtures do pytest
├── unit/                    # Testes unitários
│   ├── test_repositories.py # Testes para repositories
│   ├── test_services.py     # Testes para services
│   └── test_controllers.py  # Testes para controllers
├── integration/             # Testes de integração
│   └── test_endpoints.py    # Testes para endpoints
└── fixtures/                # Fixtures e dados de teste
```

## Dependências de Teste

As dependências necessárias estão listadas em `requirements-test.txt`:

- `pytest` - Framework de testes
- `pytest-flask` - Extensões para testes Flask
- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocking para testes
- `factory-boy` - Factory para criação de dados de teste
- `faker` - Geração de dados falsos

## Como Executar os Testes

### 1. Instalar Dependências

```bash
pip install -r requirements-test.txt
```

### 2. Executar Todos os Testes

```bash
python -m pytest
```

### 3. Executar Testes Específicos

```bash
# Apenas testes unitários
python -m pytest tests/unit/ -m unit

# Apenas testes de integração
python -m pytest tests/integration/ -m integration

# Com cobertura de código
python -m pytest --cov=. --cov-report=html

# Em modo verboso
python -m pytest -v
```

### 4. Usar o Script de Execução

```bash
# Executar todos os testes
python run_tests.py

# Executar apenas testes unitários
python run_tests.py --type unit

# Executar com cobertura
python run_tests.py --coverage

# Instalar dependências e executar
python run_tests.py --install --coverage
```

## Tipos de Testes

### Testes Unitários

Testam componentes individuais isoladamente usando mocks:

- **Repositories**: Testam operações de banco de dados
- **Services**: Testam lógica de negócio
- **Controllers**: Testam endpoints e validações

### Testes de Integração

Testam o fluxo completo entre componentes:

- **CRUD completo**: Criar, ler, atualizar e deletar
- **Validações**: Campos obrigatórios e regras de negócio
- **Paginação**: Funcionalidade de paginação
- **Busca**: Funcionalidade de busca e filtros
- **Fluxos cruzados**: Integração entre diferentes módulos

## Cobertura de Testes

Os testes cobrem:

- ✅ **Repositories**: 100% dos métodos principais
- ✅ **Services**: 100% dos métodos principais
- ✅ **Controllers**: 100% dos endpoints
- ✅ **Validações**: Todos os cenários de erro
- ✅ **Integração**: Fluxos completos entre módulos

## Fixtures Disponíveis

- `app`: Instância da aplicação Flask para testes
- `client`: Cliente de teste HTTP
- `temp_db`: Banco de dados temporário para testes
- `sample_automation_data`: Dados de exemplo para automações
- `sample_contract_data`: Dados de exemplo para contratos
- `sample_report_data`: Dados de exemplo para relatórios

## Marcadores de Teste

- `@pytest.mark.unit`: Marca testes unitários
- `@pytest.mark.integration`: Marca testes de integração
- `@pytest.mark.slow`: Marca testes lentos

## Configuração

O arquivo `pytest.ini` contém configurações específicas:

- Caminhos de teste
- Marcadores personalizados
- Configurações de cobertura
- Filtros de warnings

## Exemplos de Uso

### Executar Testes Específicos

```bash
# Testar apenas repositories
python -m pytest tests/unit/test_repositories.py

# Testar apenas um método específico
python -m pytest tests/unit/test_repositories.py::TestAutomationRepository::test_insert_automation

# Testar com filtro de nome
python -m pytest -k "test_insert"
```

### Debug de Testes

```bash
# Executar com output detalhado
python -m pytest -v -s

# Parar no primeiro erro
python -m pytest -x

# Executar apenas testes que falharam na última execução
python -m pytest --lf
```

## Relatórios

### Cobertura HTML

Após executar com `--cov-report=html`, o relatório estará disponível em:
`htmlcov/index.html`

### Relatório Terminal

O relatório de cobertura também é exibido no terminal mostrando:
- Linhas cobertas
- Linhas não cobertas
- Percentual de cobertura por arquivo

## Manutenção dos Testes

### Adicionando Novos Testes

1. **Testes Unitários**: Adicione em `tests/unit/`
2. **Testes de Integração**: Adicione em `tests/integration/`
3. **Use fixtures existentes** quando possível
4. **Siga o padrão de nomenclatura**: `test_<função>_<cenário>`

### Boas Práticas

- Use mocks para isolar componentes
- Teste cenários de sucesso e erro
- Mantenha testes independentes
- Use dados de teste realistas
- Documente casos de teste complexos

## Troubleshooting

### Problemas Comuns

1. **ImportError**: Verifique se está no diretório correto
2. **Database locked**: Certifique-se de que não há processos usando o banco
3. **Module not found**: Instale as dependências com `pip install -r requirements-test.txt`

### Logs de Debug

Para debug detalhado, adicione ao `pytest.ini`:

```ini
[tool:pytest]
log_cli = true
log_cli_level = DEBUG
```
