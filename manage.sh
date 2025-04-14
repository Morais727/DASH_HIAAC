#!/bin/bash

# Caminhos dos scripts Python e diretórios
DASHBOARD_DIR="Server/federated-dashboard"
FLASK_SCRIPT="Server/flask-server/server_flask.py"
MQTT_SCRIPT="Server/flask-server/server_mqtt_listener.py"
SYNC_SCRIPT="./sync_directories.py"
SURPLUS_LISTENER="Client/surplus_mqtt_listener.py"
PROMETHEUS_CMD="/usr/bin/prometheus"
PROMETHEUS_CONF="Server/prometheus.yml"

# Função para iniciar tudo
start_services() {
    echo "🚀 Iniciando todos os serviços em segundo plano..."

    nohup npm run dev --prefix "$DASHBOARD_DIR" > dashboard.log 2>&1 &
    echo "🟢 Dashboard iniciado."

    nohup python3 "$FLASK_SCRIPT" > flask_server.log 2>&1 &
    echo "🟢 Flask server iniciado."

    nohup python3 "$MQTT_SCRIPT" > mqtt_listener.log 2>&1 &
    echo "🟢 MQTT Listener iniciado."

    nohup python3 "$SURPLUS_LISTENER" > surplus_listener.log 2>&1 &
    echo "🟢 Surplus MQTT Listener iniciado."

    nohup sudo $PROMETHEUS_CMD --config.file=$PROMETHEUS_CONF > prometheus.log 2>&1 &
    echo "🟢 Prometheus iniciado."

    nohup python3 "$SYNC_SCRIPT" > sync.log 2>&1 &
    echo "🟢 Sincronizador de diretórios iniciado."

    echo "✅ Todos os serviços foram iniciados."
}

# Função para parar tudo
stop_services() {
    echo "🛑 Parando todos os serviços..."

    echo "⏹️ Parando Dashboard (npm)..."
    pkill -f "dashboard"
    sleep 1
    pgrep -f "dashboard" && pkill -9 -f "dashboard"

    echo "⏹️ Parando Flask Server..."
    pkill -f "$FLASK_SCRIPT"
    sleep 1
    pgrep -f "$FLASK_SCRIPT" && pkill -9 -f "$FLASK_SCRIPT"

    echo "⏹️ Parando MQTT Listener..."
    pkill -f "$MQTT_SCRIPT"
    sleep 1
    pgrep -f "$MQTT_SCRIPT" && pkill -9 -f "$MQTT_SCRIPT"

    echo "⏹️ Parando Surplus MQTT Listener..."
    pkill -f "$SURPLUS_LISTENER"
    sleep 1
    pgrep -f "$SURPLUS_LISTENER" && pkill -9 -f "$SURPLUS_LISTENER"

    echo "⏹️ Parando Prometheus..."
    sudo pkill -f "$PROMETHEUS_CMD"
    sleep 1
    sudo pgrep -f "$PROMETHEUS_CMD" && sudo pkill -9 -f "$PROMETHEUS_CMD"

    echo "⏹️ Parando sincronizador de diretórios..."
    pkill -f "$SYNC_SCRIPT"
    sleep 1
    pgrep -f "$SYNC_SCRIPT" && pkill -9 -f "$SYNC_SCRIPT"

    pkill  "server.py"
    sleep 1
    pgrep  "server.py" && pkill -9 "server.py"

    echo "✅ Todos os serviços foram encerrados com sucesso."
}

# Função para checar status (extra)
status_services() {
    echo "📊 Status dos serviços:"
    
    pgrep -fl "dashboard" || echo "❌ Dashboard não está rodando."
    pgrep -fl "$FLASK_SCRIPT" || echo "❌ Flask server não está rodando."
    pgrep -fl "$MQTT_SCRIPT" || echo "❌ MQTT Listener não está rodando."
    pgrep -fl "$SURPLUS_LISTENER" || echo "❌ Surplus MQTT Listener não está rodando."
    pgrep -fl "$PROMETHEUS_CMD" || echo "❌ Prometheus não está rodando."
    pgrep -fl "$SYNC_SCRIPT" || echo "❌ Sincronizador de diretórios não está rodando."
}

# Controle de comandos
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        status_services
        ;;
    *)
        echo "❓ Uso: $0 {start|stop|status}"
        exit 1
        ;;
esac
