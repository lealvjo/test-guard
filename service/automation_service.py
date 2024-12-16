from repository.automation_repository import AutomationRepository


class AutomationService:
    def __init__(self):
        self.repository = AutomationRepository()

    def register_automation(self, name, squad, description, language, cucumber, launch_date, git):
        self.repository.insert_automation(name, squad, description, language, cucumber, launch_date, git)

    def fetch_all_automations(self):
        automations = self.repository.get_all_automations()
        return automations

    def delete_automation(self, automation_id):
        return self.repository.delete_automation(automation_id)

    def get_automation_by_id(self, automation_id):
        return self.repository.get_automation_by_id(automation_id)

    def get_automation_by_name(self, automation_name):
        return self.repository.get_automation_by_name(automation_name)
