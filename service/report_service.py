from repository.report_repository import ReportRepository


class ReportService:
    def __init__(self):
        self.repository = ReportRepository()

    def register_report(self, automation_id, status, url_report, report_date, name, squad, tests):
        self.repository.insert_report_automation(automation_id, status, url_report, report_date, name, squad, tests)

    def fetch_all_reports(self):
        reports = self.repository.get_all_report_automations()
        return reports

    def fetch_paginated_reports(self, page, per_page):
        reports = self.repository.get_paginated_report_automations(page, per_page)
        return reports
