from flask import Flask
from flask_cors import CORS
from config import FLASK_HOST, FLASK_PORT, UPLOAD_FOLDER
from middleware import ip_restriction
from routes.metrics import metrics_bp
from routes.upload import upload_bp
from routes.control import control_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

@app.before_request
def before_request():
    ip_restriction()

# Register Blueprints
app.register_blueprint(metrics_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(control_bp)

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT)