class BaseService:
    """
    Classe base para services com funcionalidades comuns
    """
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Valida se todos os campos obrigatórios estão presentes nos dados
        
        Args:
            data (dict): Dados a serem validados
            required_fields (list): Lista de campos obrigatórios
            
        Returns:
            tuple: (is_valid, error_message, validated_data)
        """
        for field in required_fields:
            if field not in data:
                return False, f"Campo '{field}' é obrigatório", None
        return True, None, data
    
    @staticmethod
    def find_item_by_name(items, name, name_field='name'):
        """
        Busca um item pelo nome (case insensitive)
        
        Args:
            items (list): Lista de itens para buscar
            name (str): Nome a ser buscado
            name_field (str): Campo que contém o nome
            
        Returns:
            dict: Item encontrado ou None
        """
        for item in items:
            if item.get(name_field, '').lower() == name.lower():
                return item
        return None
    
    @staticmethod
    def validate_name_uniqueness(items, new_name, name_field='name', exclude_id=None):
        """
        Valida se um nome é único na lista de itens
        
        Args:
            items (list): Lista de itens para verificar
            new_name (str): Nome a ser verificado
            name_field (str): Campo que contém o nome
            exclude_id (int): ID a ser excluído da verificação (para updates)
            
        Returns:
            tuple: (is_unique, error_message)
        """
        for item in items:
            if exclude_id and item.get('id') == exclude_id:
                continue
            if item.get(name_field, '').lower() == new_name.lower():
                return False, f"Já existe um item com o nome '{new_name}'"
        return True, None
    
    @staticmethod
    def validate_list_field(data, field_name, item_validator=None):
        """
        Valida se um campo é uma lista e opcionalmente valida cada item
        
        Args:
            data (dict): Dados a serem validados
            field_name (str): Nome do campo
            item_validator (function): Função para validar cada item da lista
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if field_name not in data:
            return False, f"Campo '{field_name}' é obrigatório"
        
        field_value = data[field_name]
        if not isinstance(field_value, list):
            return False, f"Campo '{field_name}' deve ser uma lista"
        
        if item_validator:
            for i, item in enumerate(field_value):
                is_valid, error = item_validator(item, i)
                if not is_valid:
                    return False, f"Item {i+1} em '{field_name}': {error}"
        
        return True, None
    
    @staticmethod
    def validate_contract_schema(schema, index):
        """
        Valida um schema de contrato
        
        Args:
            schema (dict): Schema a ser validado
            index (int): Índice do schema na lista
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(schema, dict):
            return False, f"Schema {index+1} deve ser um objeto"
        
        # Verifica se é a estrutura com contract + expected + version + method + endpoint
        has_contract_expected = 'contract' in schema and 'expected' in schema
        has_json_schema_fields = '$schema' in schema or 'type' in schema or 'properties' in schema
        
        if not has_contract_expected and not has_json_schema_fields:
            return False, f"Schema {index+1} deve conter 'contract' e 'expected' ou ser um JSON Schema válido"
        
        # Se tem a estrutura contract + expected, validar os novos campos
        if has_contract_expected:
            # Validar método HTTP
            if 'method' in schema:
                allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
                if schema['method'] not in allowed_methods:
                    return False, f"Schema {index+1}: Método HTTP '{schema['method']}' não é válido. Métodos permitidos: {', '.join(allowed_methods)}"
            
            # Validar endpoint
            if 'endpoint' in schema:
                endpoint = schema['endpoint']
                if not isinstance(endpoint, str):
                    return False, f"Schema {index+1}: Endpoint deve ser uma string"
                if not endpoint.startswith('/'):
                    return False, f"Schema {index+1}: Endpoint deve começar com '/'. Exemplo: /api/users"
        
        return True, None
    
    @staticmethod
    def validate_duplicate_contracts(schemas):
        """
        Valida se não há contratos duplicados (mesmo nome + versão) na lista
        
        Args:
            schemas (list): Lista de schemas
            
        Returns:
            tuple: (is_valid, error_message)
        """
        contract_versions = set()
        for i, schema in enumerate(schemas):
            if 'contract' in schema and 'version' in schema:
                contract_key = f"{schema['contract'].lower()}_{schema['version']}"
                if contract_key in contract_versions:
                    return False, f"Já existe um contrato com o nome '{schema['contract']}' na versão '{schema['version']}' na mesma coleção."
                contract_versions.add(contract_key)
        
        return True, None
    
    @staticmethod
    def add_default_version_to_schemas(schemas):
        """
        Adiciona versão padrão 'v1' aos schemas que não têm versão
        
        Args:
            schemas (list): Lista de schemas
            
        Returns:
            list: Lista de schemas com versões padrão adicionadas
        """
        for schema in schemas:
            if 'contract' in schema and 'expected' in schema and 'version' not in schema:
                schema['version'] = 'v1'
        return schemas

