from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import json
import requests
import os
from werkzeug.utils import secure_filename
import paho.mqtt.publish as publish
from collections import defaultdict
import time
import subprocess
from prometheus_client import Gauge, generate_latest, REGISTRY, CONTENT_TYPE_LATEST



# === CONFIGURAÇÕES ===
PROMETHEUS_URL = "http://100.127.13.111:9090/api/v1/query"
ALLOWED_IPS = ["100.127.13.111"]
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5150

UPLOAD_FOLDER = "/mnt/fl_clients/uploads"
ALLOWED_EXTENSIONS = {"py"}

# === INICIALIZAÇÃO DO FLASK ===
app = Flask(__name__)
CORS(app)

# === FUNÇÕES UTILITÁRIAS ===
def query_prometheus(query):
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query}, timeout=3)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and 'result' in data['data']:
            return data['data']['result']
        return []
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro ao conectar ao Prometheus: {str(e)}"}

def parse_single_metric(query_result):
    if isinstance(query_result, list) and len(query_result) > 0:
        try:
            return float(query_result[0]['value'][1])
        except (IndexError, ValueError, KeyError):
            return None
    return None

# === MIDDLEWARE DE IP ===
@app.before_request
def limit_remote_addr():
    client_ip = request.remote_addr
    if client_ip not in ALLOWED_IPS:
        abort(403)

# === MÉTRICAS SISTEMICAS ===
QUERIES = {
    "cpu": "avg(cpu_usage_percent)",
    "memory": "avg(memory_usage_percent)",
    "network/rx": "avg(network_rx_bytes_per_sec)",
    "network/tx": "avg(network_tx_bytes_per_sec)",
    "exporters": 'count(up{job="node_exporter"} == 1)',
}


@app.route('/metrics/<path:metric_name>')
def get_generic_metric(metric_name):
    if metric_name not in QUERIES:
        return jsonify({"error": "Métrica não encontrada"}), 404

    query = QUERIES[metric_name]
    result = query_prometheus(query)
    
    # A chave do JSON retornado será a última parte do nome (ex: "cpu", "memory")
    key = metric_name.split("/")[-1]
    return jsonify({key: parse_single_metric(result)})

@app.route("/metrics/clients")
def get_active_clients():
    try:
        # Consulta Prometheus para verificar quais pushgateways estão UP
        query = 'up{job="pushgateway"}'
        result = query_prometheus(query)

        if isinstance(result, dict) and "error" in result:
            return jsonify({"clients": 0, "error": result["error"]}), 500

        # Filtra somente os que estão com valor = 1 (UP)
        up_gateways = [
            item["metric"]["instance"]
            for item in result
            if float(item["value"][1]) == 1.0
        ]

        return jsonify({"clients": len(up_gateways), "instances": up_gateways})
    except Exception as e:
        return jsonify({"clients": 0, "error": str(e)}), 500



# === UPLOAD DE ARQUIVOS (.py) ===
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"py", "csv", "env", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    filename_param = request.form.get("filename")  # nome desejado vindo do front

    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio."}), 400

    if not filename_param:
        return jsonify({"error": "Nome de destino (filename) não informado."}), 400

    if file and allowed_file(filename_param):
        filename = secure_filename(filename_param)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": f"Arquivo '{filename}' salvo com sucesso!"}), 200
    else:
        return jsonify({"error": "Tipo de arquivo não permitido."}), 400
    
@app.route('/save-flags', methods=['POST'])
def save_flags():
    flags = request.get_json()

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    flags_path = os.path.join(UPLOAD_FOLDER, 'upload_flags.json')
    with open(flags_path, 'w') as f:
        json.dump(flags, f, indent=4)

    return jsonify({"message": "Flags salvas com sucesso."}), 200

    
# === CONFIGURA EXP. PADRAO ===
@app.route("/salvar-envs", methods=["POST"])
def salvar_arquivos_env():
    data = request.get_json()

    if not data or "clientEnv" not in data or "serverEnv" not in data:
        return jsonify({"error": "Dados incompletos para gerar arquivos .env"}), 400

    try:
        client_env_path = "/mnt/fl_clients/Client/config_cliente.env"
        server_env_path = "/mnt/fl_clients/Server/flask-server/config_servidor.env"

        with open(client_env_path, "w") as client_file:
            client_file.write(data["clientEnv"].strip() + "\n")

        with open(server_env_path, "w") as server_file:
            server_file.write(data["serverEnv"].strip() + "\n")

        return jsonify({"message": "Arquivos .env do cliente e do servidor salvos com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao salvar arquivos: {str(e)}"}), 500

@app.route("/metrics/prometheus/combined")
def get_combined_metrics():
    global combined_history  # 👈 Importante

    accuracy_query = 'fl_client_accuracy'
    loss_query = 'fl_client_loss'

    accuracy_results = query_prometheus(accuracy_query)
    loss_results = query_prometheus(loss_query)

    combined_rounds = {}

    # Processa accuracy
    for item in accuracy_results:
        client_id = item['metric'].get('client_id')
        tipo = item['metric'].get('tipo')
        round_str = item['metric'].get('round')
        if not client_id or not tipo or not round_str:
            continue

        round_num = int(round_str)
        valor = float(item['value'][1])
        key = (round_num, client_id)

        if key not in combined_rounds:
            combined_rounds[key] = {
                "round": round_num,
                "client_id": client_id
            }

        combined_rounds[key][f"accuracy_{tipo}"] = valor

    # Processa loss
    for item in loss_results:
        client_id = item['metric'].get('client_id')
        tipo = item['metric'].get('tipo')
        round_str = item['metric'].get('round')
        if not client_id or not tipo or not round_str:
            continue

        round_num = int(round_str)
        valor = float(item['value'][1])
        key = (round_num, client_id)

        if key not in combined_rounds:
            combined_rounds[key] = {
                "round": round_num,
                "client_id": client_id
            }

        combined_rounds[key][f"loss_{tipo}"] = valor

    # Junta ao histórico
    for key, data in combined_rounds.items():
        if data not in combined_history:
            combined_history.append(data)

    return jsonify(combined_history)

# Mantém referência aos subprocessos dos clientes simulados
simulated_clients = []
RASP_COUNT = 3  # número fixo de Raspberry Pis

@app.route("/start-simulados", methods=["POST"])
def start_simulados():
    global simulated_clients, combined_history
    combined_history = []  # limpa histórico

    data = request.get_json()
    requested_clients = data.get("num_clients",RASP_COUNT)

    # Inicia raspberries reais via MQTT
    publish.single(MQTT_TOPIC, "start", hostname=MQTT_BROKER, port=MQTT_PORT)
    print(f"📡 Comando 'start' enviado via MQTT")


    return jsonify({
        "message": f"Iniciados {requested_clients} clientes: {min(RASP_COUNT, requested_clients)} raspberries"
    })


# === COMANDOS MQTT ===
MQTT_BROKER = "100.127.13.111"
MQTT_PORT = 1883
MQTT_TOPIC = "fl/training"

@app.route("/start", methods=["POST"])
@app.route("/stop", methods=["POST"])
@app.route("/down", methods=["POST"])
def mqtt_command():
    global combined_history

    command = request.path.strip("/")

    if command == "start":
        print("🧼 Limpando histórico de métricas anteriores...")
        combined_history = []  # Zera o histórico

    try:
        publish.single(MQTT_TOPIC, command, hostname=MQTT_BROKER, port=MQTT_PORT)
        return jsonify({"message": f"Comando '{command}' enviado com sucesso via MQTT"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao enviar comando MQTT: {str(e)}"}), 500


# === EXECUÇÃO ===
if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT)
