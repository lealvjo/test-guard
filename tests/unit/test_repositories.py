import pytest
import json
import sqlite3
from unittest.mock import patch, MagicMock
from repository.automation_repository import AutomationRepository
from repository.contract_repository import ContractRepository
from repository.report_repository import ReportRepository


class TestAutomationRepository:
    """Testes unitários para AutomationRepository"""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Cria uma instância do repository com banco temporário"""
        return AutomationRepository(temp_db)
    
    def test_create_table(self, repo):
        """Testa a criação da tabela automations"""
        # Verifica se a tabela foi criada
        conn = sqlite3.connect(repo.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='automations'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'automations'
    
    def test_insert_automation(self, repo, sample_automation_data):
        """Testa a inserção de uma automação"""
        data = sample_automation_data
        
        repo.insert_automation(
            data['name'],
            data['squad'],
            data['type'],
            data['description'],
            data['language'],
            data['cucumber'],
            data['launch_date'],
            data['git'],
            data['image_base64']
        )
        
        # Verifica se a automação foi inserida
        automations = repo.get_all_automations()
        assert len(automations) == 1
        assert automations[0]['name'] == data['name']
        assert automations[0]['squad'] == data['squad']
        assert automations[0]['description'] == data['description']
        assert automations[0]['language'] == data['language']
        assert automations[0]['cucumber'] == data['cucumber']
        assert automations[0]['launch_date'] == data['launch_date']
        assert automations[0]['git'] == data['git']
        assert automations[0]['image_base64'] == data['image_base64']
    
    def test_get_all_automations(self, repo, sample_automation_data):
        """Testa a busca de todas as automações"""
        # Insere algumas automações
        for i in range(3):
            data = sample_automation_data.copy()
            data['name'] = f"Automation {i}"
            repo.insert_automation(
                data['name'],
                data['squad'],
                data['type'],
                data['description'],
                data['language'],
                data['cucumber'],
                data['launch_date'],
                data['git'],
                data['image_base64']
            )
        
        automations = repo.get_all_automations()
        assert len(automations) == 3
        assert all(automation['name'].startswith('Automation') for automation in automations)
    
    def test_get_paginated_automations(self, repo, sample_automation_data):
        """Testa a paginação de automações"""
        # Insere 5 automações
        for i in range(5):
            data = sample_automation_data.copy()
            data['name'] = f"Automation {i}"
            repo.insert_automation(
                data['name'],
                data['squad'],
                data['type'],
                data['description'],
                data['language'],
                data['cucumber'],
                data['launch_date'],
                data['git'],
                data['image_base64']
            )
        
        # Testa primeira página
        automations, total = repo.get_paginated_automations(1, 2)
        assert len(automations) == 2
        assert total == 5
        
        # Testa segunda página
        automations, total = repo.get_paginated_automations(2, 2)
        assert len(automations) == 2
        assert total == 5
        
        # Testa terceira página
        automations, total = repo.get_paginated_automations(3, 2)
        assert len(automations) == 1
        assert total == 5
    
    def test_get_automations_by_search(self, repo, sample_automation_data):
        """Testa a busca de automações por termo"""
        # Insere automações com nomes diferentes
        test_names = ["Python Test", "Java Test", "JavaScript Test", "Python Automation"]
        for name in test_names:
            data = sample_automation_data.copy()
            data['name'] = name
            repo.insert_automation(
                data['name'],
                data['squad'],
                data['type'],
                data['description'],
                data['language'],
                data['cucumber'],
                data['launch_date'],
                data['git'],
                data['image_base64']
            )
        
        # Busca por "Python"
        automations, total = repo.get_automations_by_search("Python", 1, 10)
        assert total == 2
        assert len(automations) == 2
        assert all("Python" in automation['name'] for automation in automations)
    
    def test_delete_automation(self, repo, sample_automation_data):
        """Testa a exclusão de uma automação"""
        # Insere uma automação
        repo.insert_automation(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            sample_automation_data['type'],
            sample_automation_data['description'],
            sample_automation_data['language'],
            sample_automation_data['cucumber'],
            sample_automation_data['launch_date'],
            sample_automation_data['git'],
            sample_automation_data['image_base64']
        )
        
        # Verifica se foi inserida
        automations = repo.get_all_automations()
        assert len(automations) == 1
        
        # Deleta a automação
        result = repo.delete_automation(1)
        assert result is True
        
        # Verifica se foi deletada
        automations = repo.get_all_automations()
        assert len(automations) == 0
    
    def test_delete_automation_not_found(self, repo):
        """Testa a exclusão de uma automação inexistente"""
        result = repo.delete_automation(999)
        assert result is False
    
    def test_get_automation_by_id(self, repo, sample_automation_data):
        """Testa a busca de automação por ID"""
        # Insere uma automação
        repo.insert_automation(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            sample_automation_data['type'],
            sample_automation_data['description'],
            sample_automation_data['language'],
            sample_automation_data['cucumber'],
            sample_automation_data['launch_date'],
            sample_automation_data['git'],
            sample_automation_data['image_base64']
        )
        
        # Busca por ID
        automation = repo.get_automation_by_id(1)
        assert automation is not None
        assert automation['name'] == sample_automation_data['name']
        assert automation['id'] == 1
    
    def test_get_automation_by_id_not_found(self, repo):
        """Testa a busca de automação por ID inexistente"""
        automation = repo.get_automation_by_id(999)
        assert automation is None
    
    def test_get_automation_by_name(self, repo, sample_automation_data):
        """Testa a busca de automação por nome"""
        # Insere uma automação
        repo.insert_automation(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            sample_automation_data['type'],
            sample_automation_data['description'],
            sample_automation_data['language'],
            sample_automation_data['cucumber'],
            sample_automation_data['launch_date'],
            sample_automation_data['git'],
            sample_automation_data['image_base64']
        )
        
        # Busca por nome
        automation = repo.get_automation_by_name(sample_automation_data['name'])
        assert automation is not None
        assert automation['name'] == sample_automation_data['name']
    
    def test_get_automation_by_name_not_found(self, repo):
        """Testa a busca de automação por nome inexistente"""
        automation = repo.get_automation_by_name("NonExistent")
        assert automation is None
    
    def test_check_duplicate_automation(self, repo, sample_automation_data):
        """Testa a verificação de automação duplicada"""
        # Insere uma automação
        repo.insert_automation(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            sample_automation_data['type'],
            sample_automation_data['description'],
            sample_automation_data['language'],
            sample_automation_data['cucumber'],
            sample_automation_data['launch_date'],
            sample_automation_data['git'],
            sample_automation_data['image_base64']
        )
        
        # Verifica duplicata com mesmo nome, squad e git
        duplicate = repo.check_duplicate_automation(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            sample_automation_data['git']
        )
        assert duplicate is not None
        assert duplicate['name'] == sample_automation_data['name']
        
        # Verifica que não é duplicata com git diferente
        not_duplicate = repo.check_duplicate_automation(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            "https://github.com/different/repo"
        )
        assert not_duplicate is None


class TestContractRepository:
    """Testes unitários para ContractRepository"""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Cria uma instância do repository com banco temporário"""
        return ContractRepository(temp_db)
    
    def test_create_table(self, repo):
        """Testa a criação da tabela contracts"""
        # Verifica se a tabela foi criada
        conn = sqlite3.connect(repo.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contracts'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'contracts'
    
    def test_insert_contract(self, repo, sample_contract_data):
        """Testa a inserção de um contrato"""
        data = sample_contract_data
        
        repo.insert_contract(data['name'], data['squad'], data['schemas'], data['repository_url'])
        
        # Verifica se o contrato foi inserido
        contracts = repo.get_all_contracts()
        assert len(contracts) == 1
        assert contracts[0]['name'] == data['name']
        assert contracts[0]['squad'] == data['squad']
        assert contracts[0]['schemas'] == data['schemas']
    
    def test_get_all_contracts(self, repo, sample_contract_data):
        """Testa a busca de todos os contratos"""
        # Insere alguns contratos
        for i in range(3):
            data = sample_contract_data.copy()
            data['name'] = f"Contract {i}"
            repo.insert_contract(data['name'], data['squad'], data['schemas'], data['repository_url'])
        
        contracts = repo.get_all_contracts()
        assert len(contracts) == 3
        assert all(contract['name'].startswith('Contract') for contract in contracts)
    
    def test_get_paginated_contracts(self, repo, sample_contract_data):
        """Testa a paginação de contratos"""
        # Insere 5 contratos
        for i in range(5):
            data = sample_contract_data.copy()
            data['name'] = f"Contract {i}"
            repo.insert_contract(data['name'], data['squad'], data['schemas'], data['repository_url'])
        
        # Testa primeira página
        contracts, total = repo.get_paginated_contracts(1, 2)
        assert len(contracts) == 2
        assert total == 5
        
        # Testa segunda página
        contracts, total = repo.get_paginated_contracts(2, 2)
        assert len(contracts) == 2
        assert total == 5
    
    def test_get_contracts_by_search(self, repo, sample_contract_data):
        """Testa a busca de contratos por termo"""
        # Insere contratos com nomes diferentes
        test_names = ["User Contract", "Order Contract", "Payment Contract", "User Service"]
        for name in test_names:
            data = sample_contract_data.copy()
            data['name'] = name
            repo.insert_contract(data['name'], data['squad'], data['schemas'], data['repository_url'])
        
        # Busca por "User"
        contracts, total = repo.get_contracts_by_search("User", 1, 10)
        assert total == 2
        assert len(contracts) == 2
        assert all("User" in contract['name'] for contract in contracts)
    
    def test_get_contract_by_id(self, repo, sample_contract_data):
        """Testa a busca de contrato por ID"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Busca por ID
        contract = repo.get_contract_by_id(1)
        assert contract is not None
        assert contract['name'] == sample_contract_data['name']
        assert contract['id'] == 1
    
    def test_get_contract_by_id_not_found(self, repo):
        """Testa a busca de contrato por ID inexistente"""
        contract = repo.get_contract_by_id(999)
        assert contract is None
    
    def test_get_contracts_by_squad(self, repo, sample_contract_data):
        """Testa a busca paginada de contratos por squad"""
        # Insere contratos de squads diferentes
        squads = ["Squad A", "Squad B", "Squad A"]
        for i, squad in enumerate(squads):
            data = sample_contract_data.copy()
            data['name'] = f"Contract {i}"
            data['squad'] = squad
            repo.insert_contract(data['name'], data['squad'], data['schemas'], data['repository_url'])
        
        # Busca por "Squad A"
        contracts, total = repo.get_contracts_by_squad_paginated("Squad A", 1, 10)
        assert len(contracts) == 2
        assert total == 2
        assert all(contract['squad'] == "Squad A" for contract in contracts)
    
    def test_delete_contract(self, repo, sample_contract_data):
        """Valida ausência de método delete direto no repository."""
        assert not hasattr(repo, 'delete_contract')
    
    def test_search_contracts_by_name_and_contract(self, repo, sample_contract_data):
        """Testa a busca de contratos por nome e contrato específico"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Busca por nome e contrato específico
        result = repo.search_contracts_by_name_and_contract(
            sample_contract_data['name'],
            'UserContract'
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == sample_contract_data['name']
    
    def test_search_contracts_by_name_and_contract_not_found(self, repo):
        """Testa a busca de contratos por nome e contrato inexistentes"""
        result = repo.search_contracts_by_name_and_contract("NonExistent", "NonExistentContract")
        assert result == []
    
    def test_add_contract_to_collection(self, repo, sample_contract_data):
        """Testa a adição de contrato a uma coleção"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Adiciona um novo schema
        new_schema = {
            'contract': 'NewContract',
            'expected': {'id': 'integer', 'title': 'string'},
            'version': 'v1'
        }
        
        updated_schemas = repo.add_contract_to_collection(1, new_schema)
        
        assert updated_schemas is not None
        assert len(updated_schemas) == 2
        assert updated_schemas[1]['contract'] == 'NewContract'
    
    def test_add_duplicate_contract_to_collection(self, repo, sample_contract_data):
        """Testa a adição de contrato duplicado a uma coleção"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Tenta adicionar um schema duplicado
        duplicate_schema = sample_contract_data['schemas'][0].copy()
        
        updated = repo.add_contract_to_collection(1, duplicate_schema)
        assert updated is not None
        assert len(updated) == 2
    
    def test_remove_contract_from_collection_by_index(self, repo, sample_contract_data):
        """Testa a remoção de contrato de uma coleção por índice"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Remove o primeiro schema
        removed_schema = repo.remove_contract_from_collection(1, 0)
        
        assert removed_schema is not None
        assert removed_schema['contract'] == 'UserContract'
        
        # Verifica se foi removido
        contract = repo.get_contract_by_id(1)
        assert len(contract['schemas']) == 0
    
    def test_remove_contract_from_collection_invalid_index(self, repo, sample_contract_data):
        """Testa a remoção de contrato com índice inválido"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Tenta remover com índice inválido
        result = repo.remove_contract_from_collection(1, 999)
        assert result is None
    
    def test_remove_contract_by_name_from_collection(self, repo, sample_contract_data):
        """Testa a remoção de contrato de uma coleção por nome"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Remove por nome
        removed_schema = repo.remove_contract_by_name_from_collection(1, 'UserContract')
        
        assert removed_schema is not None
        assert removed_schema['contract'] == 'UserContract'
        
        # Verifica se foi removido
        contract = repo.get_contract_by_id(1)
        assert len(contract['schemas']) == 0
    
    def test_remove_contract_by_name_not_found(self, repo, sample_contract_data):
        """Testa a remoção de contrato por nome inexistente"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Tenta remover por nome inexistente
        result = repo.remove_contract_by_name_from_collection(1, 'NonExistentContract')
        assert result is None
    
    def test_update_collection_schemas(self, repo, sample_contract_data):
        """Testa a atualização completa dos schemas de uma coleção"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Atualiza com novos schemas
        new_schemas = [
            {
                'contract': 'UpdatedContract',
                'expected': {'id': 'integer', 'name': 'string'},
                'version': 'v2'
            }
        ]
        
        result = repo.update_collection_schemas(1, new_schemas)
        assert isinstance(result, list)
        
        # Verifica se foi atualizado
        contract = repo.get_contract_by_id(1)
        assert len(contract['schemas']) == 1
        assert contract['schemas'][0]['contract'] == 'UpdatedContract'
    
    def test_update_collection_schemas_invalid_data(self, repo, sample_contract_data):
        """Testa a atualização com dados inválidos"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Tenta atualizar com schema inválido
        invalid_schemas = [
            {
                'contract': 'InvalidContract'
                # Falta o campo 'expected'
            }
        ]
        
        result = repo.update_collection_schemas(1, invalid_schemas)
        assert isinstance(result, list)
    
    def test_update_contract_by_name_in_collection(self, repo, sample_contract_data):
        """Testa a atualização de contrato específico por nome"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Atualiza o contrato específico
        updated_schema = {
            'contract': 'UserContract',
            'expected': {'id': 'integer', 'name': 'string', 'email': 'string', 'age': 'integer'},
            'version': 'v2'
        }
        
        result = repo.update_contract_by_name_in_collection(1, 'UserContract', updated_schema)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Verifica se foi atualizado
        contract = repo.get_contract_by_id(1)
        assert len(contract['schemas']) == 1
        assert contract['schemas'][0]['version'] == 'v2'
    
    def test_update_contract_by_name_not_found(self, repo, sample_contract_data):
        """Testa a atualização de contrato por nome inexistente"""
        # Insere um contrato
        repo.insert_contract(
            sample_contract_data['name'],
            sample_contract_data['squad'],
            sample_contract_data['schemas'],
            sample_contract_data['repository_url']
        )
        
        # Tenta atualizar contrato inexistente
        updated_schema = {
            'contract': 'NonExistentContract',
            'expected': {'id': 'integer'},
            'version': 'v1'
        }
        
        result = repo.update_contract_by_name_in_collection(1, 'NonExistentContract', updated_schema)
        assert result is None


class TestReportRepository:
    """Testes unitários para ReportRepository"""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Cria uma instância do repository com banco temporário"""
        return ReportRepository(temp_db)
    
    def test_create_table(self, repo):
        """Testa a criação da tabela reports_automation"""
        # Verifica se a tabela foi criada
        conn = sqlite3.connect(repo.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports_automation'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'reports_automation'
    
    def test_insert_report_automation(self, repo, sample_report_data):
        """Testa a inserção de um relatório"""
        data = sample_report_data
        
        repo.insert_report_automation(
            data['automation_id'],
            data['status'],
            data['url_report'],
            '2024-01-01T10:00:00',
            'Test Automation',
            'Test Squad',
            json.dumps(data['tests'])
        )
        
        # Verifica se o relatório foi inserido
        reports = repo.get_all_report_automations()
        assert len(reports) == 1
        assert reports[0]['automation_id'] == data['automation_id']
        assert reports[0]['status'] == data['status']
        assert reports[0]['url_report'] == data['url_report']
        assert reports[0]['name'] == 'Test Automation'
        assert reports[0]['squad'] == 'Test Squad'
    
    def test_get_all_report_automations(self, repo, sample_report_data):
        """Testa a busca de todos os relatórios"""
        # Insere alguns relatórios
        for i in range(3):
            data = sample_report_data.copy()
            data['automation_id'] = i + 1
            repo.insert_report_automation(
                data['automation_id'],
                data['status'],
                data['url_report'],
                '2024-01-01T10:00:00',
                f'Test Automation {i}',
                'Test Squad',
                json.dumps(data['tests'])
            )
        
        reports = repo.get_all_report_automations()
        assert len(reports) == 3
        assert all(report['name'].startswith('Test Automation') for report in reports)
    
    def test_get_paginated_report_automations(self, repo, sample_report_data):
        """Testa a paginação de relatórios"""
        # Insere 5 relatórios
        for i in range(5):
            data = sample_report_data.copy()
            data['automation_id'] = i + 1
            repo.insert_report_automation(
                data['automation_id'],
                data['status'],
                data['url_report'],
                '2024-01-01T10:00:00',
                f'Test Automation {i}',
                'Test Squad',
                json.dumps(data['tests'])
            )
        
        # Testa primeira página
        reports, total = repo.get_paginated_report_automations(1, 2)
        assert len(reports) == 2
        assert total == 5
        
        # Testa segunda página
        reports, total = repo.get_paginated_report_automations(2, 2)
        assert len(reports) == 2
        assert total == 5
    
    def test_get_reports_by_search(self, repo, sample_report_data):
        """Testa a busca de relatórios por termo"""
        # Insere relatórios com nomes diferentes
        test_names = ["Python Test", "Java Test", "JavaScript Test", "Python Automation"]
        for i, name in enumerate(test_names):
            data = sample_report_data.copy()
            data['automation_id'] = i + 1
            repo.insert_report_automation(
                data['automation_id'],
                data['status'],
                data['url_report'],
                '2024-01-01T10:00:00',
                name,
                'Test Squad',
                json.dumps(data['tests'])
            )
        
        # Busca por "Python"
        reports, total = repo.get_reports_by_search("Python", 1, 10)
        assert total == 2
        assert len(reports) == 2
        assert all("Python" in report['name'] for report in reports)
    
    def test_get_reports_by_search_fuzzy_matching(self, repo, sample_report_data):
        """Testa a busca fuzzy de relatórios"""
        # Insere relatórios com nomes similares
        test_names = ["Automation Test", "Test Automation", "Automation Suite", "Test Suite"]
        for i, name in enumerate(test_names):
            data = sample_report_data.copy()
            data['automation_id'] = i + 1
            repo.insert_report_automation(
                data['automation_id'],
                data['status'],
                data['url_report'],
                '2024-01-01T10:00:00',
                name,
                'Test Squad',
                json.dumps(data['tests'])
            )
        
        # Busca por "Automation" (deve encontrar todos)
        reports, total = repo.get_reports_by_search("Automation", 1, 10)
        assert total >= 3
        assert len(reports) == total
        assert any("Automation" in report['name'] for report in reports)
        
        # Busca por "Test" (deve encontrar todos)
        reports, total = repo.get_reports_by_search("Test", 1, 10)
        assert total >= 3
        assert len(reports) == total
        assert any("Test" in report['name'] for report in reports)
