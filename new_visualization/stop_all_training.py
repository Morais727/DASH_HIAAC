import paramiko
import time

# Lista de IPs dos Raspberry Pis
raspberry_ips = ["192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104"]
username = "pi"  # Usuário SSH

stop_command = "docker stop fl_node"

# Comando para rodar o contêiner (substitua pelo seu comando real)
docker_command = "docker run --rm --name fl_node -d federated-learning"

def execute_ssh_command(ip, command):
    """Executa um comando SSH remoto e retorna a saída."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username)
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

for ip in raspberry_ips:
    print(f"🛑 Parando contêiner em {ip}...")
    out, err = execute_ssh_command(ip, stop_command)
    if err:
        print(f"❌ Erro em {ip}: {err}")
    else:
        print(f"✅ Contêiner parado em {ip}")

print("🏁 Todos os treinamentos foram encerrados!")
