import paho.mqtt.client as mqtt
import subprocess
import threading
import os
import time
import json

# === Caminhos e configurações ===
PYTHON_IN_VENV = "Server_env/bin/python3"
PYTHON_SERVER_PATH = "/mnt/fl_clients/Server/flask-server/server.py"
MQTT_BROKER = "100.127.13.111"
MQTT_PORT = 1883
MQTT_TOPIC = "fl/training"
SERVER_PORT = 7070

# === Variáveis globais ===
server_process = None

def free_port(port):
    """Libera a porta especificada se algum processo estiver a ocupando."""
    try:
        process = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
        pids = process.stdout.strip().split("\n")

        if pids and pids[0] != "":
            print(f"🛑 Matando processos que usam a porta {port}: {pids}")
            for pid in pids:
                subprocess.run(["kill", "-9", pid])
            time.sleep(2)
        else:
            print(f"⚠️ Nenhum processo encontrado na porta {port}. Nenhuma ação necessária.")
    except Exception as e:
        print(f"❌ Erro ao tentar liberar a porta {port}: {e}")

def start_server():
    """Inicia o servidor Python com base nas flags e variáveis de ambiente"""
    global server_process

    if server_process is not None and server_process.poll() is None:
        print("⚠️ O servidor já está rodando.")
        return

    print("🚀 Iniciando o servidor em ambiente virtual Server_env...")

    flags_path = "/mnt/fl_clients/uploads/upload_flags.json"
    script_path = PYTHON_SERVER_PATH
    env_path = "/mnt/fl_clients/Server/flask-server/config_servidor.env"

    try:
        if os.path.exists(flags_path):
            with open(flags_path, "r") as f:
                flags = json.load(f)

            if flags.get("server", False):
                uploaded_script = "/mnt/fl_clients/uploads/server.py"
                if os.path.exists(uploaded_script):
                    script_path = uploaded_script
                    print("📁 Usando server.py enviado via upload.")

            if flags.get("envServer", False):
                uploaded_env = "/mnt/fl_clients/uploads/config_servidor.env"
                if os.path.exists(uploaded_env):
                    env_path = uploaded_env
                    print("🧪 Usando config_servidor.env enviado via upload.")
    except Exception as e:
        print(f"⚠️ Erro ao ler upload_flags.json: {e}")

    if not os.path.exists(script_path):
        print(f"❌ Script server.py não encontrado em: {script_path}")
        return

    # === Carrega variáveis de ambiente ===
    env = {}

    if os.path.exists(env_path):
        try:
            print(f"📄 Carregando variáveis de ambiente do arquivo: {env_path}")
            with open(env_path) as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env[key] = value
                        print(f"  • {key} = {value}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar variáveis do .env: {e}")

    env["PATH"] = os.environ.get("PATH", "")
    env["HOME"] = os.environ.get("HOME", "/home/pi")
    env["VIRTUAL_ENV"] = os.path.abspath(os.path.dirname(os.path.dirname(PYTHON_IN_VENV)))

    log_file_path = "/mnt/fl_clients/Server/flask-server/server.log"
    os.makedirs("/mnt/fl_clients/tmp", exist_ok=True)

    try:
        log_file = open(log_file_path, "a")

        server_process = subprocess.Popen(
            [PYTHON_IN_VENV, script_path],
            env=env,
            stdout=log_file,
            stderr=log_file
        )
        print(f"✅ Servidor iniciado com PID {server_process.pid}. Logs em: {log_file_path}")
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")

def stop_server():
    """Interrompe o servidor"""
    global server_process

    if server_process is not None and server_process.poll() is None:
        print(f"🛑 Parando servidor (PID {server_process.pid})...")
        server_process.terminate()
        server_process.wait()
        print("✅ Servidor parado com sucesso.")
        server_process = None
    else:
        print("⚠️ O servidor não está em execução.")

def on_message(client, userdata, message):
    """Recebe comandos MQTT e executa as ações correspondentes."""
    command = message.payload.decode().strip()
    print(f"📥 Mensagem recebida no servidor: {command}")

    if command == "start":
        start_server()
    elif command == "stop":
        stop_server()
    else:
        print(f"⚠️ Comando desconhecido: {command}")

def on_disconnect(client, userdata, rc):
    print("🔌 Conexão MQTT perdida! Tentando reconectar...")
    while True:
        try:
            client.reconnect()
            print("✅ Reconectado ao broker MQTT!")
            break
        except Exception as e:
            print(f"❌ Falha ao reconectar: {e}. Tentando novamente em 5s...")
            time.sleep(5)

# === Inicialização ===
client = mqtt.Client()
client.on_message = on_message
client.on_disconnect = on_disconnect

# === Thread para monitorar processo e reinscrição MQTT ===
def monitor_server():
    global server_process
    while True:
        time.sleep(30)

        if server_process is None or server_process.poll() is not None:
            print("⚠️ Detecção: server.py não está rodando. Reiniciando...")
            start_server()

        try:
            result, _ = client.subscribe(MQTT_TOPIC)
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"📡 Verificação: (re)inscrito no tópico '{MQTT_TOPIC}' com sucesso.")
            else:
                print(f"❌ Erro ao tentar reinscrever no tópico '{MQTT_TOPIC}' (Código: {result})")
        except Exception as e:
            print(f"❌ Erro ao reinscrever no tópico MQTT: {e}")

monitor_thread = threading.Thread(target=monitor_server, daemon=True)
monitor_thread.start()

# Libera a porta antes de iniciar
print(f"⚠️ Verificando se a porta {SERVER_PORT} está em uso...")
free_port(SERVER_PORT)

# Conecta ao MQTT e aguarda comandos
try:
    print(f"🔗 Conectando ao broker MQTT {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    print(f"📡 Servidor inscrito no tópico '{MQTT_TOPIC}'. Aguardando comandos...")
    client.loop_forever()
except Exception as e:
    print(f"❌ Erro ao conectar ao MQTT: {e}")
