import sqlite3
import json
from fuzzywuzzy import process


class ReportRepository:
    def __init__(self, db_path='reports_automations.db', automations_db_path='automations.db'):
        self.db_path = db_path
        self.automations_db_path = automations_db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Anexar o banco de automações para fazer JOIN
        self.conn.execute(f"ATTACH DATABASE '{automations_db_path}' AS automations_db")
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports_automation'")
        if not cursor.fetchone():
            self.conn.execute('''CREATE TABLE reports_automation (
                                    id_report INTEGER PRIMARY KEY AUTOINCREMENT,
                                    automation_id INTEGER NOT NULL,
                                    status TEXT NOT NULL,
                                    url_report TEXT NOT NULL,
                                    report_date TEXT NOT NULL,
                                    name TEXT NOT NULL,
                                    squad TEXT NOT NULL,
                                    tests INTEGER NOT NULL,
                                    junit TEXT
                                )''')
            self.conn.commit()
        else:
            cursor.execute("PRAGMA table_info(reports_automation)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'junit' not in columns:
                cursor.execute("ALTER TABLE reports_automation ADD COLUMN junit TEXT")
                self.conn.commit()

    def insert_report_automation(self, automation_id, status, url_report, report_date, name, squad, tests, junit=None):
        junit_json = json.dumps(junit) if junit is not None else None
        self.conn.execute(
            'INSERT INTO reports_automation (automation_id, status, url_report, report_date, name, squad, tests, junit) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (automation_id, status, url_report, report_date, name, squad, tests, junit_json))
        self.conn.commit()

    @staticmethod
    def _deserialize_junit(report):
        junit_value = report.get('junit')
        if not junit_value:
            report['junit'] = None
            return report

        try:
            report['junit'] = json.loads(junit_value)
        except (TypeError, json.JSONDecodeError):
            report['junit'] = None
        return report

    def get_all_report_automations(self):
        # JOIN com a tabela automations para buscar o campo type
        query = """
        SELECT r.*, a.type 
        FROM reports_automation r 
        LEFT JOIN automations_db.automations a ON r.automation_id = a.id 
        ORDER BY r.id_report DESC
        """
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        reports = [self._deserialize_junit(dict(row)) for row in rows]
        return reports

    def get_paginated_report_automations(self, page, per_page):
        offset = (page - 1) * per_page
        # JOIN com a tabela automations para buscar o campo type
        query = """
        SELECT r.*, a.type 
        FROM reports_automation r 
        LEFT JOIN automations_db.automations a ON r.automation_id = a.id 
        ORDER BY r.id_report DESC 
        LIMIT ? OFFSET ?
        """

        cursor = self.conn.execute(query, (per_page, offset))
        rows = cursor.fetchall()
        reports = [self._deserialize_junit(dict(row)) for row in rows]

        # Contando o total de relatórios
        count_query = "SELECT COUNT(*) FROM reports_automation"
        cursor = self.conn.execute(count_query)
        total_reports = cursor.fetchone()[0]

        return reports, total_reports

    def get_reports_by_search(self, search_term, page, per_page):
        # Buscar todos os relatórios do banco com JOIN para incluir o tipo
        query = """
        SELECT r.*, a.type 
        FROM reports_automation r 
        LEFT JOIN automations_db.automations a ON r.automation_id = a.id 
        ORDER BY r.id_report DESC
        """
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        reports = [self._deserialize_junit(dict(row)) for row in rows]

        # Realiza a busca fuzzy no nome dos relatórios
        report_names = [report['name'] for report in reports]
        matches = process.extract(search_term, report_names, limit=len(reports))

        # Filtra os relatórios com base na similaridade fuzzy
        matched_reports = []
        matched_ids = set()

        for match in matches:
            report_name = match[0]
            score = match[1]

            if score >= 70:  # Limite de similaridade (ajustável)
                # Encontre o relatório correspondente ao nome
                matched_report = next(report for report in reports if
                                      report['name'] == report_name and report['id_report'] not in matched_ids)

                # Adiciona o id_report no conjunto para evitar duplicação
                matched_ids.add(matched_report['id_report'])

                # Adiciona o relatório à lista de relatórios correspondentes
                matched_reports.append(matched_report)

        # Paginação: calcular o total de relatórios e aplicar o limite de página
        total_reports = len(matched_reports)  # Total de relatórios que correspondem à busca
        offset = (page - 1) * per_page
        paginated_reports = matched_reports[offset:offset + per_page]

        return paginated_reports, total_reports

    def get_report_by_id(self, report_id):
        query = """
        SELECT r.*, a.type
        FROM reports_automation r
        LEFT JOIN automations_db.automations a ON r.automation_id = a.id
        WHERE r.id_report = ?
        """
        cursor = self.conn.execute(query, (report_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._deserialize_junit(dict(row))
