import paramiko
import time

# Lista de IPs dos Raspberry Pis
raspberry_ips = ["100.97.70.44", "100.99.55.62", "100.112.180.2", "100.91.59.20"]
username = "pi"  # Usuário SSH

# Comando para rodar o contêiner (substitua pelo seu comando real)
docker_command = "docker run --rm --name fl_node -d federated-learning"

def execute_ssh_command(ip, command):
    """Executa um comando SSH remoto e retorna a saída."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username)
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

# Iniciar os contêineres nos Raspberry Pis
for ip in raspberry_ips:
    print(f"🚀 Iniciando contêiner em {ip}...")
    out, err = execute_ssh_command(ip, docker_command)
    if err:
        print(f"❌ Erro em {ip}: {err}")
    else:
        print(f"✅ Contêiner iniciado em {ip}")

print("🏁 Treinamento iniciado em todos os dispositivos!")
