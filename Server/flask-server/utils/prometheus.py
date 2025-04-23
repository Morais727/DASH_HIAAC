import requests
from config import PROMETHEUS_URL

def query_prometheus(query):
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query}, timeout=3)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}).get('result', [])
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro ao conectar ao Prometheus: {str(e)}"}

def parse_single_metric(query_result):
    if isinstance(query_result, list) and query_result:
        try:
            return float(query_result[0]['value'][1])
        except Exception:
            return None
    return None