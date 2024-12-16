from flask import Flask

from controller.automation_controller import automation_controller
from controller.report_controller import report_controller

app: Flask = Flask(__name__)

app.register_blueprint(automation_controller)
app.register_blueprint(report_controller)

if __name__ == '__main__':
    app.run(debug=True)