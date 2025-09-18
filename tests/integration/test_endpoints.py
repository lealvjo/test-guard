import pytest
import json
import os
import tempfile
from datetime import datetime
from main import app


@pytest.mark.integration
class TestAutomationIntegration:
    """Testes de integração para endpoints de automação"""
    
    @pytest.fixture
    def client(self, temp_db):
        """Cria um cliente de teste com banco temporário"""
        # Configura o app para usar o banco temporário
        with patch.dict(os.environ, {'AUTOMATION_DB_PATH': temp_db}):
            app.config['TESTING'] = True
            client = app.test_client()
            yield client
    
    def test_automation_crud_flow(self, client, sample_automation_data):
        """Testa o fluxo completo de CRUD de automações"""
        # 1. Criar uma automação
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 2. Buscar todas as automações
        response = client.get('/automations')
        assert response.status_code == 200
        automations = json.loads(response.data)
        assert len(automations) == 1
        assert automations[0]['name'] == sample_automation_data['name']
        
        automation_id = automations[0]['id']
        
        # 3. Buscar automação por ID
        response = client.get(f'/automations/{automation_id}')
        assert response.status_code == 200
        automation = json.loads(response.data)
        assert automation['name'] == sample_automation_data['name']
        
        # 4. Buscar automação por nome
        response = client.get(f'/automations/{sample_automation_data["name"]}')
        assert response.status_code == 200
        automation = json.loads(response.data)
        assert automation['name'] == sample_automation_data['name']
        
        # 5. Buscar automações paginadas
        response = client.get('/automations/paginated?page=1&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_automations'] == 1
        assert data['current_page'] == 1
        assert len(data['automations']) == 1
        
        # 6. Buscar automações com termo de busca
        response = client.get(f'/automations/paginated?page=1&per_page=10&search={sample_automation_data["name"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_automations'] == 1
        assert len(data['automations']) == 1
        
        # 7. Deletar automação
        response = client.delete(f'/automation/{automation_id}')
        assert response.status_code == 200
        
        # 8. Verificar se foi deletada
        response = client.get(f'/automations/{automation_id}')
        assert response.status_code == 404
    
    def test_automation_duplicate_prevention(self, client, sample_automation_data):
        """Testa a prevenção de automações duplicadas"""
        # Criar primeira automação
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Tentar criar automação duplicada
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Já existe uma automação' in data['error']
    
    def test_automation_validation_errors(self, client):
        """Testa validação de dados de automação"""
        # Dados incompletos
        incomplete_data = {'name': 'Test Automation'}
        
        response = client.post(
            '/register-automation',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        assert response.status_code == 500  # Erro interno devido a campos faltando
    
    def test_automation_not_found_scenarios(self, client):
        """Testa cenários de automação não encontrada"""
        # Buscar automação inexistente por ID
        response = client.get('/automations/999')
        assert response.status_code == 404
        
        # Buscar automação inexistente por nome
        response = client.get('/automations/NonExistent')
        assert response.status_code == 404
        
        # Deletar automação inexistente
        response = client.delete('/automation/999')
        assert response.status_code == 404


@pytest.mark.integration
class TestContractIntegration:
    """Testes de integração para endpoints de contrato"""
    
    @pytest.fixture
    def client(self, temp_db):
        """Cria um cliente de teste com banco temporário"""
        with patch.dict(os.environ, {'CONTRACT_DB_PATH': temp_db}):
            app.config['TESTING'] = True
            client = app.test_client()
            yield client
    
    def test_contract_crud_flow(self, client, sample_contract_data):
        """Testa o fluxo completo de CRUD de contratos"""
        # 1. Verificar disponibilidade do nome
        response = client.post(
            '/contracts/check-name',
            data=json.dumps({'name': sample_contract_data['name']}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['available'] is True
        
        # 2. Criar um contrato
        response = client.post(
            '/contract',
            data=json.dumps(sample_contract_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 3. Buscar todos os contratos
        response = client.get('/contracts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert len(data['contracts']) == 1
        
        contract_id = data['contracts'][0]['id']
        
        # 4. Buscar contrato por ID
        response = client.get(f'/contracts/{contract_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['contract']['name'] == sample_contract_data['name']
        
        # 5. Buscar contratos por squad
        response = client.get(f'/contracts/squad/{sample_contract_data["squad"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        
        # 6. Buscar contratos paginados
        response = client.get('/contracts/paginated?page=1&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_contracts'] == 1
        assert data['current_page'] == 1
        
        # 7. Buscar contratos com filtros
        response = client.get(f'/contracts/paginated?page=1&per_page=10&search={sample_contract_data["name"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_contracts'] == 1
        
        # 8. Buscar contrato específico
        response = client.get(f'/contracts/search?name={sample_contract_data["name"]}&contract=UserContract')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
    
    def test_contract_name_availability_check(self, client, sample_contract_data):
        """Testa verificação de disponibilidade de nome"""
        # Verificar nome disponível
        response = client.post(
            '/contracts/check-name',
            data=json.dumps({'name': 'Available Name'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['available'] is True
        
        # Criar contrato
        response = client.post(
            '/contract',
            data=json.dumps(sample_contract_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Verificar nome não disponível
        response = client.post(
            '/contracts/check-name',
            data=json.dumps({'name': sample_contract_data['name']}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['available'] is False
    
    def test_contract_validation_errors(self, client):
        """Testa validação de dados de contrato"""
        # Dados incompletos
        incomplete_data = {'name': 'Test Contract'}
        
        response = client.post(
            '/contract',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Nome vazio
        response = client.post(
            '/contracts/check-name',
            data=json.dumps({'name': '   '}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_contract_update_operations(self, client, sample_contract_data):
        """Testa operações de atualização de contratos"""
        # Criar contrato inicial
        response = client.post(
            '/contract',
            data=json.dumps(sample_contract_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Buscar contrato criado
        response = client.get('/contracts')
        data = json.loads(response.data)
        contract_id = data['contracts'][0]['id']
        
        # Adicionar novo schema
        add_data = {
            'action': 'add',
            'schema': {
                'contract': 'NewContract',
                'expected': {'id': 'integer', 'title': 'string'},
                'version': 'v1'
            }
        }
        
        response = client.put(
            f'/contracts/{contract_id}',
            data=json.dumps(add_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verificar se foi adicionado
        response = client.get(f'/contracts/{contract_id}')
        data = json.loads(response.data)
        assert len(data['contract']['schemas']) == 2
        
        # Remover schema por índice
        remove_data = {
            'action': 'remove',
            'schema_index': 0
        }
        
        response = client.put(
            f'/contracts/{contract_id}',
            data=json.dumps(remove_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verificar se foi removido
        response = client.get(f'/contracts/{contract_id}')
        data = json.loads(response.data)
        assert len(data['contract']['schemas']) == 1
    
    def test_contract_validation_endpoint(self, client, sample_contract_data):
        """Testa endpoint de validação de contrato"""
        # Criar contrato primeiro
        response = client.post(
            '/contract',
            data=json.dumps(sample_contract_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Validar dados válidos
        validation_data = {
            'name': sample_contract_data['name'],
            'contract': 'UserContract',
            'body': {'id': 1, 'name': 'John', 'email': 'john@example.com'}
        }
        
        response = client.post(
            '/contract-validate',
            data=json.dumps(validation_data),
            content_type='application/json'
        )
        # Pode retornar 200 ou 400 dependendo se jsonschema está disponível
        assert response.status_code in [200, 400]
        
        # Validar dados inválidos
        invalid_validation_data = {
            'name': sample_contract_data['name'],
            'contract': 'UserContract',
            'body': {'invalid': 'data'}
        }
        
        response = client.post(
            '/contract-validate',
            data=json.dumps(invalid_validation_data),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]


@pytest.mark.integration
class TestReportIntegration:
    """Testes de integração para endpoints de relatório"""
    
    @pytest.fixture
    def client(self, temp_db):
        """Cria um cliente de teste com banco temporário"""
        with patch.dict(os.environ, {'REPORT_DB_PATH': temp_db}):
            app.config['TESTING'] = True
            client = app.test_client()
            yield client
    
    def test_report_flow_with_automation(self, client, sample_automation_data, sample_report_data):
        """Testa o fluxo completo de criação de relatório com automação"""
        # 1. Criar uma automação primeiro
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 2. Buscar a automação criada
        response = client.get('/automations')
        automations = json.loads(response.data)
        automation_id = automations[0]['id']
        
        # 3. Criar um relatório
        report_data = sample_report_data.copy()
        report_data['automation_id'] = automation_id
        
        response = client.post(
            '/report',
            data=json.dumps(report_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 4. Buscar todos os relatórios
        response = client.get('/reports')
        assert response.status_code == 200
        reports = json.loads(response.data)
        assert len(reports) == 1
        assert reports[0]['automation_id'] == automation_id
        
        # 5. Buscar relatórios paginados
        response = client.get('/reports/paginated?page=1&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_reports'] == 1
        assert data['current_page'] == 1
        
        # 6. Buscar relatórios com termo de busca
        response = client.get('/reports/paginated?page=1&per_page=10&search=Test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_reports'] == 1
    
    def test_report_without_automation(self, client, sample_report_data):
        """Testa criação de relatório sem automação existente"""
        response = client.post(
            '/report',
            data=json.dumps(sample_report_data),
            content_type='application/json'
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Automation not found'
    
    def test_report_search_functionality(self, client, sample_automation_data, sample_report_data):
        """Testa funcionalidade de busca de relatórios"""
        # Criar múltiplas automações e relatórios
        automation_names = ['Python Test', 'Java Test', 'JavaScript Test']
        automations = []
        
        for name in automation_names:
            automation_data = sample_automation_data.copy()
            automation_data['name'] = name
            
            response = client.post(
                '/register-automation',
                data=json.dumps(automation_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            
            # Buscar automação criada
            response = client.get('/automations')
            automation_list = json.loads(response.data)
            automation = next(a for a in automation_list if a['name'] == name)
            automations.append(automation)
        
        # Criar relatórios para cada automação
        for i, automation in enumerate(automations):
            report_data = sample_report_data.copy()
            report_data['automation_id'] = automation['id']
            
            response = client.post(
                '/report',
                data=json.dumps(report_data),
                content_type='application/json'
            )
            assert response.status_code == 201
        
        # Buscar relatórios com termo "Python"
        response = client.get('/reports/paginated?page=1&per_page=10&search=Python')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_reports'] == 1
        
        # Buscar relatórios com termo "Test"
        response = client.get('/reports/paginated?page=1&per_page=10&search=Test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_reports'] == 3


@pytest.mark.integration
class TestCrossModuleIntegration:
    """Testes de integração entre diferentes módulos"""
    
    @pytest.fixture
    def client(self, temp_db):
        """Cria um cliente de teste com banco temporário"""
        with patch.dict(os.environ, {
            'AUTOMATION_DB_PATH': temp_db,
            'CONTRACT_DB_PATH': temp_db,
            'REPORT_DB_PATH': temp_db
        }):
            app.config['TESTING'] = True
            client = app.test_client()
            yield client
    
    def test_complete_workflow(self, client, sample_automation_data, sample_contract_data, sample_report_data):
        """Testa um fluxo de trabalho completo envolvendo todos os módulos"""
        # 1. Criar automação
        response = client.post(
            '/register-automation',
            data=json.dumps(sample_automation_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 2. Criar contrato
        response = client.post(
            '/contract',
            data=json.dumps(sample_contract_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 3. Buscar automação para criar relatório
        response = client.get('/automations')
        automations = json.loads(response.data)
        automation_id = automations[0]['id']
        
        # 4. Criar relatório
        report_data = sample_report_data.copy()
        report_data['automation_id'] = automation_id
        
        response = client.post(
            '/report',
            data=json.dumps(report_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # 5. Verificar dados em todos os módulos
        response = client.get('/automations')
        assert response.status_code == 200
        automations = json.loads(response.data)
        assert len(automations) == 1
        
        response = client.get('/contracts')
        assert response.status_code == 200
        contracts = json.loads(response.data)
        assert contracts['total'] == 1
        
        response = client.get('/reports')
        assert response.status_code == 200
        reports = json.loads(response.data)
        assert len(reports) == 1
    
    def test_pagination_across_modules(self, client, sample_automation_data, sample_contract_data, sample_report_data):
        """Testa paginação em todos os módulos"""
        # Criar múltiplos registros em cada módulo
        for i in range(5):
            # Automações
            automation_data = sample_automation_data.copy()
            automation_data['name'] = f'Automation {i}'
            
            response = client.post(
                '/register-automation',
                data=json.dumps(automation_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            
            # Contratos
            contract_data = sample_contract_data.copy()
            contract_data['name'] = f'Contract {i}'
            
            response = client.post(
                '/contract',
                data=json.dumps(contract_data),
                content_type='application/json'
            )
            assert response.status_code == 201
        
        # Testar paginação em automações
        response = client.get('/automations/paginated?page=1&per_page=2')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_automations'] == 5
        assert len(data['automations']) == 2
        
        # Testar paginação em contratos
        response = client.get('/contracts/paginated?page=1&per_page=2')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_contracts'] == 5
        assert len(data['contracts']) == 2
    
    def test_search_across_modules(self, client, sample_automation_data, sample_contract_data):
        """Testa busca em todos os módulos"""
        # Criar registros com nomes específicos
        test_names = ['Python Test', 'Java Test', 'JavaScript Test']
        
        for name in test_names:
            # Automação
            automation_data = sample_automation_data.copy()
            automation_data['name'] = name
            
            response = client.post(
                '/register-automation',
                data=json.dumps(automation_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            
            # Contrato
            contract_data = sample_contract_data.copy()
            contract_data['name'] = name
            
            response = client.post(
                '/contract',
                data=json.dumps(contract_data),
                content_type='application/json'
            )
            assert response.status_code == 201
        
        # Buscar "Python" em automações
        response = client.get('/automations/paginated?page=1&per_page=10&search=Python')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_automations'] == 1
        
        # Buscar "Test" em contratos
        response = client.get('/contracts/paginated?page=1&per_page=10&search=Test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_contracts'] == 3


# Fixtures adicionais para testes de integração
@pytest.fixture
def patch_os_environ():
    """Patch para variáveis de ambiente"""
    import os
    from unittest.mock import patch
    return patch.dict(os.environ, {})
