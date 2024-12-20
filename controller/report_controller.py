from collections import Counter
from datetime import datetime

from flask import Blueprint, request, jsonify, render_template

from service.automation_service import AutomationService
from service.report_service import ReportService

report_controller = Blueprint('report_controller', __name__)
automation_service = AutomationService()
report_service = ReportService()


@report_controller.route('/')
def index():
    return render_template('index.html')


@report_controller.route('/report', methods=['POST'])
def register_automation():
    data = request.get_json()
    automation = automation_service.get_automation_by_id(data['automation_id'])

    if automation is None:
        return jsonify({"message": "Automation not found"}), 404

    report_service.register_report(
        automation_id=data['automation_id'],
        status=data['status'],
        url_report=data['url_report'],
        report_date=datetime.now().isoformat(),
        name=automation['name'],
        squad=automation['squad'],
        tests=data['tests']
    )

    response = {
        'message': 'Relatorio gerado com sucesso!',
        'received_data': data
    }

    return jsonify(response), 201


@report_controller.route('/reports', methods=['GET'])
def get_all_reports():
    automations = report_service.fetch_all_reports()
    return jsonify(automations), 200


@report_controller.route('/reports/paginated', methods=['GET'])
def get_paginated_reports():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_term = request.args.get('search', None)

    # Busca os relatórios paginados e o total de relatórios
    reports, total_reports = report_service.fetch_paginated_reports(page, per_page, search_term)

    # Calcula o total de páginas
    total_pages = (total_reports + per_page - 1) // per_page  # arredonda para cima

    # Retorna os relatórios junto com a informação da paginação
    return jsonify({
        'reports': reports,
        'total_reports': total_reports,
        'total_pages': total_pages,
        'current_page': page
    }), 200
