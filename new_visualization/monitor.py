import paramiko
import pandas as pd
import time
import streamlit as st  # Adicionando Streamlit para exibir os dados

# Lista de IPs dos Raspberry Pis
raspberry_ips = ["192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104"]
username = "pi"

# Função para executar comandos SSH remotamente
def execute_ssh_command(ip, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username)
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode().strip()

# Função para obter métricas de CPU e RAM
def get_system_metrics(ip):
    cpu_command = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"
    ram_command = "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'"

    cpu_usage = execute_ssh_command(ip, cpu_command)
    ram_usage = execute_ssh_command(ip, ram_command)

    return float(cpu_usage), float(ram_usage)

# Criando DataFrame para monitoramento
data = []
for ip in raspberry_ips:
    cpu, ram = get_system_metrics(ip)
    data.append({"IP": ip, "CPU (%)": cpu, "RAM (%)": ram})

df = pd.DataFrame(data)

# Exibir dados no Streamlit
st.title("Monitoramento dos Raspberry Pis")
st.dataframe(df)

# Plotar gráfico interativo no Streamlit
st.subheader("📊 Uso de CPU (%)")
st.line_chart(df.set_index("IP")["CPU (%)"])

st.subheader("📊 Uso de RAM (%)")
st.line_chart(df.set_index("IP")["RAM (%)"])
