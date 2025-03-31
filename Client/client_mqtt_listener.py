import paho.mqtt.client as mqtt
import threading
import subprocess
import os
import time
import signal
import logging
import json

# === Configuração de Logs ===
LOG_DIR = "/home/pi/logs"  # Altere para /var/log/federated_client se preferir
LOG_FILE = os.path.join(LOG_DIR, "controller.log")
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

VENV_PYTHON = "/home/pi/venv/bin/python3"
CLIENT_SCRIPT = "/mnt/fl_clients/Client/client.py"

client_process = None  # Armazena o processo do cliente federado

def start_client():
    """Inicia o cliente federado com base nas flags e variáveis de ambiente"""
    global client_process

    if client_process and client_process.poll() is None:
        log("⚠️ O cliente já está em execução.")
        return

    if not os.path.exists(VENV_PYTHON):
        log(f"❌ Python do ambiente virtual não encontrado: {VENV_PYTHON}", "error")
        return

    # === Verifica flags do JSON ===
    flags_path = "/mnt/fl_clients/uploads/upload_flags.json"
    script_path = CLIENT_SCRIPT  # Default
    env_path = "/mnt/fl_clients/Client/config_cliente.env"  # Default

    try:
        if os.path.exists(flags_path):
            with open(flags_path, 'r') as f:
                flags = json.load(f)

            # Verifica se deve usar client.py da pasta uploads
            if flags.get("client", False):
                uploaded_script = "/mnt/fl_clients/uploads/client.py"
                if os.path.exists(uploaded_script):
                    script_path = uploaded_script
                    log("📁 Usando client.py enviado via upload.")
                else:
                    log("⚠️ Flag client=True, mas o client.py não foi encontrado. Usando script padrão.")

            # Verifica se deve usar .env da pasta uploads
            if flags.get("envClient", False):
                uploaded_env = "/mnt/fl_clients/uploads/config_cliente.env"
                if os.path.exists(uploaded_env):
                    env_path = uploaded_env
                    log("🧪 Usando variáveis de ambiente do .env enviado via upload.")
                else:
                    log("⚠️ Flag envClient=True, mas o config_cliente.env não foi encontrado. Usando env padrão.")
        else:
            log("⚠️ Arquivo upload_flags.json não encontrado. Usando configurações padrão.")
    except Exception as e:
        log(f"⚠️ Erro ao ler upload_flags.json: {e}. Usando valores padrão.", "warning")

    if not os.path.exists(script_path):
        log(f"❌ Script client.py não encontrado: {script_path}", "error")
        return

    # === Limpa e carrega novas variáveis de ambiente ===
    env = {}  # Ambiente limpo

    if os.path.exists(env_path):
        try:
            with open(env_path) as f:
                log(f"📦 Carregando variáveis de: {env_path}")
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env[key] = value
                        log(f"  • {key} = {value}")
        except Exception as e:
            log(f"⚠️ Erro ao carregar .env: {e}", "warning")
    else:
        log(f"⚠️ Arquivo .env não encontrado em: {env_path}", "warning")

    # Garante que o mínimo necessário do ambiente do sistema seja passado (como PATH)
    env["PATH"] = os.environ.get("PATH", "")
    env["HOME"] = os.environ.get("HOME", "/home/pi")

    try:
        log(f"🚀 Iniciando o cliente federado com script: {script_path}")
        os.makedirs(LOG_DIR, exist_ok=True)

        client_log = open(CLIENT_LOG_FILE, "a")
        client_process = subprocess.Popen(
            [VENV_PYTHON, script_path],
            env=env,
            stdout=client_log,
            stderr=client_log
        )

        log(f"✅ Cliente iniciado com PID {client_process.pid}")
    except Exception as e:
        log(f"❌ Falha ao iniciar o cliente: {e}", "error")


def stop_client():
    """Interrompe o cliente federado se estiver rodando"""
    global client_process

    if client_process and client_process.poll() is None:
        log("🛑 Parando o cliente federado...")
        client_process.terminate()

        try:
            client_process.wait(timeout=10)
            log("✅ Cliente parado com sucesso.")
        except subprocess.TimeoutExpired:
            log("⚠️ Cliente não respondeu ao sinal de término. Forçando encerramento...")
            client_process.kill()
            log("✅ Cliente encerrado à força.")
    else:
        log("⚠️ Nenhum cliente está em execução.")

def on_message(client, userdata, message):
    """Recebe comandos via MQTT e inicia ou para o cliente"""
    command = message.payload.decode().strip()
    log(f"📥 Mensagem recebida: {command}")

    if command == "start":
        start_client()
    elif command == "stop":
        stop_client()
    else:
        log(f"⚠️ Comando desconhecido: {command}")

def on_disconnect(client, userdata, rc):
    """Reconecta automaticamente ao broker MQTT em caso de desconexão."""
    log("🔌 Conexão MQTT perdida! Tentando reconectar...")
    while True:
        try:
            client.reconnect()
            log("✅ Reconectado ao broker MQTT!")
            break
        except Exception as e:
            log(f"❌ Falha ao reconectar: {e}. Tentando novamente em 5s...", "error")
            time.sleep(5)

# === Inicialização MQTT ===
client = mqtt.Client()
client.on_message = on_message
client.on_disconnect = on_disconnect

# === Verificação periódica do client.py ===
def monitor_client():
    global client_process
#  aaa
    while True:
        time.sleep(30)  # Verifica a cada 30 segundos

        # Verifica se o processo morreu
        if client_process is None or client_process.poll() is not None:
            try:
                result, _ = client.subscribe(MQTT_TOPIC)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    log(f"📡 Verificação: cliente (re)inscrito no tópico '{MQTT_TOPIC}' com sucesso.")
                else:
                    log(f"❌ Erro ao (re)inscrever no tópico '{MQTT_TOPIC}'. Código: {result}", "warning")
            except Exception as e:
                log(f"❌ Falha ao tentar reinscrever no tópico MQTT: {e}", "error")


# === Inicia a thread de monitoramento do cliente ===
monitor_thread = threading.Thread(target=monitor_client, daemon=True)
monitor_thread.start()
 

try:
    log(f"🔗 Conectando ao broker MQTT {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    log(f"📡 Inscrito no tópico '{MQTT_TOPIC}'. Aguardando mensagens...")
    client.loop_forever()
except Exception as e:
    log(f"❌ Erro ao conectar ao MQTT: {e}", "error")
