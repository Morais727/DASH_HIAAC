#!/bin/bash

echo "🛑 Parando todos os contêineres em execução..."
docker stop $(docker ps -q)

echo "🧹 Removendo TODOS os contêineres..."
docker rm $(docker ps -aq)

echo "📦 Removendo TODAS as imagens Docker..."
docker rmi $(docker images -q) -f

echo "🗑️  Limpando volumes e cache..."
docker system prune -af --volumes

echo "✅ Docker completamente limpo! 🚀"
