import sqlite3


class ReportRepository:
    def __init__(self, db_path='reports_automations.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
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
                                    squad TEXT NOT NULL
                                )''')
            self.conn.commit()


    def insert_report_automation(self, automation_id, status, url_report, report_date, name, squad):
        self.conn.execute(
            'INSERT INTO reports_automation (automation_id, status, url_report, report_date, name, squad) VALUES (?, ?, ?, ?, ?, ?)',
            (automation_id, status, url_report, report_date, name, squad))
        self.conn.commit()

    def get_all_report_automations(self):
        cursor = self.conn.execute("SELECT * FROM reports_automation")
        rows = cursor.fetchall()
        reports = [dict(row) for row in rows]
        return reports

    def get_paginated_report_automations(self, page, per_page):
        offset = (page - 1) * per_page
        query = "SELECT * FROM reports_automation LIMIT ? OFFSET ?"

        cursor = self.conn.execute(query, (per_page, offset))
        rows = cursor.fetchall()
        reports = [dict(row) for row in rows]
        return reports