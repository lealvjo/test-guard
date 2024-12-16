import sqlite3


class AutomationRepository:
    def __init__(self, db_path='automations.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='automations'")
        if not cursor.fetchone():
            self.conn.execute('''CREATE TABLE automations (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    squad TEXT,
                                    description TEXT NOT NULL,
                                    language TEXT NOT NULL,
                                    cucumber TEXT NOT NULL,
                                    launch_date TEXT NOT NULL,
                                    git TEXT NOT NULL
                                )''')
            self.conn.commit()

    def insert_automation(self, name, squad, description, language, cucumber, launch_date, git):
        self.conn.execute(
            'INSERT INTO automations (name, squad, description, language, cucumber, launch_date, git) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, squad, description, language, cucumber, launch_date, git))
        self.conn.commit()

    def get_all_automations(self):
        cursor = self.conn.execute("SELECT * FROM automations")
        rows = cursor.fetchall()
        automations = [dict(row) for row in rows]
        return automations

    def delete_automation(self, automation_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM automations WHERE id = ?', (automation_id,))
        self.conn.commit()

        return cursor.rowcount > 0

    def get_automation_by_id(self, automation_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM automations WHERE id = ?', (automation_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_automation_by_name(self, automation_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM automations WHERE name = ?', (automation_name,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
