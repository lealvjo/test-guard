import sqlite3
import json
from repository.base_repository import BaseRepository

class ContractRepository(BaseRepository):
    def __init__(self, db_path='contracts.db'):
        super().__init__(db_path)
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                squad TEXT NOT NULL,
                schemas TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de logs de validação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contract_validation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id TEXT,
                collection_name TEXT NOT NULL,
                contract_name TEXT NOT NULL,
                execution_date TEXT NOT NULL,
                message TEXT NOT NULL,
                valid BOOLEAN NOT NULL,
                validated_data TEXT NOT NULL,
                validation_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def insert_contract(self, name, squad, schemas):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        schemas_json = json.dumps(schemas)
        cursor.execute('INSERT INTO contracts (name, squad, schemas, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)', 
                      (name, squad, schemas_json))
        conn.commit()
        conn.close()

    def get_all_contracts(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Configurar row_factory para retornar objetos Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contracts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        contracts = self.convert_rows_to_contracts(rows)
        conn.close()
        return contracts

    def get_paginated_contracts(self, page, per_page):
        def _get_paginated_contracts(conn):
            cursor = conn.cursor()
            
            # Contar total de contratos
            cursor.execute('SELECT COUNT(*) FROM contracts')
            total_contracts = cursor.fetchone()[0]
            
            # Calcular offset usando BaseRepository
            offset = self.calculate_pagination(page, per_page)
            
            # Buscar contratos paginados
            cursor.execute('SELECT * FROM contracts ORDER BY created_at DESC LIMIT ? OFFSET ?', 
                          (per_page, offset))
            rows = cursor.fetchall()
            
            contracts = self.convert_rows_to_contracts(rows)
            return contracts, total_contracts
        
        return self.execute_with_connection(_get_paginated_contracts)

    def insert_validation_log(self, contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error=None):
        """Insere um log de validação de contrato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validated_data_json = json.dumps(validated_data)
        validation_error_json = json.dumps(validation_error) if validation_error else None
        
        cursor.execute('''
            INSERT INTO contract_validation_logs 
            (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data_json, validation_error_json))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_validation_logs(self, limit=100, offset=0):
        """Busca logs de validação com paginação"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_by_collection(self, collection_name, limit=100, offset=0):
        """Busca logs de validação por coleção"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            WHERE collection_name = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (collection_name, limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_count(self):
        """Retorna o total de logs de validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM contract_validation_logs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_contracts_by_search(self, search_term, page, per_page):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contar total de contratos que correspondem à busca
        cursor.execute('SELECT COUNT(*) FROM contracts WHERE name LIKE ?', (f'%{search_term}%',))
        total_contracts = cursor.fetchone()[0]
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Buscar contratos paginados
        cursor.execute('SELECT * FROM contracts WHERE name LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?', 
                      (f'%{search_term}%', per_page, offset))
        rows = cursor.fetchall()
        contracts = self.convert_rows_to_contracts(rows)
        conn.close()
        
        return contracts, total_contracts

    def insert_validation_log(self, contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error=None):
        """Insere um log de validação de contrato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validated_data_json = json.dumps(validated_data)
        validation_error_json = json.dumps(validation_error) if validation_error else None
        
        cursor.execute('''
            INSERT INTO contract_validation_logs 
            (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data_json, validation_error_json))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_validation_logs(self, limit=100, offset=0):
        """Busca logs de validação com paginação"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_by_collection(self, collection_name, limit=100, offset=0):
        """Busca logs de validação por coleção"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            WHERE collection_name = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (collection_name, limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_count(self):
        """Retorna o total de logs de validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM contract_validation_logs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_contract_by_id(self, contract_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contracts WHERE id = ?', (contract_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            contracts = self.convert_rows_to_contracts([row])
            return contracts[0] if contracts else None
        return None

    def get_contracts_by_squad(self, squad):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contracts WHERE squad = ? ORDER BY created_at DESC', (squad,))
        rows = cursor.fetchall()
        contracts = self.convert_rows_to_contracts(rows)
        conn.close()
        return contracts

    def delete_contract(self, contract_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))
        conn.commit()
        conn.close()

    def search_contracts_by_name_and_contract(self, name, contract_term):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contracts WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        contracts = self.convert_rows_to_contracts([row])
        if not contracts:
            return None
            
        contract = contracts[0]
        schemas = contract['schemas']
        
        # Procurar pelo contrato específico
        for schema in schemas:
            if schema.get('contract') == contract_term:
                return {
                    'collection_name': contract['name'],
                    'contract_name': schema['contract'],
                    'schema': schema['expected']
                }
        
        return None

    def add_contract_to_collection(self, collection_id, new_schema):
        def _add_contract(conn):
            # Buscar a coleção usando método da BaseRepository
            schemas = self.get_schemas_from_collection(conn, collection_id)
            
            if not schemas:
                return None
            
            # Verificar se já existe um contrato com o mesmo nome e versão
            for schema in schemas:
                if (schema.get('contract') == new_schema.get('contract') and 
                    schema.get('version') == new_schema.get('version')):
                    raise ValueError(f"Já existe um contrato com nome '{new_schema.get('contract')}' e versão '{new_schema.get('version')}' nesta coleção")
            
            # Adicionar o novo schema
            schemas.append(new_schema)
            
            # Atualizar no banco usando método da BaseRepository
            self.update_schemas_in_collection(conn, collection_id, schemas)
            
            return schemas
        
        return self.execute_with_connection(_add_contract)

    def remove_contract_from_collection(self, collection_id, schema_index):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar a coleção
        cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        schemas = json.loads(row[0])
        
        # Verifica se o índice é válido
        if schema_index < 0 or schema_index >= len(schemas):
            return None
        
        # Remove o schema pelo índice
        removed_schema = schemas.pop(schema_index)
        
        # Atualiza no banco
        schemas_json = json.dumps(schemas)
        cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
        
        conn.commit()
        conn.close()
        
        return removed_schema

    def remove_contract_by_name_from_collection(self, collection_id, contract_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar a coleção
        cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        schemas = json.loads(row[0])
        
        # Encontrar o índice do contrato pelo nome
        contract_index = None
        for i, schema in enumerate(schemas):
            if schema.get('contract') == contract_name:
                contract_index = i
                break
        
        if contract_index is None:
            return None
        
        # Remove o schema pelo índice
        removed_schema = schemas.pop(contract_index)
        
        # Atualiza no banco
        schemas_json = json.dumps(schemas)
        cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
        
        conn.commit()
        conn.close()
        
        return removed_schema

    def update_collection_schemas(self, collection_id, new_schemas):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Validar se todos os schemas têm os campos obrigatórios
        for schema in new_schemas:
            if not isinstance(schema, dict):
                raise ValueError("Cada schema deve ser um objeto JSON")
            if 'contract' not in schema or 'expected' not in schema:
                raise ValueError("Cada schema deve ter os campos 'contract' e 'expected'")
        
        # Atualizar no banco
        schemas_json = json.dumps(new_schemas)
        cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
        
        conn.commit()
        conn.close()
        
        return True

    def update_contract_by_name_in_collection(self, collection_id, contract_name, updated_schema):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar a coleção
        cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        schemas = json.loads(row[0])
        
        # Encontrar o índice do contrato pelo nome
        contract_index = None
        for i, schema in enumerate(schemas):
            if schema.get('contract') == contract_name:
                contract_index = i
                break
        
        if contract_index is None:
            return None
        
        # Atualizar o schema
        schemas[contract_index] = updated_schema
        
        # Atualizar no banco
        schemas_json = json.dumps(schemas)
        cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
        
        conn.commit()
        conn.close()
        
        return updated_schema

    def get_contracts_by_squad_paginated(self, squad, page, per_page):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contar total de contratos da squad
        cursor.execute('SELECT COUNT(*) FROM contracts WHERE squad = ?', (squad,))
        total_contracts = cursor.fetchone()[0]
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Buscar contratos paginados
        cursor.execute('SELECT * FROM contracts WHERE squad = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', 
                      (squad, per_page, offset))
        rows = cursor.fetchall()
        contracts = self.convert_rows_to_contracts(rows)
        conn.close()
        
        return contracts, total_contracts

    def insert_validation_log(self, contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error=None):
        """Insere um log de validação de contrato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validated_data_json = json.dumps(validated_data)
        validation_error_json = json.dumps(validation_error) if validation_error else None
        
        cursor.execute('''
            INSERT INTO contract_validation_logs 
            (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data_json, validation_error_json))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_validation_logs(self, limit=100, offset=0):
        """Busca logs de validação com paginação"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_by_collection(self, collection_name, limit=100, offset=0):
        """Busca logs de validação por coleção"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            WHERE collection_name = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (collection_name, limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_count(self):
        """Retorna o total de logs de validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM contract_validation_logs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_contracts_by_search_and_squad(self, search_term, squad, page, per_page):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contar total de contratos que correspondem à busca e squad
        cursor.execute('SELECT COUNT(*) FROM contracts WHERE name LIKE ? AND squad = ?', 
                      (f'%{search_term}%', squad))
        total_contracts = cursor.fetchone()[0]
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Buscar contratos paginados
        cursor.execute('SELECT * FROM contracts WHERE name LIKE ? AND squad = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', 
                      (f'%{search_term}%', squad, per_page, offset))
        rows = cursor.fetchall()
        contracts = self.convert_rows_to_contracts(rows)
        conn.close()
        
        return contracts, total_contracts

    def insert_validation_log(self, contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error=None):
        """Insere um log de validação de contrato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validated_data_json = json.dumps(validated_data)
        validation_error_json = json.dumps(validation_error) if validation_error else None
        
        cursor.execute('''
            INSERT INTO contract_validation_logs 
            (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data_json, validation_error_json))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_validation_logs(self, limit=100, offset=0):
        """Busca logs de validação com paginação"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_by_collection(self, collection_name, limit=100, offset=0):
        """Busca logs de validação por coleção"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            WHERE collection_name = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (collection_name, limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            logs.append(log)
        
        conn.close()
        return logs

    def get_validation_logs_count(self):
        """Retorna o total de logs de validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM contract_validation_logs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_contract_validation_history(self, collection_name, contract_name, limit=3):
        """Busca histórico de validações de um contrato específico"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contract_validation_logs 
            WHERE collection_name = ? AND contract_name = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (collection_name, contract_name, limit))
        
        history = []
        for row in cursor.fetchall():
            log = dict(row)
            log['validated_data'] = json.loads(log['validated_data'])
            if log['validation_error']:
                log['validation_error'] = json.loads(log['validation_error'])
            history.append(log)
        
        conn.close()
        return history

