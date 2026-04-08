from collections import Counter
from datetime import datetime

from flask import Blueprint, request, jsonify, render_template

from service.automation_service import AutomationService
from service.report_service import ReportService

report_controller = Blueprint('report_controller', __name__)
automation_service = AutomationService()
report_service = ReportService()


@report_controller.route('/dash')
def dash():
    return render_template('execution_dashboard.html')


@report_controller.route('/')
def index():
    return render_template('index.html')


@report_controller.route('/report', methods=['POST'])
def register_automation():
    data = request.get_json()
    junit = data.get('junit', None)

    if junit is not None and not isinstance(junit, dict):
        return jsonify({"message": "Campo 'junit' deve ser um objeto JSON ou null"}), 400

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
        tests=data['tests'],
        junit=junit
    )

    response = {
        'message': 'Relatorio gerado com sucesso!',
        'received_data': data
    }

    return jsonify(response), 201


@report_controller.route('/reports', methods=['GET'])
def get_all_reports():
    reports = report_service.fetch_all_reports()
    return jsonify(reports), 200


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


def _collect_testcases(node):
    testcases = []
    if isinstance(node, dict):
        if 'testcase' in node:
            raw_testcases = node['testcase']
            if isinstance(raw_testcases, dict):
                testcases.append(raw_testcases)
            elif isinstance(raw_testcases, list):
                testcases.extend([item for item in raw_testcases if isinstance(item, dict)])
        for value in node.values():
            testcases.extend(_collect_testcases(value))
    elif isinstance(node, list):
        for item in node:
            testcases.extend(_collect_testcases(item))
    return testcases


@report_controller.route('/reports/<int:report_id>/junit', methods=['GET'])
def junit_report(report_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    report = report_service.fetch_report_by_id(report_id)
    if not report:
        return render_template('junit_report.html', report=None, error='Relatório não encontrado.'), 404

    junit_data = report.get('junit')
    if not isinstance(junit_data, dict):
        return render_template(
            'junit_report.html',
            report=report,
            error='Este relatório não possui dados JUnit para exibição.',
            summary=None,
            testcases=[],
            pagination=None
        ), 200

    root_suite = junit_data.get('testsuite') or junit_data.get('testsuites') or junit_data
    all_testcases = _collect_testcases(root_suite)
    total_testcases = len(all_testcases)
    total_pages = max(1, (total_testcases + per_page - 1) // per_page)

    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    testcases = all_testcases[start:end]

    summary = {
        'tests': root_suite.get('tests', total_testcases) if isinstance(root_suite, dict) else total_testcases,
        'failures': root_suite.get('failures', 0) if isinstance(root_suite, dict) else 0,
        'errors': root_suite.get('errors', 0) if isinstance(root_suite, dict) else 0,
        'skipped': root_suite.get('skipped', 0) if isinstance(root_suite, dict) else 0,
        'time': root_suite.get('time', 'N/A') if isinstance(root_suite, dict) else 'N/A',
        'suite_name': root_suite.get('name', 'JUnit Report') if isinstance(root_suite, dict) else 'JUnit Report'
    }

    pagination = {
        'current_page': page,
        'per_page': per_page,
        'total_testcases': total_testcases,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1,
        'next_page': page + 1
    }

    return render_template(
        'junit_report.html',
        report=report,
        error=None,
        summary=summary,
        testcases=testcases,
        pagination=pagination
    ), 200
