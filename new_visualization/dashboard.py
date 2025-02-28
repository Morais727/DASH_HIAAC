import streamlit as st
import paramiko
import pandas as pd
import os
import time

# Configuração dos Raspberry Pis
raspberry_ips = ["192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104"]
username = "pi"

# Comandos do Docker
docker_build_command = "docker build -t federated-learning ."
docker_save_command = "docker save federated-learning -o federated-learning.tar"
docker_load_command = "docker load -i /home/pi/federated-learning.tar"
docker_run_command = "docker run --rm --name fl_node -d federated-learning"
docker_stop_command = "docker stop fl_node"

# Função para executar comandos SSH
def execute_ssh_command(ip, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username)
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

# Função para monitorar CPU e RAM
def get_system_metrics(ip):
    cpu_command = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"
    ram_command = "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'"

    cpu_usage, _ = execute_ssh_command(ip, cpu_command)
    ram_usage, _ = execute_ssh_command(ip, ram_command)

    return float(cpu_usage.strip()), float(ram_usage.strip())

# Interface no Streamlit
st.title("🚀 Gerenciamento de Treinamento Federado com Raspberry Pis")

# Seção: Build e Deploy da Imagem
st.header("1️⃣ Build e Deploy da Imagem Docker")

if st.button("🔨 Construir Imagem Docker"):
    with st.spinner("Construindo imagem Docker..."):
        os.system(docker_build_command)
        os.system(docker_save_command)
    st.success("Imagem Docker construída com sucesso!")

if st.button("📤 Enviar Imagem para os Raspberry Pis"):
    with st.spinner("Enviando imagem..."):
        for ip in raspberry_ips:
            os.system(f"scp federated-learning.tar pi@{ip}:/home/pi/")
    st.success("Imagem enviada com sucesso!")

if st.button("📂 Carregar Imagem nos Raspberry Pis"):
    with st.spinner("Carregando imagem..."):
        for ip in raspberry_ips:
            execute_ssh_command(ip, docker_load_command)
    st.success("Imagem carregada com sucesso!")

# Seção: Início e Parada do Treinamento
st.header("2️⃣ Controle do Treinamento")

if st.button("🚀 Iniciar Treinamento"):
    with st.spinner("Iniciando treinamento..."):
        for ip in raspberry_ips:
            execute_ssh_command(ip, docker_run_command)
    st.success("Treinamento iniciado com sucesso!")

if st.button("🛑 Encerrar Treinamento"):
    with st.spinner("Encerrando treinamento..."):
        for ip in raspberry_ips:
            execute_ssh_command(ip, docker_stop_command)
    st.success("Treinamento encerrado!")

# Seção: Monitoramento em Tempo Real
st.header("3️⃣ Monitoramento dos Raspberry Pis")

if st.button("📊 Atualizar Monitoramento"):
    with st.spinner("Obtendo métricas..."):
        data = []
        for ip in raspberry_ips:
            cpu, ram = get_system_metrics(ip)
            data.append({"IP": ip, "CPU (%)": cpu, "RAM (%)": ram})

        df = pd.DataFrame(data)
        st.dataframe(df)

        # Gráficos interativos
        st.subheader("📈 Uso de CPU (%)")
        st.line_chart(df.set_index("IP")["CPU (%)"])

        st.subheader("📈 Uso de RAM (%)")
        st.line_chart(df.set_index("IP")["RAM (%)"])
