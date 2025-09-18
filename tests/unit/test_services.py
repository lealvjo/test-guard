import pytest
import json
from unittest.mock import patch, MagicMock
from service.automation_service import AutomationService
from service.contract_service import ContractService
from service.report_service import ReportService


class TestAutomationService:
    """Testes unitários para AutomationService"""
    
    @pytest.fixture
    def service(self):
        """Cria uma instância do service com repository mockado"""
        with patch('service.automation_service.AutomationRepository') as mock_repo:
            service = AutomationService()
            service.repository = mock_repo.return_value
            return service
    
    def test_register_automation_success(self, service, sample_automation_data):
        """Testa o registro bem-sucedido de uma automação"""
        # Mock do repository
        service.repository.check_duplicate_automation.return_value = None
        service.repository.insert_automation.return_value = None
        
        # Dados de teste
        data = sample_automation_data
        
        # Executa o método
        service.register_automation(
            data['name'],
            data['squad'],
            data['description'],
            data['language'],
            data['cucumber'],
            data['launch_date'],
            data['git'],
            data['image_base64']
        )
        
        # Verifica se os métodos foram chamados corretamente
        service.repository.check_duplicate_automation.assert_called_once_with(
            data['name'], data['squad'], data['git']
        )
        service.repository.insert_automation.assert_called_once_with(
            data['name'], data['squad'], data['description'],
            data['language'], data['cucumber'], data['launch_date'],
            data['git'], data['image_base64']
        )
    
    def test_register_automation_duplicate(self, service, sample_automation_data):
        """Testa o registro de automação duplicada"""
        # Mock do repository retornando duplicata
        duplicate_automation = {
            'id': 1,
            'name': sample_automation_data['name'],
            'squad': sample_automation_data['squad'],
            'git': sample_automation_data['git']
        }
        service.repository.check_duplicate_automation.return_value = duplicate_automation
        
        # Dados de teste
        data = sample_automation_data
        
        # Executa o método e verifica se levanta exceção
        with pytest.raises(ValueError, match="Já existe uma automação com o nome"):
            service.register_automation(
                data['name'],
                data['squad'],
                data['description'],
                data['language'],
                data['cucumber'],
                data['launch_date'],
                data['git'],
                data['image_base64']
            )
        
        # Verifica se não tentou inserir
        service.repository.insert_automation.assert_not_called()
    
    def test_fetch_all_automations(self, service):
        """Testa a busca de todas as automações"""
        # Mock do repository
        expected_automations = [
            {'id': 1, 'name': 'Automation 1'},
            {'id': 2, 'name': 'Automation 2'}
        ]
        service.repository.get_all_automations.return_value = expected_automations
        
        # Executa o método
        result = service.fetch_all_automations()
        
        # Verifica o resultado
        assert result == expected_automations
        service.repository.get_all_automations.assert_called_once()
    
    def test_delete_automation(self, service):
        """Testa a exclusão de uma automação"""
        # Mock do repository
        service.repository.delete_automation.return_value = True
        
        # Executa o método
        result = service.delete_automation(1)
        
        # Verifica o resultado
        assert result is True
        service.repository.delete_automation.assert_called_once_with(1)
    
    def test_get_automation_by_id(self, service):
        """Testa a busca de automação por ID"""
        # Mock do repository
        expected_automation = {'id': 1, 'name': 'Test Automation'}
        service.repository.get_automation_by_id.return_value = expected_automation
        
        # Executa o método
        result = service.get_automation_by_id(1)
        
        # Verifica o resultado
        assert result == expected_automation
        service.repository.get_automation_by_id.assert_called_once_with(1)
    
    def test_get_automation_by_name(self, service):
        """Testa a busca de automação por nome"""
        # Mock do repository
        expected_automation = {'id': 1, 'name': 'Test Automation'}
        service.repository.get_automation_by_name.return_value = expected_automation
        
        # Executa o método
        result = service.get_automation_by_name('Test Automation')
        
        # Verifica o resultado
        assert result == expected_automation
        service.repository.get_automation_by_name.assert_called_once_with('Test Automation')
    
    def test_fetch_paginated_automations_with_search(self, service):
        """Testa a busca paginada de automações com termo de busca"""
        # Mock do repository
        expected_automations = [{'id': 1, 'name': 'Python Test'}]
        expected_total = 1
        service.repository.get_automations_by_search.return_value = (expected_automations, expected_total)
        
        # Executa o método
        automations, total = service.fetch_paginated_automations(1, 10, 'Python')
        
        # Verifica o resultado
        assert automations == expected_automations
        assert total == expected_total
        service.repository.get_automations_by_search.assert_called_once_with('Python', 1, 10)
    
    def test_fetch_paginated_automations_without_search(self, service):
        """Testa a busca paginada de automações sem termo de busca"""
        # Mock do repository
        expected_automations = [{'id': 1, 'name': 'Test Automation'}]
        expected_total = 1
        service.repository.get_paginated_automations.return_value = (expected_automations, expected_total)
        
        # Executa o método
        automations, total = service.fetch_paginated_automations(1, 10)
        
        # Verifica o resultado
        assert automations == expected_automations
        assert total == expected_total
        service.repository.get_paginated_automations.assert_called_once_with(1, 10)


class TestContractService:
    """Testes unitários para ContractService"""
    
    @pytest.fixture
    def service(self):
        """Cria uma instância do service com repository mockado"""
        with patch('service.contract_service.ContractRepository') as mock_repo:
            service = ContractService()
            service.contract_repository = mock_repo.return_value
            return service
    
    def test_validate_contract_data_success(self, service, sample_contract_data):
        """Testa a validação bem-sucedida de dados de contrato"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = []
        
        # Executa o método
        is_valid, error_message, validated_data = service.validate_contract_data(sample_contract_data)
        
        # Verifica o resultado
        assert is_valid is True
        assert error_message is None
        assert validated_data['name'] == sample_contract_data['name']
        assert validated_data['squad'] == sample_contract_data['squad']
        assert validated_data['schemas'] == sample_contract_data['schemas']
    
    def test_validate_contract_data_missing_fields(self, service):
        """Testa a validação com campos obrigatórios faltando"""
        # Dados incompletos
        incomplete_data = {'name': 'Test Contract'}
        
        # Executa o método
        is_valid, error_message, validated_data = service.validate_contract_data(incomplete_data)
        
        # Verifica o resultado
        assert is_valid is False
        assert "Campo 'squad' é obrigatório" in error_message
        assert validated_data is None
    
    def test_validate_contract_data_duplicate_name(self, service, sample_contract_data):
        """Testa a validação com nome duplicado"""
        # Mock do repository retornando contrato existente
        existing_contract = {'id': 1, 'name': sample_contract_data['name']}
        service.contract_repository.get_all_contracts.return_value = [existing_contract]
        
        # Executa o método
        is_valid, error_message, validated_data = service.validate_contract_data(sample_contract_data)
        
        # Verifica o resultado
        assert is_valid is False
        assert f"Já existe uma coleção com o nome '{sample_contract_data['name']}'" in error_message
        assert validated_data is None
    
    def test_validate_contract_data_invalid_schemas(self, service, sample_contract_data):
        """Testa a validação com schemas inválidos"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = []
        
        # Dados com schemas inválidos
        invalid_data = sample_contract_data.copy()
        invalid_data['schemas'] = [
            {
                'contract': 'InvalidContract'
                # Falta o campo 'expected'
            }
        ]
        
        # Executa o método
        is_valid, error_message, validated_data = service.validate_contract_data(invalid_data)
        
        # Verifica o resultado
        assert is_valid is False
        assert "deve conter 'contract' e 'expected'" in error_message
        assert validated_data is None
    
    def test_validate_contract_data_duplicate_contracts(self, service, sample_contract_data):
        """Testa a validação com contratos duplicados"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = []
        
        # Dados com contratos duplicados
        duplicate_data = sample_contract_data.copy()
        duplicate_data['schemas'] = [
            {
                'contract': 'UserContract',
                'expected': {'id': 'integer'},
                'version': 'v1'
            },
            {
                'contract': 'UserContract',
                'expected': {'id': 'integer'},
                'version': 'v1'
            }
        ]
        
        # Executa o método
        is_valid, error_message, validated_data = service.validate_contract_data(duplicate_data)
        
        # Verifica o resultado
        assert is_valid is False
        assert "Já existe um contrato com o nome 'UserContract'" in error_message
        assert validated_data is None
    
    def test_create_contract_success(self, service, sample_contract_data):
        """Testa a criação bem-sucedida de um contrato"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = []
        service.contract_repository.insert_contract.return_value = None
        
        # Executa o método
        success, result_data, error_message = service.create_contract(sample_contract_data)
        
        # Verifica o resultado
        assert success is True
        assert error_message is None
        assert result_data['message'] == 'Coleção de contratos salva com sucesso!'
        assert result_data['received_data']['name'] == sample_contract_data['name']
        assert result_data['received_data']['squad'] == sample_contract_data['squad']
        assert result_data['received_data']['schemas_count'] == len(sample_contract_data['schemas'])
        
        # Verifica se o repository foi chamado
        service.contract_repository.insert_contract.assert_called_once()
    
    def test_create_contract_validation_error(self, service):
        """Testa a criação de contrato com erro de validação"""
        # Dados inválidos
        invalid_data = {'name': 'Test Contract'}
        
        # Executa o método
        success, result_data, error_message = service.create_contract(invalid_data)
        
        # Verifica o resultado
        assert success is False
        assert result_data is None
        assert error_message is not None
    
    def test_create_contract_repository_error(self, service, sample_contract_data):
        """Testa a criação de contrato com erro no repository"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = []
        service.contract_repository.insert_contract.side_effect = Exception("Database error")
        
        # Executa o método
        success, result_data, error_message = service.create_contract(sample_contract_data)
        
        # Verifica o resultado
        assert success is False
        assert result_data is None
        assert "Erro ao salvar contrato: Database error" in error_message
    
    def test_validate_contract_update_data_add_action(self, service):
        """Testa a validação de dados de atualização para ação 'add'"""
        data = {
            'action': 'add',
            'schema': {'contract': 'NewContract', 'expected': {'id': 'integer'}}
        }
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is True
        assert error_message is None
        assert action_type == 'add'
        assert validated_data['schema'] == data['schema']
    
    def test_validate_contract_update_data_add_missing_schema(self, service):
        """Testa a validação de dados de atualização para ação 'add' sem schema"""
        data = {'action': 'add'}
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is False
        assert "Campo 'schema' é obrigatório para ação 'add'" in error_message
    
    def test_validate_contract_update_data_remove_by_index(self, service):
        """Testa a validação de dados de atualização para ação 'remove' por índice"""
        data = {
            'action': 'remove',
            'schema_index': 0
        }
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is True
        assert error_message is None
        assert action_type == 'remove_by_index'
        assert validated_data['schema_index'] == 0
    
    def test_validate_contract_update_data_remove_by_name(self, service):
        """Testa a validação de dados de atualização para ação 'remove' por nome"""
        data = {
            'action': 'remove',
            'contract_name': 'UserContract'
        }
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is True
        assert error_message is None
        assert action_type == 'remove_by_name'
        assert validated_data['contract_name'] == 'UserContract'
    
    def test_validate_contract_update_data_remove_missing_params(self, service):
        """Testa a validação de dados de atualização para ação 'remove' sem parâmetros"""
        data = {'action': 'remove'}
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is False
        assert "Campo 'schema_index' ou 'contract_name' é obrigatório" in error_message
    
    def test_validate_contract_update_data_update_by_name(self, service):
        """Testa a validação de dados de atualização para ação 'update' por nome"""
        data = {
            'action': 'update',
            'contract_name': 'UserContract',
            'schema': {'contract': 'UserContract', 'expected': {'id': 'integer'}}
        }
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is True
        assert error_message is None
        assert action_type == 'update_by_name'
        assert validated_data['contract_name'] == 'UserContract'
        assert validated_data['schema'] == data['schema']
    
    def test_validate_contract_update_data_update_complete(self, service):
        """Testa a validação de dados de atualização para ação 'update' completa"""
        data = {
            'action': 'update',
            'schemas': [
                {'contract': 'UserContract', 'expected': {'id': 'integer'}}
            ]
        }
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is True
        assert error_message is None
        assert action_type == 'update_complete'
        assert validated_data['schemas'] == data['schemas']
    
    def test_validate_contract_update_data_invalid_action(self, service):
        """Testa a validação de dados de atualização com ação inválida"""
        data = {'action': 'invalid'}
        
        # Executa o método
        is_valid, error_message, action_type, validated_data = service.validate_contract_update_data(data)
        
        # Verifica o resultado
        assert is_valid is False
        assert "Ação inválida. Use 'add', 'remove' ou 'update'" in error_message
    
    @patch('service.contract_service.JSONSCHEMA_AVAILABLE', True)
    @patch('service.contract_service.validate')
    def test_validate_contract_success(self, mock_validate, service, sample_contract_data):
        """Testa a validação bem-sucedida de contrato"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = [sample_contract_data]
        
        # Dados para validar
        body_to_validate = {'id': 1, 'name': 'John', 'email': 'john@example.com'}
        
        # Executa o método
        result = service.validate_contract('Test Contract Collection', 'UserContract', body_to_validate)
        
        # Verifica o resultado
        assert result['valid'] is True
        assert result['message'] == 'Validação bem-sucedida!'
        assert result['collection_name'] == 'Test Contract Collection'
        assert result['contract_name'] == 'UserContract'
        assert result['validated_data'] == body_to_validate
        
        # Verifica se o validate foi chamado
        mock_validate.assert_called_once()
    
    @patch('service.contract_service.JSONSCHEMA_AVAILABLE', False)
    def test_validate_contract_jsonschema_not_available(self, service):
        """Testa a validação quando jsonschema não está disponível"""
        # Executa o método
        result = service.validate_contract('Test Collection', 'TestContract', {})
        
        # Verifica o resultado
        assert result['valid'] is False
        assert 'Biblioteca jsonschema não está instalada' in result['error']
    
    @patch('service.contract_service.JSONSCHEMA_AVAILABLE', True)
    def test_validate_contract_collection_not_found(self, service):
        """Testa a validação quando a coleção não é encontrada"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = []
        
        # Executa o método
        result = service.validate_contract('NonExistent Collection', 'TestContract', {})
        
        # Verifica o resultado
        assert result['valid'] is False
        assert 'Coleção "NonExistent Collection" não encontrada' in result['error']
    
    @patch('service.contract_service.JSONSCHEMA_AVAILABLE', True)
    def test_validate_contract_contract_not_found(self, service, sample_contract_data):
        """Testa a validação quando o contrato não é encontrado"""
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = [sample_contract_data]
        
        # Executa o método
        result = service.validate_contract('Test Contract Collection', 'NonExistentContract', {})
        
        # Verifica o resultado
        assert result['valid'] is False
        assert 'Contrato "NonExistentContract" não encontrado' in result['error']
    
    @patch('service.contract_service.JSONSCHEMA_AVAILABLE', True)
    @patch('service.contract_service.validate')
    def test_validate_contract_validation_error(self, mock_validate, service, sample_contract_data):
        """Testa a validação com erro de validação"""
        from jsonschema import ValidationError
        
        # Mock do repository
        service.contract_repository.get_all_contracts.return_value = [sample_contract_data]
        
        # Mock do ValidationError
        mock_validate.side_effect = ValidationError("Invalid data", path=['name'])
        
        # Dados para validar
        body_to_validate = {'id': 1, 'name': 'John'}
        
        # Executa o método
        result = service.validate_contract('Test Contract Collection', 'UserContract', body_to_validate)
        
        # Verifica o resultado
        assert result['valid'] is False
        assert 'Erro de validação: Invalid data' in result['error']
        assert result['validation_error']['message'] == 'Invalid data'
        assert result['validated_data'] == body_to_validate


class TestReportService:
    """Testes unitários para ReportService"""
    
    @pytest.fixture
    def service(self):
        """Cria uma instância do service com repository mockado"""
        with patch('service.report_service.ReportRepository') as mock_repo:
            service = ReportService()
            service.repository = mock_repo.return_value
            return service
    
    def test_register_report(self, service, sample_report_data):
        """Testa o registro de um relatório"""
        # Mock do repository
        service.repository.insert_report_automation.return_value = None
        
        # Dados de teste
        data = sample_report_data
        
        # Executa o método
        service.register_report(
            data['automation_id'],
            data['status'],
            data['url_report'],
            '2024-01-01T10:00:00',
            'Test Automation',
            'Test Squad',
            json.dumps(data['tests'])
        )
        
        # Verifica se o método foi chamado corretamente
        service.repository.insert_report_automation.assert_called_once_with(
            data['automation_id'],
            data['status'],
            data['url_report'],
            '2024-01-01T10:00:00',
            'Test Automation',
            'Test Squad',
            json.dumps(data['tests'])
        )
    
    def test_fetch_all_reports(self, service):
        """Testa a busca de todos os relatórios"""
        # Mock do repository
        expected_reports = [
            {'id_report': 1, 'name': 'Report 1'},
            {'id_report': 2, 'name': 'Report 2'}
        ]
        service.repository.get_all_report_automations.return_value = expected_reports
        
        # Executa o método
        result = service.fetch_all_reports()
        
        # Verifica o resultado
        assert result == expected_reports
        service.repository.get_all_report_automations.assert_called_once()
    
    def test_fetch_paginated_reports_with_search(self, service):
        """Testa a busca paginada de relatórios com termo de busca"""
        # Mock do repository
        expected_reports = [{'id_report': 1, 'name': 'Python Test'}]
        expected_total = 1
        service.repository.get_reports_by_search.return_value = (expected_reports, expected_total)
        
        # Executa o método
        reports, total = service.fetch_paginated_reports(1, 10, 'Python')
        
        # Verifica o resultado
        assert reports == expected_reports
        assert total == expected_total
        service.repository.get_reports_by_search.assert_called_once_with('Python', 1, 10)
    
    def test_fetch_paginated_reports_without_search(self, service):
        """Testa a busca paginada de relatórios sem termo de busca"""
        # Mock do repository
        expected_reports = [{'id_report': 1, 'name': 'Test Report'}]
        expected_total = 1
        service.repository.get_paginated_report_automations.return_value = (expected_reports, expected_total)
        
        # Executa o método
        reports, total = service.fetch_paginated_reports(1, 10)
        
        # Verifica o resultado
        assert reports == expected_reports
        assert total == expected_total
        service.repository.get_paginated_report_automations.assert_called_once_with(1, 10)
