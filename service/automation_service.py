from repository.automation_repository import AutomationRepository


class AutomationService:
    def __init__(self):
        self.repository = AutomationRepository()

    def register_automation(self, name, squad, type, description, language, cucumber, launch_date, git, image_base64=None):
        # Validar tipo permitido
        allowed_types = ['Frontend', 'Backend', 'Mobile']
        if type not in allowed_types:
            raise ValueError(f"Tipo '{type}' não é válido. Tipos permitidos: {', '.join(allowed_types)}")
        
        # Verificar se já existe uma automação com o mesmo nome, squad e repositório
        existing_automation = self.repository.check_duplicate_automation(name, squad, git)
        if existing_automation:
            raise ValueError(f"Já existe uma automação com o nome '{name}' no squad '{squad}' com o repositório '{git}'. Escolha um nome diferente ou verifique se não está duplicando.")
        
        self.repository.insert_automation(name, squad, type, description, language, cucumber, launch_date, git, image_base64)

    def fetch_all_automations(self):
        automations = self.repository.get_all_automations()
        return automations

    def delete_automation(self, automation_id):
        return self.repository.delete_automation(automation_id)

    def get_automation_by_id(self, automation_id):
        return self.repository.get_automation_by_id(automation_id)

    def get_automation_by_name(self, automation_name):
        return self.repository.get_automation_by_name(automation_name)

    def fetch_paginated_automations(self, page, per_page, search_term=None):
        if search_term:
            automations, total = self.repository.get_automations_by_search(search_term, page, per_page)
        else:
            automations, total = self.repository.get_paginated_automations(page, per_page)
        return automations, total