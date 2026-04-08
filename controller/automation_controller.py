from flask import Blueprint, request, jsonify, render_template
from controller.base_controller import BaseController
from service.automation_service import AutomationService

automation_controller = Blueprint('automation_controller', __name__)
automation_service = AutomationService()


@automation_controller.route('/automations/new', methods=['GET'])
def new_automation():
    """Renderiza a página de cadastro de automação"""
    return render_template('register_automation.html')


@automation_controller.route('/automations/list', methods=['GET'])
def list_automations():
    """Renderiza a página de listagem de automações"""
    return render_template('automations_list.html')


@automation_controller.route('/register-automation', methods=['POST'])
@BaseController.handle_request
def register_automation():
    """Registra uma nova automação"""
    data = request.get_json()
    
    # Validação usando BaseController
    is_valid, error_response = BaseController.validate_required_fields(data, [
        'name', 'squad', 'type', 'description', 'language', 'cucumber', 'launch_date', 'git'
    ])
    
    if not is_valid:
        return error_response
    
    # Validação adicional
    if not data['name'].strip():
        return BaseController.error_response("Nome não pode estar vazio")
    
    # Validar tipo permitido
    allowed_types = ['Frontend', 'Backend', 'Mobile']
    if data['type'] not in allowed_types:
        return BaseController.error_response(f"Tipo '{data['type']}' não é válido. Tipos permitidos: {', '.join(allowed_types)}")
    
    try:
        # Criar automação
        automation_id = automation_service.create_automation(data)
        
        return BaseController.success_response(
            "Automação cadastrada com sucesso!",
            {"automation_id": automation_id},
            201
        )
    except Exception as e:
        return BaseController.error_response(f"Erro ao cadastrar automação: {str(e)}", 500)


@automation_controller.route('/automations', methods=['GET'])
@BaseController.handle_request
def get_automations():
    """Retorna todas as automações"""
    try:
        automations = automation_service.get_all_automations()
        return BaseController.success_response("Automações carregadas com sucesso", {"automations": automations})
    except Exception as e:
        return BaseController.error_response(f"Erro ao carregar automações: {str(e)}", 500)


@automation_controller.route('/automations/paginated', methods=['GET'])
@BaseController.handle_request
def get_paginated_automations():
    """Retorna automações paginadas"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_term = request.args.get('search', '')
    squad_filter = request.args.get('squad', '')
    type_filter = request.args.get('type', '')
    
    try:
        automations, total_automations = automation_service.get_paginated_automations(
            page, per_page, search_term, squad_filter, type_filter
        )
        
        total_pages = (total_automations + per_page - 1) // per_page
        
        return BaseController.success_response("Automações carregadas com sucesso", {
            "automations": automations,
            "total_automations": total_automations,
            "total_pages": total_pages,
            "current_page": page
        })
    except Exception as e:
        return BaseController.error_response(f"Erro ao carregar automações: {str(e)}", 500)


@automation_controller.route('/automations/<int:automation_id>', methods=['GET'])
@BaseController.handle_request
def get_automation(automation_id):
    """Retorna uma automação específica"""
    try:
        automation = automation_service.get_automation_by_id(automation_id)
        if not automation:
            return BaseController.error_response("Automação não encontrada", 404)
        
        return BaseController.success_response("Automação carregada com sucesso", {"automation": automation})
    except Exception as e:
        return BaseController.error_response(f"Erro ao carregar automação: {str(e)}", 500)


@automation_controller.route('/automations/<int:automation_id>', methods=['PUT'])
@BaseController.handle_request
def update_automation(automation_id):
    """Atualiza uma automação"""
    data = request.get_json()
    
    # Validação usando BaseController
    is_valid, error_response = BaseController.validate_required_fields(data, [
        'name', 'squad', 'type', 'description', 'language', 'cucumber', 'launch_date', 'git'
    ])
    
    if not is_valid:
        return error_response
    
    try:
        # Verificar se a automação existe
        existing_automation = automation_service.get_automation_by_id(automation_id)
        if not existing_automation:
            return BaseController.error_response("Automação não encontrada", 404)
        
        # Atualizar automação
        automation_service.update_automation(automation_id, data)
        
        return BaseController.success_response("Automação atualizada com sucesso")
    except Exception as e:
        return BaseController.error_response(f"Erro ao atualizar automação: {str(e)}", 500)


@automation_controller.route('/automations/<int:automation_id>', methods=['DELETE'])
@BaseController.handle_request
def delete_automation(automation_id):
    """Remove uma automação"""
    try:
        # Verificar se a automação existe
        existing_automation = automation_service.get_automation_by_id(automation_id)
        if not existing_automation:
            return BaseController.error_response("Automação não encontrada", 404)
        
        # Remover automação
        automation_service.delete_automation(automation_id)
        
        return BaseController.success_response("Automação removida com sucesso")
    except Exception as e:
        return BaseController.error_response(f"Erro ao remover automação: {str(e)}", 500)

