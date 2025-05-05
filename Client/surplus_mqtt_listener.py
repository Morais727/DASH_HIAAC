import paho.mqtt.client as mqtt
import threading
import subprocess
import os
import time
import signal
import logging
import json

# === Configuração de Logs ===
LOG_DIR = "/mnt/fl_clients/tmp"  
LOG_FILE = os.path.join(LOG_DIR, "Surplus_controller.log")
CLIENT_LOG_FILE = os.path.join(LOG_DIR, "client.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def log(msg, level="info"):
    print(msg)
    getattr(logging, level.lower())(msg)

# === Configurações MQTT e do ambiente ===
MQTT_BROKER = "100.127.13.111"
MQTT_PORT = 1883
MQTT_TOPIC = "fl/training"

VENV_PYTHON = "Surplus_env/bin/python"
DEFAULT_SCRIPT = "/mnt/fl_clients/Client/client.py"
DEFAULT_ENV = "/mnt/fl_clients/Client/config_cliente.env"

client_processes = []  # Lista para múltiplos subprocessos

def start_clients():
    """Inicia os clientes federados conforme definido nas flags"""
    global client_processes

    if any(p.poll() is None for p in client_processes):
        log("Clientes já estão em execução.")
        return

    flags_path = "/mnt/fl_clients/uploads/upload_flags.json"
    script_path = DEFAULT_SCRIPT
    env_path = DEFAULT_ENV
    surplus_clients = 1  # Valor padrão

    # === Leitura das flags ===
    try:
        if os.path.exists(flags_path):
            with open(flags_path, 'r') as f:
                flags = json.load(f)

            if flags.get("client", False) and os.path.exists("/mnt/fl_clients/uploads/client.py"):
                script_path = "/mnt/fl_clients/uploads/client.py"
                log("Usando client.py enviado via upload.")
            else:
                script_path = "/mnt/fl_clients/Client/client_surplus.py"
                log("Usando client_surplus.py como padrão.")
            
            if flags.get("envClient", False) and os.path.exists("/mnt/fl_clients/uploads/config_cliente.env"):
                env_path = "/mnt/fl_clients/uploads/config_cliente.env"
                log("Usando .env enviado via upload.")
            else:
                log("Usando .env padrão.")

            surplus_clients = int(flags.get("surplus_clients", 1))
        else:
            log("upload_flags.json não encontrado. Usando configurações padrão.")
            script_path = "/mnt/fl_clients/Client/client_surplus.py"
    except Exception as e:
        log(f"Erro ao ler upload_flags.json: {e}. Usando valores padrão.", "warning")
        script_path = "/mnt/fl_clients/Client/client_surplus.py"


    # === Verificação dos caminhos ===
    if not os.path.exists(script_path):
        log(f"Script client.py não encontrado: {script_path}", "error")
        return

    if not os.path.exists(VENV_PYTHON):
        log(f"Python do ambiente virtual não encontrado: {VENV_PYTHON}", "error")
        return

    # === Ambiente limpo com variáveis do .env ===
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/home/pi")}

    if os.path.exists(env_path):
        try:
            with open(env_path) as f:
                log(f"Carregando variáveis de: {env_path}")
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env[key] = value
                        log(f"  • {key} = {value}")
        except Exception as e:
            log(f"Erro ao carregar .env: {e}", "warning")

    # === Inicialização dos subprocessos ===
    client_processes.clear()
    for i in range(surplus_clients):
        try:
            log(f"Iniciando cliente federado {i + 1}/{surplus_clients} com script: {script_path}")
            client_log = open(CLIENT_LOG_FILE, "a")
            proc = subprocess.Popen(
                [VENV_PYTHON, script_path],
                env=env,
                stdout=client_log,
                stderr=client_log
            )
            client_processes.append(proc)
            log(f"Cliente {i + 1} iniciado com PID {proc.pid}")
        except Exception as e:
            log(f"Falha ao iniciar cliente {i + 1}: {e}", "error")

def stop_clients():
    """Encerra todos os clientes em execução"""
    global client_processes

    if not client_processes:
        log("Nenhum cliente está em execução.")
        return

    for i, proc in enumerate(client_processes, start=1):
        if proc.poll() is None:
            log(f"Encerrando cliente {i} (PID {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
                log(f"Cliente {i} encerrado com sucesso.")
            except subprocess.TimeoutExpired:
                log(f"Cliente {i} não respondeu ao término. Forçando kill...")
                proc.kill()
                log(f"Cliente {i} morto à força.")
        else:
            log(f"Cliente {i} já estava parado.")

    client_processes.clear()

def on_message(client, userdata, message):
    command = message.payload.decode().strip()
    log(f"Mensagem recebida: {command}")

    if command == "start":
        start_clients()
    elif command == "stop":
        stop_clients()
    else:
        log(f"Comando desconhecido: {command}")

def on_disconnect(client, userdata, rc):
    log("Conexão MQTT perdida! Tentando reconectar...")
    while True:
        try:
            client.reconnect()
            log("Reconectado ao broker MQTT!")
            break
        except Exception as e:
            log(f"Falha ao reconectar: {e}. Tentando novamente em 5s...", "error")
            time.sleep(5)

# === Inicialização MQTT ===
client = mqtt.Client()
client.on_message = on_message
client.on_disconnect = on_disconnect

# === Monitoramento dos processos ===
def monitor_clients():
    while True:
        time.sleep(30)
        active = sum(1 for p in client_processes if p.poll() is None)
        log(f"Monitor: {active} cliente(s) ainda ativos.")

monitor_thread = threading.Thread(target=monitor_clients, daemon=True)
monitor_thread.start()

try:
    log(f"Conectando ao broker MQTT {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    log(f"Inscrito no tópico '{MQTT_TOPIC}'. Aguardando comandos...")
    client.loop_forever()
except Exception as e:
    log(f"Erro ao conectar ao MQTT: {e}", "error")
