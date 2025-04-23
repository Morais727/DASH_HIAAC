from flask import Blueprint, jsonify
from utils.prometheus import query_prometheus, parse_single_metric

metrics_bp = Blueprint('metrics', __name__)

QUERIES = {
    "cpu": "avg(cpu_usage_percent)",
    "memory": "avg(memory_usage_percent)",
    "network/rx": "avg(network_rx_bytes_per_sec)",
    "network/tx": "avg(network_tx_bytes_per_sec)",
    "exporters": 'count(up{job="node_exporter"} == 1)',
}

@metrics_bp.route('/metrics/<path:metric_name>')
def get_generic_metric(metric_name):
    if metric_name not in QUERIES:
        return jsonify({"error": "Métrica não encontrada"}), 404
    result = query_prometheus(QUERIES[metric_name])
    key = metric_name.split("/")[-1]
    return jsonify({key: parse_single_metric(result)})

@metrics_bp.route("/metrics/clients")
def get_active_clients():
    try:
        result = query_prometheus('up{job="pushgateway"}')
        if isinstance(result, dict) and "error" in result:
            return jsonify({"clients": 0, "error": result["error"]}), 500
        up_gateways = [item["metric"]["instance"] for item in result if float(item["value"][1]) == 1.0]
        return jsonify({"clients": len(up_gateways), "instances": up_gateways})
    except Exception as e:
        return jsonify({"clients": 0, "error": str(e)}), 500