from flask import Blueprint, request, jsonify, render_template
from repository.contract_repository import ContractRepository
from service.contract_service import ContractService
from controller.base_controller import BaseController
from datetime import datetime
from service.base_service import BaseService
import subprocess
import json
import re

test_contract_controller = Blueprint('test_contract_controller', __name__)
contract_repository = ContractRepository()
contract_service = ContractService()


@test_contract_controller.route('/contracts/new', methods=['GET'])
def new_contract_form():
    return render_template('register_contract.html')


@test_contract_controller.route('/contracts/list', methods=['GET'])
def contracts_list():
    return render_template('contracts_list.html')


@test_contract_controller.route('/schema-generator', methods=['GET'])
def schema_generator():
    """Renderiza a página do gerador de schema"""
    return render_template('schema_generator.html')


@test_contract_controller.route('/contracts/check-name', methods=['POST'])
@BaseController.handle_request
def check_contract_name():
    data = request.get_json()
    
    # Validação usando BaseController
    is_valid, error_response = BaseController.validate_required_fields(data, ['name'])
    if not is_valid:
        return error_response
    
    name = data['name'].strip()
    
    if not name:
        return BaseController.error_response("Nome não pode estar vazio")
    
    # Usa o service para verificar disponibilidade
    contracts = contract_repository.get_all_contracts()
    existing_contract = BaseService.find_item_by_name(contracts, name)
    
    if existing_contract:
        return BaseController.success_response(
            f"Já existe uma coleção com o nome '{name}'",
            {"available": False}
        )
    
    return BaseController.success_response(
        f"Nome '{name}' está disponível",
        {"available": True}
    )


@test_contract_controller.route('/contract', methods=['POST'])
@BaseController.handle_request
def contract():
    data = request.get_json()
    
    # Usa o service para validar e criar o contrato
    success, result_data, error_message = contract_service.create_contract(data)
    
    if success:
        return BaseController.success_response(
            result_data['message'],
            result_data,
            201
        )
    else:
        return BaseController.error_response(error_message)


@test_contract_controller.route('/contracts-dash')
def contracts_dashboard():
    return render_template('contracts_dashboard.html')


@test_contract_controller.route('/contracts', methods=['GET'])
def get_all_contracts():
    try:
        contracts = contract_repository.get_all_contracts()
        return jsonify({
            'message': 'Contratos recuperados com sucesso!',
            'contracts': contracts,
            'total': len(contracts)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao recuperar contratos: {str(e)}"}), 500


@test_contract_controller.route('/contracts/paginated', methods=['GET'])
def get_paginated_contracts():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search_term = request.args.get('search', None)
        squad_filter = request.args.get('squad', None)

        if search_term and squad_filter:
            # Busca por nome E squad
            contracts, total_contracts = contract_repository.get_contracts_by_search_and_squad(search_term, squad_filter, page, per_page)
        elif search_term:
            contracts, total_contracts = contract_repository.get_contracts_by_search(search_term, page, per_page)
        elif squad_filter:
            contracts, total_contracts = contract_repository.get_contracts_by_squad_paginated(squad_filter, page, per_page)
        else:
            contracts, total_contracts = contract_repository.get_paginated_contracts(page, per_page)

        # Calcula o total de páginas
        total_pages = (total_contracts + per_page - 1) // per_page

        return jsonify({
            'contracts': contracts,
            'total_contracts': total_contracts,
            'total_pages': total_pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao recuperar contratos: {str(e)}"}), 500


@test_contract_controller.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract_by_id(contract_id):
    try:
        contract = contract_repository.get_contract_by_id(contract_id)
        
        if contract is None:
            return jsonify({"error": "Contrato não encontrado"}), 404
        
        return jsonify({
            'message': 'Contrato recuperado com sucesso!',
            'contract': contract
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao recuperar contrato: {str(e)}"}), 500


@test_contract_controller.route('/contracts/squad/<string:squad>', methods=['GET'])
def get_contracts_by_squad(squad):
    try:
        contracts = contract_repository.get_contracts_by_squad(squad)
        return jsonify({
            'message': f'Contratos da squad {squad} recuperados com sucesso!',
            'contracts': contracts,
            'total': len(contracts)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao recuperar contratos da squad: {str(e)}"}), 500


@test_contract_controller.route('/contracts/search', methods=['GET'])
def search_contracts_by_name_and_contract():
    try:
        name = request.args.get('name')
        contract_term = request.args.get('contract')
        
        if not name:
            return jsonify({"error": "Parâmetro 'name' é obrigatório"}), 400
        
        if not contract_term:
            return jsonify({"error": "Parâmetro 'contract' é obrigatório"}), 400
        
        contracts = contract_repository.search_contracts_by_name_and_contract(name, contract_term)
        
        return jsonify({
            'message': 'Busca realizada com sucesso!',
            'search_params': {
                'name': name,
                'contract': contract_term
            },
            'contracts': contracts,
            'total': len(contracts)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar contratos: {str(e)}"}), 500


@test_contract_controller.route('/contracts/<int:collection_id>', methods=['PUT'])
def update_collection_contracts(collection_id):
    try:
        data = request.get_json()
        
        # Valida os dados usando o service
        is_valid, error_message, action_type, validated_data = contract_service.validate_contract_update_data(data)
        
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Executa a ação baseada no tipo
        if action_type == 'add':
            updated_schemas = contract_repository.add_contract_to_collection(collection_id, validated_data['schema'])
            if updated_schemas is None:
                return jsonify({"error": "Coleção não encontrada"}), 404
            
            return jsonify({
                'message': 'Contrato adicionado à coleção com sucesso!',
                'collection_id': collection_id,
                'schemas_count': len(updated_schemas),
                'schemas': updated_schemas
            }), 200
            
        elif action_type == 'remove_by_index':
            removed_schema = contract_repository.remove_contract_from_collection(collection_id, validated_data['schema_index'])
            if removed_schema is None:
                return jsonify({"error": "Coleção não encontrada ou índice inválido"}), 404
            
            return jsonify({
                'message': 'Contrato removido da coleção com sucesso!',
                'collection_id': collection_id,
                'removed_by': 'index',
                'removed_schema': removed_schema
            }), 200
            
        elif action_type == 'remove_by_name':
            removed_schema = contract_repository.remove_contract_by_name_from_collection(collection_id, validated_data['contract_name'])
            if removed_schema is None:
                return jsonify({"error": "Coleção não encontrada ou contrato não encontrado"}), 404
            
            return jsonify({
                'message': 'Contrato removido da coleção com sucesso!',
                'collection_id': collection_id,
                'removed_by': 'name',
                'contract_name': validated_data['contract_name'],
                'removed_schema': removed_schema
            }), 200
            
        elif action_type == 'update_by_name':
            updated_schemas = contract_repository.update_contract_by_name_in_collection(collection_id, validated_data['contract_name'], validated_data['schema'])
            if updated_schemas is None:
                return jsonify({"error": "Coleção não encontrada ou contrato não encontrado"}), 404
            
            return jsonify({
                'message': 'Contrato atualizado com sucesso!',
                'collection_id': collection_id,
                'updated_by': 'name',
                'contract_name': validated_data['contract_name'],
                'schemas_count': len(updated_schemas),
                'schemas': updated_schemas
            }), 200
            
        elif action_type == 'update_by_name_direct':
            # Suporte ao formato da modal de edição
            updated_schemas = contract_repository.update_contract_by_name_in_collection(collection_id, validated_data['contract_name'], validated_data['schema'])
            if updated_schemas is None:
                return jsonify({"error": "Coleção não encontrada ou contrato não encontrado"}), 404
            
            return jsonify({
                'message': 'Contrato atualizado com sucesso!',
                'collection_id': collection_id,
                'contract_name': validated_data['contract_name'],
                'schemas_count': len(updated_schemas),
                'schemas': updated_schemas
            }), 200
            
        elif action_type == 'update_complete':
            updated_schemas = contract_repository.update_collection_schemas(collection_id, validated_data['schemas'])
            if updated_schemas is None:
                return jsonify({"error": "Coleção não encontrada"}), 404
            
            return jsonify({
                'message': 'Coleção atualizada com sucesso!',
                'collection_id': collection_id,
                'updated_by': 'complete',
                'schemas_count': len(updated_schemas),
                'schemas': updated_schemas
            }), 200
            
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar coleção: {str(e)}"}), 500

@test_contract_controller.route('/contract-validate', methods=['POST'])
@BaseController.handle_request
def validate_contract():
    data = request.get_json()
    
    # Validação dos campos obrigatórios - aceita ambos os formatos
    # Formato novo: collection_name, contract_name, body_to_validate
    # Formato antigo: name, contract, body
    if 'collection_name' in data and 'contract_name' in data and 'body_to_validate' in data:
        collection_name = data['collection_name']
        contract_name = data['contract_name']
        body_to_validate = data['body_to_validate']
    elif 'name' in data and 'contract' in data and 'body' in data:
        collection_name = data['name']
        contract_name = data['contract']
        body_to_validate = data['body']
    else:
        return BaseController.error_response("Campos obrigatórios: collection_name, contract_name, body_to_validate (ou name, contract, body)")
    
    # Campos opcionais
    version = data.get('version', 'v1.0')
    method = data.get('method', 'POST')
    
    # Validação do body - aceita tanto objeto quanto array
    if not isinstance(body_to_validate, (dict, list)):
        return BaseController.error_response("Campo 'body' deve ser um objeto JSON ou array")
    
    # Chama o service para validar
    validation_result = contract_service.validate_contract(
        collection_name, 
        contract_name, 
        body_to_validate
    )
    
    # Retorna o resultado da validação
    execution_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if validation_result['valid']:
        # Salvar log de sucesso
        contract_service.save_validation_log(
            contract_id=validation_result.get('contract_id'),
            collection_name=validation_result.get('collection_name', ''),
            contract_name=validation_result.get('contract_name', ''),
            execution_date=execution_date,
            message=validation_result.get('message', ''),
            valid=True,
            validated_data=validation_result.get('validated_data', []),
            validation_error=None,
            version=version,
            method=method
        )
        
        return BaseController.success_response(
            validation_result['message'],
            {
                'collection_name': validation_result.get('collection_name', ''),
                'contract_name': validation_result.get('contract_name', ''),
                'message': validation_result.get('message', ''),
                'valid': validation_result.get('valid', True),
                'validated_data': validation_result.get('validated_data', {}),
                'contract_id': validation_result.get('contract_id'),
                'execution_date': execution_date,
                'version': version,
                'method': method
            }
        )
    else:
        # Salvar log de erro
        contract_service.save_validation_log(
            contract_id=validation_result.get('contract_id'),
            collection_name=validation_result.get('collection_name', ''),
            contract_name=validation_result.get('contract_name', ''),
            execution_date=execution_date,
            message=validation_result.get('error', 'Erro na validação'),
            valid=False,
            validated_data=validation_result.get('validated_data', []),
            validation_error=validation_result.get('validation_error', None)
        )
        
        # Retorna erro no mesmo formato do sucesso, mas com valid: false
        return jsonify({
            "collection_name": validation_result.get('collection_name', ''),
            "contract_name": validation_result.get('contract_name', ''),
            "message": validation_result.get('error', 'Erro na validação'),
            "valid": False,
            "validated_data": validation_result.get('validated_data', []),
            "validation_error": validation_result.get('validation_error', None),
            "execution_date": execution_date,
            "contract_id": validation_result.get('contract_id'),
            "version": version,
            "method": method
        }), 400

@test_contract_controller.route('/contract-validation-logs', methods=['GET'])
@BaseController.handle_request
def get_validation_logs():
    """Endpoint para buscar logs de validação de contratos"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        collection_name = request.args.get('collection_name', None)
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Buscar logs
        if collection_name:
            logs = contract_service.get_validation_logs_by_collection(collection_name, per_page, offset)
        else:
            logs = contract_service.get_validation_logs(per_page, offset)
        
        total_count = contract_service.get_validation_logs_count()
        
        return BaseController.success_response(
            "Logs de validação recuperados com sucesso",
            {
                "logs": logs,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page
                }
            }
        )
    except Exception as e:
        return BaseController.error_response(f"Erro ao buscar logs de validação: {str(e)}", 500)

@test_contract_controller.route('/contract-validation-history', methods=['GET'])
@BaseController.handle_request
def get_contract_validation_history():
    """Endpoint para buscar histórico de validações de um contrato específico"""
    try:
        collection_name = request.args.get('collection_name')
        contract_name = request.args.get('contract_name')
        limit = request.args.get('limit', 3, type=int)
        
        if not collection_name or not contract_name:
            return BaseController.error_response("Parâmetros collection_name e contract_name são obrigatórios")
        
        history = contract_service.get_contract_validation_history(collection_name, contract_name, limit)
        
        return BaseController.success_response(
            f"Histórico encontrado: {len(history)} execuções",
            {"history": history}
        )
    except Exception as e:
        return BaseController.error_response(f"Erro ao buscar histórico: {str(e)}")

@test_contract_controller.route('/execute-curl', methods=['POST'])
@BaseController.handle_request
def execute_curl():
    """Endpoint para executar curl e extrair response body"""
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        is_valid, error_response = BaseController.validate_required_fields(data, ['curl_command'])
        if not is_valid:
            return error_response
        
        curl_command = data['curl_command'].strip()
        
        if not curl_command:
            return BaseController.error_response("Comando curl não pode estar vazio")
        
        # Validar se é um comando curl válido
        if not curl_command.startswith('curl'):
            return BaseController.error_response("Comando deve começar com 'curl'")
        
        # Executar o comando curl
        try:
            # Usar shell=True para Windows e Linux
            result = subprocess.run(
                curl_command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30  # Timeout de 30 segundos
            )
            
            if result.returncode != 0:
                return BaseController.error_response(f"Erro ao executar curl: {result.stderr}")
            
            # Extrair response body do output do curl
            response_output = result.stdout
            
            # Tentar extrair JSON do response
            response_body = extract_json_from_curl_output(response_output)
            
            if response_body is None:
                return BaseController.error_response("Não foi possível extrair JSON válido da resposta do curl")
            
            return BaseController.success_response(
                "Curl executado com sucesso",
                {
                    "response_body": response_body,
                    "raw_output": response_output
                }
            )
            
        except subprocess.TimeoutExpired:
            return BaseController.error_response("Timeout: O comando curl demorou mais de 30 segundos para executar")
        except Exception as e:
            return BaseController.error_response(f"Erro ao executar curl: {str(e)}")
            
    except Exception as e:
        return BaseController.error_response(f"Erro interno: {str(e)}")

def extract_json_from_curl_output(output):
    """Extrai JSON da saída do comando curl"""
    try:
        # Remover headers HTTP se existirem
        lines = output.split('\n')
        json_start = -1
        
        # Procurar por início de JSON
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('{') or line.startswith('['):
                json_start = i
                break
        
        if json_start == -1:
            return None
        
        # Juntar linhas a partir do início do JSON
        json_lines = lines[json_start:]
        json_text = '\n'.join(json_lines)
        
        # Tentar fazer parse do JSON
        parsed_json = json.loads(json_text)
        return parsed_json
        
    except json.JSONDecodeError:
        # Se não conseguir fazer parse, tentar extrair JSON usando regex
        try:
            # Procurar por padrões JSON na saída
            json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])'
            matches = re.findall(json_pattern, output, re.DOTALL)
            
            for match in matches:
                try:
                    parsed_json = json.loads(match)
                    return parsed_json
                except json.JSONDecodeError:
                    continue
            
            return None
        except Exception:
            return None
    except Exception:
        return None
