from repository.report_repository import ReportRepository


class ReportService:
    def __init__(self):
        self.repository = ReportRepository()

    def register_report(self, automation_id, status, url_report, report_date, name, squad, tests):
        self.repository.insert_report_automation(automation_id, status, url_report, report_date, name, squad, tests)

    def fetch_all_reports(self):
        reports = self.repository.get_all_report_automations()
        return reports

    def fetch_paginated_reports(self, page, per_page, search_term=None):
        # Se o termo de busca foi fornecido, aplicamos a busca fuzzy
        if search_term:
            reports = self.repository.get_reports_by_search(search_term)
        else:
            # Caso contrário, apenas fazemos a busca paginada padrão
            reports = self.repository.get_paginated_report_automations(page, per_page)

        return reports
