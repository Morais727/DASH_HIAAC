from flask import Blueprint, request, jsonify
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, RASP_COUNT
import paho.mqtt.publish as publish

control_bp = Blueprint('control', __name__)
combined_history = []

@control_bp.route("/start-simulados", methods=["POST"])
def start_simulados():
    global combined_history
    combined_history = []
    data = request.get_json()
    requested_clients = data.get("num_clients", RASP_COUNT)
    publish.single(MQTT_TOPIC, "start", hostname=MQTT_BROKER, port=MQTT_PORT)
    return jsonify({
        "message": f"Iniciados {requested_clients} clientes: {min(RASP_COUNT, requested_clients)} raspberries"
    })

@control_bp.route("/start", methods=["POST"])
@control_bp.route("/stop", methods=["POST"])
@control_bp.route("/down", methods=["POST"])
def mqtt_command():
    global combined_history
    command = request.path.strip("/")
    if command == "start":
        combined_history = []
    try:
        publish.single(MQTT_TOPIC, command, hostname=MQTT_BROKER, port=MQTT_PORT)
        return jsonify({"message": f"Comando '{command}' enviado com sucesso via MQTT"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao enviar comando MQTT: {str(e)}"}), 500

@control_bp.route("/metrics/prometheus/combined")
def get_combined_metrics():
    global combined_history
    from utils.prometheus import query_prometheus

    accuracy_query = 'fl_client_accuracy'
    loss_query = 'fl_client_loss'

    accuracy_results = query_prometheus(accuracy_query)
    loss_results = query_prometheus(loss_query)

    combined_rounds = {}

    for result_set, metric_type in [(accuracy_results, "accuracy"), (loss_results, "loss")]:
        for item in result_set:
            client_id = item['metric'].get('client_id')
            tipo = item['metric'].get('tipo')
            round_str = item['metric'].get('round')
            if not client_id or not tipo or not round_str:
                continue
            round_num = int(round_str)
            valor = float(item['value'][1])
            key = (round_num, client_id)
            if key not in combined_rounds:
                combined_rounds[key] = {"round": round_num, "client_id": client_id}
            combined_rounds[key][f"{metric_type}_{tipo}"] = valor

    for key, data in combined_rounds.items():
        if data not in combined_history:
            combined_history.append(data)

    return jsonify(combined_history)