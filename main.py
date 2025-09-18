from flask import Flask
from flask_cors import CORS

from controller.report_controller import report_controller
from controller.test_contract_controller import test_contract_controller
from controller.automation_controller import automation_controller

app: Flask = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

app.register_blueprint(report_controller)
app.register_blueprint(test_contract_controller)
app.register_blueprint(automation_controller)

if __name__ == '__main__':
    app.run(debug=True)