import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from controller.automation_controller import automation_controller
from controller.report_controller import report_controller
from controller.test_contract_controller import test_contract_controller


class TestAutomationController:
    """Testes unitários para AutomationController"""
    
    @pytest.fixture
    def app(self):
        """Cria uma aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(automation_controller)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Cria um cliente de teste"""
        return app.test_client()
    
    @patch('controller.automation_controller.AutomationService')
    def test_new_automation_form(self, mock_service, client):
        """Testa o endpoint GET /automations/new"""
        response = client.get('/automations/new')
        
        assert response.status_code == 200
        assert b'register_automation.html' in response.data or response.data.decode().find('register_automation') != -1
    
    @patch('controller.automation_controller.AutomationService')
    def test_list_automations_view(self, mock_service, client):
        """Testa o endpoint GET /automations/list"""
        response = client.get('/automations/list')
        
        assert response.status_code == 200
        assert b'automations_list.html' in response.data or response.data.decode().find('automations_list') != -1
    
    @patch('controller.automation_controller.AutomationService')
    def test_schema_generator_view(self, mock_service, client):
        """Testa o endpoint GET /schema-generator"""
        response = client.get('/schema-generator')
        
        assert response.status_code == 200
        assert b'schema_generator.html' in response.data or response.data.decode().find('schema_generator') != -1
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_paginated_automations_success(self, mock_service, client):
        """Testa o endpoint GET /automations/paginated com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.fetch_paginated_automations.return_value = (
            [{'id': 1, 'name': 'Test Automation'}], 1
        )
        
        response = client.get('/automations/paginated?page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'automations' in data
        assert 'total_automations' in data
        assert 'total_pages' in data
        assert 'current_page' in data
        assert data['total_automations'] == 1
        assert data['current_page'] == 1
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_paginated_automations_with_search(self, mock_service, client):
        """Testa o endpoint GET /automations/paginated com busca"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.fetch_paginated_automations.return_value = (
            [{'id': 1, 'name': 'Python Test'}], 1
        )
        
        response = client.get('/automations/paginated?page=1&per_page=10&search=Python')
        
        assert response.status_code == 200
        mock_service_instance.fetch_paginated_automations.assert_called_once_with(1, 10, 'Python')
    
    @patch('controller.automation_controller.AutomationService')
    def test_register_automation_success(self, mock_service, client, sample_automation_data):
        """Testa o endpoint POST /register-automation com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.register_automation.return_value = None
        
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Automação cadastrada com sucesso!'
        assert 'received_data' in data
        
        # Verifica se o service foi chamado corretamente
        mock_service_instance.register_automation.assert_called_once_with(
            sample_automation_data['name'],
            sample_automation_data['squad'],
            sample_automation_data['description'],
            sample_automation_data['language'],
            sample_automation_data['cucumber'],
            sample_automation_data['launch_date'],
            sample_automation_data['git'],
            sample_automation_data.get('image_base64')
        )
    
    @patch('controller.automation_controller.AutomationService')
    def test_register_automation_validation_error(self, mock_service, client):
        """Testa o endpoint POST /register-automation com erro de validação"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.register_automation.side_effect = ValueError("Dados inválidos")
        
        invalid_data = {'name': 'Test'}
        
        response = client.post(
            '/register-automation',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Dados inválidos'
    
    @patch('controller.automation_controller.AutomationService')
    def test_register_automation_internal_error(self, mock_service, client, sample_automation_data):
        """Testa o endpoint POST /register-automation com erro interno"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.register_automation.side_effect = Exception("Erro interno")
        
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Erro interno' in data['error']
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_all_automations(self, mock_service, client):
        """Testa o endpoint GET /automations"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        expected_automations = [{'id': 1, 'name': 'Test Automation'}]
        mock_service_instance.fetch_all_automations.return_value = expected_automations
        
        response = client.get('/automations')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == expected_automations
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_automation_by_id_success(self, mock_service, client):
        """Testa o endpoint GET /automations/<id> com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        expected_automation = {'id': 1, 'name': 'Test Automation'}
        mock_service_instance.get_automation_by_id.return_value = expected_automation
        
        response = client.get('/automations/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == expected_automation
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_automation_by_id_not_found(self, mock_service, client):
        """Testa o endpoint GET /automations/<id> quando não encontrado"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.get_automation_by_id.return_value = None
        
        response = client.get('/automations/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Automation not found'
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_automation_by_name_success(self, mock_service, client):
        """Testa o endpoint GET /automations/<name> com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        expected_automation = {'id': 1, 'name': 'Test Automation'}
        mock_service_instance.get_automation_by_name.return_value = expected_automation
        
        response = client.get('/automations/Test%20Automation')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == expected_automation
    
    @patch('controller.automation_controller.AutomationService')
    def test_get_automation_by_name_not_found(self, mock_service, client):
        """Testa o endpoint GET /automations/<name> quando não encontrado"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.get_automation_by_name.return_value = None
        
        response = client.get('/automations/NonExistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Automation not found'
    
    @patch('controller.automation_controller.AutomationService')
    def test_delete_automation_success(self, mock_service, client):
        """Testa o endpoint DELETE /automation/<id> com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.delete_automation.return_value = True
        
        response = client.delete('/automation/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deletado com sucesso' in data['message']
    
    @patch('controller.automation_controller.AutomationService')
    def test_delete_automation_not_found(self, mock_service, client):
        """Testa o endpoint DELETE /automation/<id> quando não encontrado"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.delete_automation.return_value = False
        
        response = client.delete('/automation/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'não encontrado' in data['error']


class TestReportController:
    """Testes unitários para ReportController"""
    
    @pytest.fixture
    def app(self):
        """Cria uma aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(report_controller)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Cria um cliente de teste"""
        return app.test_client()
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_dash_view(self, mock_report_service, mock_automation_service, client):
        """Testa o endpoint GET /dash"""
        response = client.get('/dash')
        
        assert response.status_code == 200
        assert b'execution_dashboard.html' in response.data or response.data.decode().find('execution_dashboard') != -1
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_index_view(self, mock_report_service, mock_automation_service, client):
        """Testa o endpoint GET /"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'index.html' in response.data or response.data.decode().find('index') != -1
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_register_automation_success(self, mock_report_service, mock_automation_service, client, sample_report_data):
        """Testa o endpoint POST /report com sucesso"""
        # Mock dos services
        mock_automation_service_instance = mock_automation_service.return_value
        mock_report_service_instance = mock_report_service.return_value
        
        mock_automation_service_instance.get_automation_by_id.return_value = {
            'id': 1, 'name': 'Test Automation', 'squad': 'Test Squad'
        }
        mock_report_service_instance.register_report.return_value = None
        
        response = client.post(
            '/report',
            data=json.dumps(sample_report_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Relatorio gerado com sucesso!'
        assert 'received_data' in data
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_register_automation_not_found(self, mock_report_service, mock_automation_service, client, sample_report_data):
        """Testa o endpoint POST /report quando automação não encontrada"""
        # Mock dos services
        mock_automation_service_instance = mock_automation_service.return_value
        mock_automation_service_instance.get_automation_by_id.return_value = None
        
        response = client.post(
            '/report',
            data=json.dumps(sample_report_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Automation not found'
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_get_all_reports(self, mock_report_service, mock_automation_service, client):
        """Testa o endpoint GET /reports"""
        # Mock do service
        mock_report_service_instance = mock_report_service.return_value
        expected_reports = [{'id_report': 1, 'name': 'Test Report'}]
        mock_report_service_instance.fetch_all_reports.return_value = expected_reports
        
        response = client.get('/reports')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == expected_reports
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_get_paginated_reports_with_search(self, mock_report_service, mock_automation_service, client):
        """Testa o endpoint GET /reports/paginated com busca"""
        # Mock do service
        mock_report_service_instance = mock_report_service.return_value
        expected_reports = [{'id_report': 1, 'name': 'Python Test'}]
        mock_report_service_instance.fetch_paginated_reports.return_value = (expected_reports, 1)
        
        response = client.get('/reports/paginated?page=1&per_page=10&search=Python')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'reports' in data
        assert 'total_reports' in data
        assert 'total_pages' in data
        assert 'current_page' in data
        assert data['total_reports'] == 1
        assert data['current_page'] == 1
        
        # Verifica se o service foi chamado com os parâmetros corretos
        mock_report_service_instance.fetch_paginated_reports.assert_called_once_with(1, 10, 'Python')
    
    @patch('controller.report_controller.AutomationService')
    @patch('controller.report_controller.ReportService')
    def test_get_paginated_reports_without_search(self, mock_report_service, mock_automation_service, client):
        """Testa o endpoint GET /reports/paginated sem busca"""
        # Mock do service
        mock_report_service_instance = mock_report_service.return_value
        expected_reports = [{'id_report': 1, 'name': 'Test Report'}]
        mock_report_service_instance.fetch_paginated_reports.return_value = (expected_reports, 1)
        
        response = client.get('/reports/paginated?page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'reports' in data
        assert 'total_reports' in data
        assert 'total_pages' in data
        assert 'current_page' in data
        
        # Verifica se o service foi chamado sem termo de busca
        mock_report_service_instance.fetch_paginated_reports.assert_called_once_with(1, 10, None)


class TestContractController:
    """Testes unitários para TestContractController"""
    
    @pytest.fixture
    def app(self):
        """Cria uma aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(test_contract_controller)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Cria um cliente de teste"""
        return app.test_client()
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_new_contract_form(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/new"""
        response = client.get('/contracts/new')
        
        assert response.status_code == 200
        assert b'register_contract.html' in response.data or response.data.decode().find('register_contract') != -1
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_contracts_list(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/list"""
        response = client.get('/contracts/list')
        
        assert response.status_code == 200
        assert b'contracts_list.html' in response.data or response.data.decode().find('contracts_list') != -1
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_check_contract_name_success(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contracts/check-name com nome disponível"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        mock_repository_instance.get_all_contracts.return_value = []
        
        data = {'name': 'Available Name'}
        
        response = client.post(
            '/contracts/check-name',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == "Nome 'Available Name' está disponível"
        assert response_data['available'] is True
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_check_contract_name_already_exists(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contracts/check-name com nome já existente"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        mock_repository_instance.get_all_contracts.return_value = [
            {'id': 1, 'name': 'Existing Name'}
        ]
        
        data = {'name': 'Existing Name'}
        
        response = client.post(
            '/contracts/check-name',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == "Já existe uma coleção com o nome 'Existing Name'"
        assert response_data['available'] is False
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_check_contract_name_missing_field(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contracts/check-name com campo obrigatório faltando"""
        data = {}
        
        response = client.post(
            '/contracts/check-name',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "Campo 'name' é obrigatório" in response_data['error']
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_check_contract_name_empty(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contracts/check-name com nome vazio"""
        data = {'name': '   '}
        
        response = client.post(
            '/contracts/check-name',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "Nome não pode estar vazio" in response_data['error']
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_contract_success(self, mock_service, mock_repository, client, sample_contract_data):
        """Testa o endpoint POST /contract com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.create_contract.return_value = (
            True,
            {'message': 'Coleção de contratos salva com sucesso!'},
            None
        )
        
        response = client.post(
            '/contract',
            data=json.dumps(sample_contract_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Coleção de contratos salva com sucesso!'
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_contract_validation_error(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contract com erro de validação"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.create_contract.return_value = (
            False,
            None,
            'Dados inválidos'
        )
        
        invalid_data = {'name': 'Test'}
        
        response = client.post(
            '/contract',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Dados inválidos'
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_all_contracts_success(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts com sucesso"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contracts = [{'id': 1, 'name': 'Test Contract'}]
        mock_repository_instance.get_all_contracts.return_value = expected_contracts
        
        response = client.get('/contracts')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Contratos recuperados com sucesso!'
        assert response_data['contracts'] == expected_contracts
        assert response_data['total'] == 1
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_all_contracts_error(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts com erro"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        mock_repository_instance.get_all_contracts.side_effect = Exception("Database error")
        
        response = client.get('/contracts')
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Erro ao recuperar contratos: Database error" in response_data['error']
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_paginated_contracts_success(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/paginated com sucesso"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contracts = [{'id': 1, 'name': 'Test Contract'}]
        mock_repository_instance.get_paginated_contracts.return_value = (expected_contracts, 1)
        
        response = client.get('/contracts/paginated?page=1&per_page=10')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'contracts' in response_data
        assert 'total_contracts' in response_data
        assert 'total_pages' in response_data
        assert 'current_page' in response_data
        assert response_data['total_contracts'] == 1
        assert response_data['current_page'] == 1
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_paginated_contracts_with_search(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/paginated com busca"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contracts = [{'id': 1, 'name': 'User Contract'}]
        mock_repository_instance.get_contracts_by_search.return_value = (expected_contracts, 1)
        
        response = client.get('/contracts/paginated?page=1&per_page=10&search=User')
        
        assert response.status_code == 200
        mock_repository_instance.get_contracts_by_search.assert_called_once_with('User', 1, 10)
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_paginated_contracts_with_squad(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/paginated com filtro de squad"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contracts = [{'id': 1, 'name': 'Test Contract', 'squad': 'Test Squad'}]
        mock_repository_instance.get_contracts_by_squad_paginated.return_value = (expected_contracts, 1)
        
        response = client.get('/contracts/paginated?page=1&per_page=10&squad=Test%20Squad')
        
        assert response.status_code == 200
        mock_repository_instance.get_contracts_by_squad_paginated.assert_called_once_with('Test Squad', 1, 10)
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_paginated_contracts_with_search_and_squad(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/paginated com busca e filtro de squad"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contracts = [{'id': 1, 'name': 'User Contract', 'squad': 'Test Squad'}]
        mock_repository_instance.get_contracts_by_search_and_squad.return_value = (expected_contracts, 1)
        
        response = client.get('/contracts/paginated?page=1&per_page=10&search=User&squad=Test%20Squad')
        
        assert response.status_code == 200
        mock_repository_instance.get_contracts_by_search_and_squad.assert_called_once_with('User', 'Test Squad', 1, 10)
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_contract_by_id_success(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/<id> com sucesso"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contract = {'id': 1, 'name': 'Test Contract'}
        mock_repository_instance.get_contract_by_id.return_value = expected_contract
        
        response = client.get('/contracts/1')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Contrato recuperado com sucesso!'
        assert response_data['contract'] == expected_contract
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_contract_by_id_not_found(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/<id> quando não encontrado"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        mock_repository_instance.get_contract_by_id.return_value = None
        
        response = client.get('/contracts/999')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Contrato não encontrado'
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_get_contracts_by_squad_success(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/squad/<squad> com sucesso"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_contracts = [{'id': 1, 'name': 'Test Contract', 'squad': 'Test Squad'}]
        mock_repository_instance.get_contracts_by_squad.return_value = expected_contracts
        
        response = client.get('/contracts/squad/Test%20Squad')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Contratos da squad Test Squad recuperados com sucesso!'
        assert response_data['contracts'] == expected_contracts
        assert response_data['total'] == 1
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_search_contracts_by_name_and_contract_success(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/search com sucesso"""
        # Mock do repository
        mock_repository_instance = mock_repository.return_value
        expected_result = {
            'collection_name': 'Test Collection',
            'contract_name': 'UserContract',
            'schema': {'id': 'integer', 'name': 'string'}
        }
        mock_repository_instance.search_contracts_by_name_and_contract.return_value = expected_result
        
        response = client.get('/contracts/search?name=Test%20Collection&contract=UserContract')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Busca realizada com sucesso!'
        assert response_data['contracts'] == expected_result
        assert response_data['total'] == 1
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_search_contracts_missing_name(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/search sem parâmetro name"""
        response = client.get('/contracts/search?contract=UserContract')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "Parâmetro 'name' é obrigatório" in response_data['error']
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_search_contracts_missing_contract(self, mock_service, mock_repository, client):
        """Testa o endpoint GET /contracts/search sem parâmetro contract"""
        response = client.get('/contracts/search?name=Test%20Collection')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "Parâmetro 'contract' é obrigatório" in response_data['error']
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_validate_contract_success(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contract-validate com sucesso"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.validate_contract.return_value = {
            'valid': True,
            'message': 'Validação bem-sucedida!'
        }
        
        data = {
            'name': 'Test Collection',
            'contract': 'UserContract',
            'body': {'id': 1, 'name': 'John', 'email': 'john@example.com'}
        }
        
        response = client.post(
            '/contract-validate',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Validação bem-sucedida!'
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_validate_contract_validation_error(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contract-validate com erro de validação"""
        # Mock do service
        mock_service_instance = mock_service.return_value
        mock_service_instance.validate_contract.return_value = {
            'valid': False,
            'error': 'Erro de validação'
        }
        
        data = {
            'name': 'Test Collection',
            'contract': 'UserContract',
            'body': {'invalid': 'data'}
        }
        
        response = client.post(
            '/contract-validate',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Erro de validação'
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_validate_contract_missing_fields(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contract-validate com campos obrigatórios faltando"""
        data = {'name': 'Test Collection'}
        
        response = client.post(
            '/contract-validate',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "Campo 'contract' é obrigatório" in response_data['error']
    
    @patch('controller.test_contract_controller.ContractRepository')
    @patch('controller.test_contract_controller.ContractService')
    def test_validate_contract_invalid_body(self, mock_service, mock_repository, client):
        """Testa o endpoint POST /contract-validate com body inválido"""
        data = {
            'name': 'Test Collection',
            'contract': 'UserContract',
            'body': 'invalid_string'
        }
        
        response = client.post(
            '/contract-validate',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "Campo 'body' deve ser um objeto JSON ou array" in response_data['error']
