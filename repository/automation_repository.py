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
                                    git TEXT NOT NULL,
                                    image_base64 TEXT
                                )''')
            self.conn.commit()
        else:
            # Verificar se as colunas image_base64 e type existem, se não existirem, adicionar
            cursor.execute("PRAGMA table_info(automations)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'image_base64' not in columns:
                cursor.execute("ALTER TABLE automations ADD COLUMN image_base64 TEXT")
                self.conn.commit()
            if 'type' not in columns:
                cursor.execute("ALTER TABLE automations ADD COLUMN type TEXT")
                self.conn.commit()

    def insert_automation(self, name, squad, type, description, language, cucumber, launch_date, git, image_base64=None):
        self.conn.execute(
            'INSERT INTO automations (name, squad, type, description, language, cucumber, launch_date, git, image_base64) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (name, squad, type, description, language, cucumber, launch_date, git, image_base64))
        self.conn.commit()

    def get_all_automations(self):
        cursor = self.conn.execute("SELECT * FROM automations")
        rows = cursor.fetchall()
        automations = [dict(row) for row in rows]
        return automations

    def get_paginated_automations(self, page, per_page, search_term='', squad_filter='', type_filter=''):
        offset = (page - 1) * per_page
        
        # Construir query com filtros
        where_conditions = []
        params = []
        
        if search_term:
            where_conditions.append("lower(name) LIKE lower(?)")
            params.append(f"%{search_term}%")
        
        if squad_filter:
            where_conditions.append("lower(squad) = lower(?)")
            params.append(squad_filter)
        
        if type_filter:
            where_conditions.append("lower(type) = lower(?)")
            params.append(type_filter)
        
        # Query principal
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        query = f"SELECT * FROM automations{where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        cursor = self.conn.execute(query, params)
        rows = cursor.fetchall()
        automations = [dict(row) for row in rows]

        # Query de contagem
        count_query = f"SELECT COUNT(*) FROM automations{where_clause}"
        count_params = params[:-2]  # Remove per_page e offset
        
        cursor = self.conn.execute(count_query, count_params)
        total_automations = cursor.fetchone()[0]

        return automations, total_automations

    def get_automations_by_search(self, search_term, page, per_page):
        offset = (page - 1) * per_page
        like_term = f"%{search_term}%"

        query = (
            "SELECT * FROM automations WHERE lower(name) LIKE lower(?) "
            "ORDER BY id DESC LIMIT ? OFFSET ?"
        )
        cursor = self.conn.execute(query, (like_term, per_page, offset))
        rows = cursor.fetchall()
        automations = [dict(row) for row in rows]

        count_query = "SELECT COUNT(*) FROM automations WHERE lower(name) LIKE lower(?)"
        cursor = self.conn.execute(count_query, (like_term,))
        total_automations = cursor.fetchone()[0]

        return automations, total_automations

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

    def check_duplicate_automation(self, name, squad, git):
        """
        Verifica se já existe uma automação com o mesmo nome, squad e repositório git
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM automations WHERE LOWER(name) = LOWER(?) AND LOWER(squad) = LOWER(?) AND LOWER(git) = LOWER(?)',
            (name, squad, git)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None

    def update_automation(self, automation_id, data):
        """
        Atualiza uma automação existente
        """
        cursor = self.conn.cursor()
        
        # Construir query de atualização
        set_clauses = []
        params = []
        
        for key, value in data.items():
            if key != 'id':  # Não atualizar o ID
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(automation_id)
        
        query = f"UPDATE automations SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()
        
        return cursor.rowcount > 0