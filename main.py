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
    # No runner interativo do Cursor/IPython, o reloader do Flask pode gerar
    # "SystemExit: 1" ao reiniciar o processo. Mantemos debug ligado, mas sem reloader.
    app.run(debug=True, use_reloader=False)
    