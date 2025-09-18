from repository.contract_repository import ContractRepository
from service.base_service import BaseService

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class ContractService(BaseService):
    def __init__(self):
        self.contract_repository = ContractRepository()

    def validate_contract_data(self, data):
        """
        Valida os dados de entrada para criação de contrato
        
        Args:
            data (dict): Dados do contrato
            
        Returns:
            tuple: (is_valid, error_message, validated_data)
        """
        # Validação de campos obrigatórios usando BaseService
        is_valid, error_message, validated_data = self.validate_required_fields(data, ['name', 'squad', 'schemas', 'repository_url'])
        if not is_valid:
            return False, error_message, None
        
        # Campo obrigatório repository_url
        repository_url = validated_data['repository_url'].strip() if validated_data['repository_url'] else None
        
        # Validação específica do repository_url
        if not repository_url:
            return False, "URL do repositório é obrigatória", None
        
        name = validated_data['name']
        squad = validated_data['squad']
        schemas = validated_data['schemas']
        
        # Validação de nome único usando BaseService
        existing_contracts = self.contract_repository.get_all_contracts()
        is_unique, error_message = self.validate_name_uniqueness(existing_contracts, name)
        if not is_unique:
            return False, f"Já existe uma coleção com o nome '{name}'. Escolha um nome diferente.", None
        
        # Validação de schemas usando BaseService
        is_valid, error_message = self.validate_list_field({'schemas': schemas}, 'schemas', self.validate_contract_schema)
        if not is_valid:
            return False, error_message, None
        
        # Adicionar versão padrão usando BaseService
        schemas = self.add_default_version_to_schemas(schemas)
        
        # Validação de duplicatas usando BaseService
        is_valid, error_message = self.validate_duplicate_contracts(schemas)
        if not is_valid:
            return False, error_message, None
        
        return True, None, {
            'name': name,
            'squad': squad,
            'schemas': schemas,
            'repository_url': repository_url
        }

    def create_contract(self, data):
        """
        Cria um novo contrato
        
        Args:
            data (dict): Dados do contrato
            
        Returns:
            tuple: (success, result_data, error_message)
        """
        is_valid, error_message, validated_data = self.validate_contract_data(data)
        
        if not is_valid:
            return False, None, error_message
        
        try:
            self.contract_repository.insert_contract(
                validated_data['name'],
                validated_data['squad'],
                validated_data['schemas'],
                validated_data['repository_url']
            )
            
            result_data = {
                'message': 'Coleção de contratos salva com sucesso!',
                'received_data': {
                    'name': validated_data['name'],
                    'squad': validated_data['squad'],
                    'repository_url': validated_data['repository_url'],
                    'schemas_count': len(validated_data['schemas']),
                    'schemas': validated_data['schemas']
                }
            }
            
            return True, result_data, None
            
        except Exception as e:
            return False, None, f"Erro ao salvar contrato: {str(e)}"

    def validate_contract_update_data(self, data):
        """
        Valida os dados de entrada para atualização de contrato
        
        Args:
            data (dict): Dados da atualização
            
        Returns:
            tuple: (is_valid, error_message, action_type, validated_data)
        """
        action = data.get('action')
        
        if action == 'add':
            new_schema = data.get('schema')
            if not new_schema:
                return False, "Campo 'schema' é obrigatório para ação 'add'", None, None
            return True, None, 'add', {'schema': new_schema}
            
        elif action == 'remove':
            schema_index = data.get('schema_index')
            contract_name = data.get('contract_name')
            
            if schema_index is not None:
                return True, None, 'remove_by_index', {'schema_index': schema_index}
            elif contract_name is not None:
                return True, None, 'remove_by_name', {'contract_name': contract_name}
            else:
                return False, "Campo 'schema_index' ou 'contract_name' é obrigatório para ação 'remove'", None, None
                
        elif action == 'update':
            contract_name = data.get('contract_name')
            updated_schema = data.get('schema')
            new_schemas = data.get('schemas')
            
            if contract_name is not None and updated_schema is not None:
                return True, None, 'update_by_name', {'contract_name': contract_name, 'schema': updated_schema}
            elif new_schemas is not None:
                return True, None, 'update_complete', {'schemas': new_schemas}
            else:
                return False, "Para atualização por nome use 'contract_name' e 'schema', para atualização completa use 'schemas'", None, None
                
        # Suporte ao formato da modal de edição (sem action)
        elif 'contract_name' in data and 'schema' in data and 'action' not in data:
            return True, None, 'update_by_name_direct', {'contract_name': data['contract_name'], 'schema': data['schema']}
                
        else:
            return False, "Ação inválida. Use 'add', 'remove' ou 'update'", None, None

    def validate_contract(self, collection_name, contract_name, body_to_validate):
        """
        Valida um body contra um contrato específico de uma coleção
        
        Args:
            collection_name (str): Nome da coleção
            contract_name (str): Nome do contrato específico
            body_to_validate (dict): Dados para validar
            
        Returns:
            dict: Resultado da validação
        """
        if not JSONSCHEMA_AVAILABLE:
            return {
                'valid': False,
                'error': 'Biblioteca jsonschema não está instalada. Execute: pip install jsonschema'
            }

        try:
            # Busca a coleção usando BaseService
            contracts = self.contract_repository.get_all_contracts()
            collection = self.find_item_by_name(contracts, collection_name)
            
            if not collection:
                return {
                    'valid': False,
                    'error': f'Coleção "{collection_name}" não encontrada'
                }

            # Busca o contrato específico dentro da coleção
            target_schema = None
            contract_index = None
            
            # Verificar se schemas é uma lista válida
            if not isinstance(collection['schemas'], list):
                return {
                    'valid': False,
                    'error': f'Formato inválido de schemas na coleção "{collection_name}". Tipo: {type(collection["schemas"])}'
                }
            
            for i, schema in enumerate(collection['schemas']):
                # Verifica se é a estrutura antiga (contract + expected)
                if 'contract' in schema and contract_name.lower() in schema['contract'].lower():
                    target_schema = schema['expected']
                    contract_index = i
                    break
                # Verifica se é JSON Schema direto
                elif isinstance(schema, dict):
                    schema_title = schema.get('title', '').lower()
                    schema_id = schema.get('$id', '').lower()
                    if contract_name.lower() in schema_title or contract_name.lower() in schema_id:
                        target_schema = schema
                        contract_index = i
                        break

            if not target_schema:
                return {
                    'valid': False,
                    'error': f'Contrato "{contract_name}" não encontrado na coleção "{collection_name}"'
                }

            # Valida o body contra o schema
            # Criar ID único para o contrato específico
            contract_id = f"{collection['id']}-{contract_index}"
            
            # Validar se o schema é válido antes de usar
            if not isinstance(target_schema, dict):
                return {
                    'valid': False,
                    'error': f'Schema inválido para o contrato "{contract_name}". Schema deve ser um objeto JSON válido.',
                    'collection_name': collection_name,
                    'contract_name': contract_name,
                    'validated_data': body_to_validate,
                    'contract_id': contract_id
                }
            
            # Verificar se o schema tem pelo menos um campo obrigatório do JSON Schema
            if not any(key in target_schema for key in ['type', 'properties', '$schema', 'items']):
                return {
                    'valid': False,
                    'error': f'Schema inválido para o contrato "{contract_name}". Schema deve conter pelo menos um dos campos: type, properties, $schema ou items.',
                    'collection_name': collection_name,
                    'contract_name': contract_name,
                    'validated_data': body_to_validate,
                    'contract_id': contract_id
                }
            
            validate(instance=body_to_validate, schema=target_schema)
            
            return {
                'valid': True,
                'message': 'Validação bem-sucedida!',
                'collection_name': collection_name,
                'contract_name': contract_name,
                'validated_data': body_to_validate,
                'contract_id': contract_id
            }

        except ValidationError as e:
            # Criar ID único para o contrato específico (se encontrado)
            contract_id = None
            if 'collection' in locals() and 'contract_index' in locals() and contract_index is not None:
                contract_id = f"{collection['id']}-{contract_index}"
            
            return {
                'valid': False,
                'error': f'Erro de validação: {e.message}',
                'validation_error': {
                    'message': e.message,
                    'path': list(e.absolute_path) if e.absolute_path else [],
                    'schema_path': list(e.schema_path) if e.schema_path else []
                },
                'collection_name': collection_name,
                'contract_name': contract_name,
                'validated_data': body_to_validate,
                'contract_id': contract_id
            }
        except Exception as e:
            # Criar ID único para o contrato específico (se encontrado)
            contract_id = None
            if 'collection' in locals() and 'contract_index' in locals() and contract_index is not None:
                contract_id = f"{collection['id']}-{contract_index}"
            
            return {
                'valid': False,
                'error': f'Erro interno: {str(e)}',
                'collection_name': collection_name,
                'contract_name': contract_name,
                'validated_data': body_to_validate,
                'contract_id': contract_id
            }

    def save_validation_log(self, contract_id, collection_name, contract_name, execution_date, message, valid, validated_data, validation_error=None, skip_duplicates=True, version='v1.0', method='POST'):
        """Salva um log de validação de contrato com verificação de duplicatas"""
        try:
            log_id = self.contract_repository.save_validation_log_with_deduplication(
                contract_id=contract_id,
                collection_name=collection_name,
                contract_name=contract_name,
                execution_date=execution_date,
                message=message,
                valid=valid,
                validated_data=validated_data,
                validation_error=validation_error,
                skip_duplicates=skip_duplicates,
                version=version,
                method=method
            )
            return log_id
        except Exception as e:
            print(f"Erro ao salvar log de validação: {str(e)}")
            return None

    def get_validation_logs(self, limit=100, offset=0):
        """Busca logs de validação com paginação"""
        try:
            return self.contract_repository.get_validation_logs(limit, offset)
        except Exception as e:
            print(f"Erro ao buscar logs de validação: {str(e)}")
            return []

    def get_contract_validation_history(self, collection_name, contract_name, limit=3):
        """Busca histórico de validações de um contrato específico"""
        try:
            return self.contract_repository.get_contract_validation_history(collection_name, contract_name, limit)
        except Exception as e:
            print(f"Erro ao buscar histórico de validação: {str(e)}")
            return []

    def get_validation_logs_by_collection(self, collection_name, limit=100, offset=0):
        """Busca logs de validação por coleção"""
        try:
            return self.contract_repository.get_validation_logs_by_collection(collection_name, limit, offset)
        except Exception as e:
            print(f"Erro ao buscar logs de validação por coleção: {str(e)}")
            return []

    def get_validation_logs_count(self):
        """Retorna o total de logs de validação"""
        try:
            return self.contract_repository.get_validation_logs_count()
        except Exception as e:
            print(f"Erro ao contar logs de validação: {str(e)}")
            return 0
