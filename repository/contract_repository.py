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
                repository_url TEXT NOT NULL,
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
                version TEXT NOT NULL,
                method TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def insert_contract(self, name, squad, schemas, repository_url):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        schemas_json = json.dumps(schemas)
        cursor.execute('INSERT INTO contracts (name, squad, schemas, repository_url, created_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)', 
                      (name, squad, schemas_json, repository_url))
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

    def insert_validation_log(self, contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error=None, version='v1.0', method='POST'):
        """Insere um log de validação de contrato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Garantir que version e method não sejam None ou vazios
        if not version or version.strip() == '':
            version = 'v1.0'
        if not method or method.strip() == '':
            method = 'POST'
        
        # Usar a mesma formatação JSON para consistência
        validated_data_json = json.dumps(validated_data, sort_keys=True, separators=(',', ':'))
        validation_error_json = json.dumps(validation_error, sort_keys=True, separators=(',', ':')) if validation_error else None
        
        cursor.execute('''
            INSERT INTO contract_validation_logs 
            (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error, version, method, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (contract_id, collection_name, contract_name, execution_date, message, valid, validated_data_json, validation_error_json, version, method))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def update_contract_by_name_in_collection(self, collection_id, contract_name, new_schema):
        """
        Atualiza um contrato específico por nome dentro de uma coleção
        
        Args:
            collection_id: ID da coleção
            contract_name: Nome do contrato a ser atualizado
            new_schema: Novo schema para o contrato
            
        Returns:
            list: Lista atualizada de schemas ou None se não encontrado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Buscar a coleção atual
            cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Carregar schemas existentes
            schemas = json.loads(result[0]) if result[0] else []
            
            # Encontrar e atualizar o contrato específico
            contract_found = False
            for i, schema in enumerate(schemas):
                schema_title = schema.get('title', '').lower()
                schema_id = schema.get('$id', '').lower()
                schema_contract = schema.get('contract', '').lower()
                
                if (contract_name.lower() in schema_title or 
                    contract_name.lower() in schema_id or 
                    contract_name.lower() in schema_contract):
                    schemas[i] = new_schema
                    contract_found = True
                    break
            
            if not contract_found:
                return None
            
            # Salvar schemas atualizados
            schemas_json = json.dumps(schemas)
            cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
            conn.commit()
            
            return schemas
            
        except Exception as e:
            print(f"Erro ao atualizar contrato: {str(e)}")
            return None
        finally:
            conn.close()

    def add_contract_to_collection(self, collection_id, new_schema):
        """
        Adiciona um novo contrato a uma coleção
        
        Args:
            collection_id: ID da coleção
            new_schema: Novo schema para adicionar
            
        Returns:
            list: Lista atualizada de schemas ou None se não encontrado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Buscar a coleção atual
            cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Carregar schemas existentes
            schemas = json.loads(result[0]) if result[0] else []
            
            # Adicionar novo schema
            schemas.append(new_schema)
            
            # Salvar schemas atualizados
            schemas_json = json.dumps(schemas)
            cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
            conn.commit()
            
            return schemas
            
        except Exception as e:
            print(f"Erro ao adicionar contrato: {str(e)}")
            return None
        finally:
            conn.close()

    def remove_contract_from_collection(self, collection_id, schema_index):
        """
        Remove um contrato de uma coleção por índice
        
        Args:
            collection_id: ID da coleção
            schema_index: Índice do schema a ser removido
            
        Returns:
            dict: Schema removido ou None se não encontrado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Buscar a coleção atual
            cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Carregar schemas existentes
            schemas = json.loads(result[0]) if result[0] else []
            
            # Verificar se o índice é válido
            if schema_index < 0 or schema_index >= len(schemas):
                return None
            
            # Remover schema
            removed_schema = schemas.pop(schema_index)
            
            # Salvar schemas atualizados
            schemas_json = json.dumps(schemas)
            cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
            conn.commit()
            
            return removed_schema
            
        except Exception as e:
            print(f"Erro ao remover contrato: {str(e)}")
            return None
        finally:
            conn.close()

    def remove_contract_by_name_from_collection(self, collection_id, contract_name):
        """
        Remove um contrato de uma coleção por nome
        
        Args:
            collection_id: ID da coleção
            contract_name: Nome do contrato a ser removido
            
        Returns:
            dict: Schema removido ou None se não encontrado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Buscar a coleção atual
            cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Carregar schemas existentes
            schemas = json.loads(result[0]) if result[0] else []
            
            # Encontrar e remover o contrato específico
            removed_schema = None
            for i, schema in enumerate(schemas):
                schema_title = schema.get('title', '').lower()
                schema_id = schema.get('$id', '').lower()
                schema_contract = schema.get('contract', '').lower()
                
                if (contract_name.lower() in schema_title or 
                    contract_name.lower() in schema_id or 
                    contract_name.lower() in schema_contract):
                    removed_schema = schemas.pop(i)
                    break
            
            if removed_schema is None:
                return None
            
            # Salvar schemas atualizados
            schemas_json = json.dumps(schemas)
            cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
            conn.commit()
            
            return removed_schema
            
        except Exception as e:
            print(f"Erro ao remover contrato por nome: {str(e)}")
            return None
        finally:
            conn.close()

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

    def get_contract_schema_by_name(self, collection_name, contract_name):
        """Busca o schema de um contrato específico por nome da coleção e nome do contrato"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT schemas FROM contracts WHERE name = ?', (collection_name,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row['schemas']:
            try:
                schemas = json.loads(row['schemas'])
                # Procurar pelo contrato específico nos schemas
                for schema in schemas:
                    if schema.get('name') == contract_name:
                        return schema
            except json.JSONDecodeError:
                pass
        return None

    def update_collection_schemas(self, collection_id, schemas):
        """Atualiza os schemas de uma coleção específica"""
        try:
            def _update_schemas(conn):
                schemas_json = json.dumps(schemas)
                cursor = conn.cursor()
                cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    # Buscar a coleção atualizada
                    cursor.execute('SELECT * FROM contracts WHERE id = ?', (collection_id,))
                    row = cursor.fetchone()
                    if row:
                        contracts = self.convert_rows_to_contracts([row])
                        return contracts[0]['schemas'] if contracts else None
                return None
            
            return self.execute_with_connection(_update_schemas)
        except Exception as e:
            print(f"Erro ao atualizar schemas da coleção: {str(e)}")
            return None

    def search_contracts_by_name_and_contract(self, collection_name, contract_name):
        """Busca contratos por nome da coleção e nome do contrato"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar coleções que coincidem com o nome
        cursor.execute('SELECT * FROM contracts WHERE name LIKE ?', (f'%{collection_name}%',))
        rows = cursor.fetchall()
        contracts = self.convert_rows_to_contracts(rows)
        conn.close()
        
        # Filtrar por contrato específico nos schemas
        matching_contracts = []
        for contract in contracts:
            if contract['schemas']:
                for schema in contract['schemas']:
                    if isinstance(schema, dict):
                        # Verificar se é a estrutura antiga (contract + expected)
                        if 'contract' in schema and contract_name.lower() in schema['contract'].lower():
                            matching_contracts.append(contract)
                            break
                        # Verificar se é JSON Schema direto
                        elif isinstance(schema, dict):
                            schema_title = schema.get('title', '').lower()
                            schema_id = schema.get('$id', '').lower()
                            if contract_name.lower() in schema_title or contract_name.lower() in schema_id:
                                matching_contracts.append(contract)
                                break
        
        return matching_contracts

    def check_recent_duplicate_body(self, collection_name, contract_name, body_to_validate, version='v1.0', method='POST', time_window_minutes=2):
        """
        Verifica se já existe um log recente com o mesmo body, version e method
        
        Args:
            collection_name: Nome da coleção
            contract_name: Nome do contrato
            body_to_validate: Body para validar
            version: Versão do contrato
            method: Método HTTP
            time_window_minutes: Janela de tempo para considerar "recente" (padrão: 2 minutos)
        
        Returns:
            bool: True se encontrar duplicata recente, False caso contrário
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Converter body para JSON string para comparação (com sort_keys para consistência)
        body_json = json.dumps(body_to_validate, sort_keys=True, separators=(',', ':'))
        
        # Buscar logs recentes com mesmo body, version e method - usar CURRENT_TIMESTAMP para compatibilidade
        cursor.execute('''
            SELECT COUNT(*) FROM contract_validation_logs 
            WHERE collection_name = ? 
            AND contract_name = ? 
            AND validated_data = ?
            AND version = ?
            AND method = ?
            AND created_at > datetime('now', '-{} minutes')
        '''.format(time_window_minutes), (collection_name, contract_name, body_json, version, method))
        
        count = cursor.fetchone()[0]
        
        # Se não encontrou com CURRENT_TIMESTAMP, tentar com datetime('now')
        if count == 0:
            cursor.execute('''
                SELECT COUNT(*) FROM contract_validation_logs 
                WHERE collection_name = ? 
                AND contract_name = ? 
                AND validated_data = ?
                AND version = ?
                AND method = ?
                AND datetime(created_at) > datetime('now', '-{} minutes')
            '''.format(time_window_minutes), (collection_name, contract_name, body_json, version, method))
            
            count = cursor.fetchone()[0]
        
        conn.close()
        
        return count > 0

    def save_validation_log_with_deduplication(self, contract_id, collection_name, contract_name, 
                                             execution_date, message, valid, validated_data, 
                                             validation_error=None, skip_duplicates=True, version='v1.0', method='POST'):
        """
        Salva log de validação com verificação de duplicatas
        
        Args:
            skip_duplicates: Se True, não salva se encontrar duplicata recente
        """
        if skip_duplicates:
            # Verificar se já existe uma execução recente com o mesmo body, version e method
            if self.check_recent_duplicate_body(collection_name, contract_name, validated_data, version, method):
                print(f"Log duplicado detectado para {collection_name}/{contract_name} (v{version}, {method}), pulando salvamento")
                return None  # Não salvar
        
        # Salvar normalmente
        return self.insert_validation_log(
            contract_id=contract_id,
            collection_name=collection_name,
            contract_name=contract_name,
            execution_date=execution_date,
            message=message,
            valid=valid,
            validated_data=validated_data,
            validation_error=validation_error,
            version=version,
            method=method
        )

