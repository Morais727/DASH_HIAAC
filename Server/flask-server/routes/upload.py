import os, json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_bp = Blueprint('upload', __name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    filename_param = request.form.get("filename")

    if file.filename == '' or not filename_param:
        return jsonify({"error": "Nome de arquivo inválido."}), 400

    if file and allowed_file(filename_param):
        filename = secure_filename(filename_param)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": f"Arquivo '{filename}' salvo com sucesso!"}), 200
    return jsonify({"error": "Tipo de arquivo não permitido."}), 400

@upload_bp.route('/save-flags', methods=['POST'])
def save_flags():
    flags = request.get_json()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with open(os.path.join(UPLOAD_FOLDER, 'upload_flags.json'), 'w') as f:
        json.dump(flags, f, indent=4)
    return jsonify({"message": "Flags salvas com sucesso."}), 200

@upload_bp.route("/salvar-envs", methods=["POST"])
def salvar_arquivos_env():
    data = request.get_json()
    if not data or "clientEnv" not in data or "serverEnv" not in data:
        return jsonify({"error": "Dados incompletos para gerar arquivos .env"}), 400

    try:
        paths = {
            "client": "/mnt/fl_clients/Client/config_cliente.env",
            "server": "/mnt/fl_clients/Server/flask-server/config_servidor.env"
        }
        with open(paths["client"], "w") as cf: cf.write(data["clientEnv"].strip() + "\n")
        with open(paths["server"], "w") as sf: sf.write(data["serverEnv"].strip() + "\n")
        return jsonify({"message": "Arquivos .env do cliente e do servidor salvos com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao salvar arquivos: {str(e)}"}), 500