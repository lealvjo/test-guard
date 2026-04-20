import pytest
import os
import tempfile
import sqlite3
from unittest.mock import patch
from flask import Flask

# Configuração do pytest
@pytest.fixture(scope='session')
def app():
    """Cria uma instância da aplicação Flask para testes"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Registra os blueprints
    from controller.automation_controller import automation_controller
    from controller.report_controller import report_controller
    from controller.test_contract_controller import test_contract_controller
    
    app.register_blueprint(automation_controller)
    app.register_blueprint(report_controller)
    app.register_blueprint(test_contract_controller)
    
    return app

@pytest.fixture
def client(app):
    """Cria um cliente de teste para a aplicação Flask"""
    return app.test_client()

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário para testes"""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    
    # Cria as tabelas necessárias
    conn.execute('''CREATE TABLE automations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        squad TEXT,
        description TEXT NOT NULL,
        language TEXT NOT NULL,
        cucumber TEXT NOT NULL,
        launch_date TEXT NOT NULL,
        git TEXT NOT NULL,
        image_base64 TEXT
    )''')
    
    conn.execute('''CREATE TABLE contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        squad TEXT,
        schemas TEXT NOT NULL,
        repository_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.execute('''CREATE TABLE reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        automation_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        url_report TEXT,
        report_date TEXT NOT NULL,
        name TEXT NOT NULL,
        squad TEXT NOT NULL,
        tests TEXT NOT NULL,
        FOREIGN KEY (automation_id) REFERENCES automations (id)
    )''')
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Limpa o arquivo temporário
    try:
        os.unlink(path)
    except (PermissionError, FileNotFoundError):
        # Ignora erros de permissão no Windows
        pass

@pytest.fixture
def sample_automation_data():
    """Dados de exemplo para uma automação"""
    return {
        'name': 'Test Automation',
        'squad': 'Test Squad',
        'type': 'Backend',
        'description': 'Automation for testing purposes',
        'language': 'Python',
        'cucumber': 'BDD',
        'launch_date': '2024-01-01',
        'git': 'https://github.com/test/automation',
        'image_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    }

@pytest.fixture
def sample_contract_data():
    """Dados de exemplo para um contrato"""
    return {
        'id': 1,
        'name': 'Test Contract Collection',
        'squad': 'Test Squad',
        'repository_url': 'https://github.com/test/contracts',
        'schemas': [
            {
                'contract': 'UserContract',
                'expected': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'}
                    },
                    'required': ['id', 'name', 'email']
                },
                'version': 'v1'
            }
        ]
    }

@pytest.fixture
def sample_report_data():
    """Dados de exemplo para um relatório"""
    return {
        'automation_id': 1,
        'status': 'PASSED',
        'url_report': 'https://example.com/report',
        'tests': {
            'total': 10,
            'passed': 8,
            'failed': 2
        }
    }

# Configurações do pytest
def pytest_configure(config):
    """Configurações adicionais do pytest"""
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )
