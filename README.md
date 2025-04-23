# 🧠 DASH_HIAAC - Federated Learning Dashboard

Este projeto tem como objetivo fornecer uma infraestrutura completa para experimentos de **Aprendizado Federado (Federated Learning)** com visualização de métricas, controle de experimentos e monitoramento de clientes (reais e simulados), com uso de **MQTT**, **Prometheus** e **Flask**, e interface gráfica feita em **React**.

---

## 🚀 Tecnologias Utilizadas

| Tecnologia         | Descrição                                                                 |
|--------------------|---------------------------------------------------------------------------|
| **Python**         | Backend com Flask e scripts de controle para cliente e servidor           |
| **Flask**          | API REST principal e gerenciamento de uploads e métricas                  |
| **React + MUI**    | Frontend com visualização de métricas e interface para configuração       |
| **MQTT (Paho)**    | Comunicação entre servidor e clientes via mensagens assíncronas           |
| **Prometheus**     | Coleta e consulta de métricas do sistema e clientes FL                    |
| **Node.js/NPM**    | Execução e gerenciamento do dashboard frontend                            |
| **Bash**           | Automação com script `manage.sh` para start/stop/status                   |

---

## 🧩 Estrutura do Projeto

```
DASH_HIAAC/
├── Client/
│   └── client_mqtt_listener.py
├── Server/
│   ├── flask-server/
│   │   ├── server_flask.py
│   │   ├── server_mqtt_listener.py
│   │   └── config_servidor.env
│   ├── federated-dashboard/
│   │   └── src/pages/...
│   └── prometheus.yml
├── manage.sh
└── sync_directories.py
```

---

## ⚙️ Pré-requisitos

- Python 3.8+
- Node.js e npm
- Prometheus instalado no sistema (`/usr/bin/prometheus`)
- Acesso à rede com broker MQTT (default: `100.127.13.111`)
- Raspberry Pi (opcional, para testes reais)

---

## 🛠️ Instalação

```bash
# Clone o repositório
git clone https://github.com/Morais727/DASH_HIAAC.git
cd DASH_HIAAC

# Instale dependências do backend
pip install -r requirements.txt  # (dependências a serem especificadas)

# Instale dependências do frontend
cd Server/federated-dashboard
npm install
```

---

## ▶️ Executando os Serviços

Use o script de gerenciamento:

```bash
# Iniciar todos os serviços
./manage.sh start

# Parar todos os serviços
./manage.sh stop

# Verificar status dos serviços
./manage.sh status
```

---

## 🌐 Acessando a Interface Web

Após iniciar os serviços, abra no navegador:

```
http://localhost:5173
```

Você verá o menu principal com opções para:
- Acompanhar Métricas
- Configurar Experimentos
- Configurar IPs dos Clientes

---

## 📄 Uploads e Configurações

- Faça upload dos scripts `client.py`, `server.py` e arquivos `.env` diretamente pela interface.
- Use as flags para indicar se o sistema deve usar os arquivos enviados.
- Configure os IPs dos Raspberry Pis pela aba de configuração.

---

## 📊 Métricas e Visualização

As seguintes métricas são monitoradas e exibidas em tempo real:

| Métrica         | Origem              |
|------------------|---------------------|
| Uso de CPU       | node_exporter       |
| Uso de Memória   | node_exporter       |
| Rede (RX/TX)     | node_exporter       |
| Accuracy         | pushgateway         |
| Loss             | pushgateway         |

---

## 🔀 Comandos Disponíveis (MQTT)

- `start`: Inicia o treinamento FL em todos os clientes conectados
- `stop`: Interrompe a execução
- `down`: Desliga clientes (uso futuro)

---

## 🧪 Exportação de Resultados

- Os gráficos de **Accuracy** e **Loss** podem ser exportados nos formatos:
  - CSV
  - JSON
  - XLSX

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir _issues_, enviar _pull requests_, ou sugerir melhorias.

---

## 📄 Licença

Este projeto é de uso educacional e faz parte das atividades do **Hub de Inteligência Artificial e Arquiteturas Cognitivas (H.IAAC)** - Instituto de Computação - UNICAMP.

---

