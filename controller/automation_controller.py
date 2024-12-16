from flask import Blueprint, request, jsonify

from service.automation_service import AutomationService

automation_controller = Blueprint('automation_controller', __name__)
automation_service = AutomationService()


@automation_controller.route('/register-automation', methods=['POST'])
def register_automation():
    data = request.get_json()

    automation_service.register_automation(
        name=data['name'],
        squad=data['squad'],
        description=data['description'],
        language=data['language'],
        cucumber=data['cucumber'],
        launch_date=data['launch_date'],
        git=data['git']
    )

    response = {
        'message': 'Dados recebidos e salvos com sucesso!',
        'received_data': data
    }

    return jsonify(response), 201


@automation_controller.route('/automations', methods=['GET'])
def get_all_automations():
    automations = automation_service.fetch_all_automations()
    return jsonify(automations), 200


@automation_controller.route('/automations/<int:automation_id>', methods=['GET'])
def get_automation_by_id(automation_id):
    automation = automation_service.get_automation_by_id(automation_id)

    if automation is None:
        return jsonify({"message": "Automation not found"}), 404

    return jsonify(automation), 200


# todo arrumar esse codigo aqui depois
@automation_controller.route('/automations/<string:automation_name>', methods=['GET'])
def get_automation_by_name(automation_name):
    automation = automation_service.get_automation_by_name(automation_name)

    if automation is None:
        return jsonify({"message": "Automation not found"}), 404

    return jsonify(automation), 200


@automation_controller.route('/automation/<int:automation_id>', methods=['DELETE'])
def delete_game(automation_id):
    result = automation_service.delete_automation(automation_id)

    if result:
        return jsonify({'message': f'Automacao com ID {automation_id} deletado com sucesso!'}), 200
    else:
        return jsonify({'error': f'Automacao com ID {automation_id} não encontrado.'}), 404
