#!/bin/bash

# 1️⃣ Build da imagem Docker localmente
echo "🔨 Construindo imagem Docker..."
docker build -t federated-learning .

# 2️⃣ Exportando imagem para um arquivo
echo "📦 Salvando imagem Docker..."
docker save federated-learning -o federated-learning.tar

# Lista de IPs dos Raspberry Pis
raspberry_ips=("192.168.1.101" "192.168.1.102" "192.168.1.103" "192.168.1.104")

# 3️⃣ Enviando imagem para os Raspberry Pis
echo "🚀 Enviando imagem para os Raspberry Pis..."
for ip in "${raspberry_ips[@]}"; do
    scp federated-learning.tar pi@$ip:/home/pi/
done

# 4️⃣ Carregando a imagem Docker nos Raspberry Pis
echo "📂 Carregando imagem Docker nos dispositivos..."
for ip in "${raspberry_ips[@]}"; do
    ssh pi@$ip "docker load -i /home/pi/federated-learning.tar"
done

# 5️⃣ Iniciando os contêineres
echo "🏁 Iniciando treinamento em todos os dispositivos..."
for ip in "${raspberry_ips[@]}"; do
    ssh pi@$ip "docker run --rm --name fl_node -d federated-learning"
done

echo "✅ Processo concluído com sucesso!"


#chmod +x deploy_and_run.sh


#./deploy_and_run.sh