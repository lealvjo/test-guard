import sqlite3
import json
from contextlib import contextmanager


class BaseRepository:
    """
    Classe base para repositories com funcionalidades comuns
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para gerenciar conexões com o banco de dados
        
        Yields:
            sqlite3.Connection: Conexão com o banco de dados
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_with_connection(self, func):
        """
        Executa uma função com uma conexão gerenciada automaticamente
        
        Args:
            func: Função que recebe uma conexão como parâmetro
            
        Returns:
            Resultado da função
        """
        with self.get_connection() as conn:
            return func(conn)
    
    def convert_rows_to_contracts(self, rows):
        """
        Converte rows do SQLite em dicionários de contratos
        
        Args:
            rows: Rows do SQLite
            
        Returns:
            list: Lista de contratos convertidos
        """
        contracts = []
        for row in rows:
            contract = dict(row)
            if 'schemas' in contract:
                try:
                    contract['schemas'] = json.loads(contract['schemas'])
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Erro ao fazer parse do JSON do campo schemas: {e}")
                    print(f"Dados do schemas: {contract['schemas']}")
                    contract['schemas'] = []  # Valor padrão em caso de erro
            contracts.append(contract)
        return contracts
    
    def convert_rows_to_automations(self, rows):
        """
        Converte rows do SQLite em dicionários de automações
        
        Args:
            rows: Rows do SQLite
            
        Returns:
            list: Lista de automações convertidas
        """
        return [dict(row) for row in rows]
    
    def convert_rows_to_reports(self, rows):
        """
        Converte rows do SQLite em dicionários de relatórios
        
        Args:
            rows: Rows do SQLite
            
        Returns:
            list: Lista de relatórios convertidos
        """
        return [dict(row) for row in rows]
    
    def calculate_pagination(self, page, per_page):
        """
        Calcula offset para paginação
        
        Args:
            page (int): Página atual
            per_page (int): Itens por página
            
        Returns:
            int: Offset calculado
        """
        return (page - 1) * per_page
    
    def get_total_pages(self, total_items, per_page):
        """
        Calcula total de páginas
        
        Args:
            total_items (int): Total de itens
            per_page (int): Itens por página
            
        Returns:
            int: Total de páginas
        """
        return (total_items + per_page - 1) // per_page
    
    def update_schemas_in_collection(self, conn, collection_id, schemas):
        """
        Atualiza schemas de uma coleção no banco
        
        Args:
            conn: Conexão com o banco
            collection_id (int): ID da coleção
            schemas (list): Lista de schemas atualizados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        schemas_json = json.dumps(schemas)
        cursor = conn.cursor()
        cursor.execute('UPDATE contracts SET schemas = ? WHERE id = ?', (schemas_json, collection_id))
        conn.commit()
        return True
    
    def get_schemas_from_collection(self, conn, collection_id):
        """
        Busca schemas de uma coleção
        
        Args:
            conn: Conexão com o banco
            collection_id (int): ID da coleção
            
        Returns:
            list: Lista de schemas ou None se não encontrado
        """
        cursor = conn.cursor()
        cursor.execute('SELECT schemas FROM contracts WHERE id = ?', (collection_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return json.loads(row[0])
