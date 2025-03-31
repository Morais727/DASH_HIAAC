#!/bin/bash

# Lista de IPs
IPS=("100.97.70.44" "100.99.55.62" "100.112.180.2" "100.91.59.20")

# Usuário SSH
USER="pi"

# Comando para abrir um terminal
TERMINAL="gnome-terminal"

# Obtém a tela principal e sua resolução
PRIMARY_SCREEN=$(xrandr | grep " primary" | awk '{print $1}')
SCREEN_RESOLUTION=$(xrandr | grep -A1 "$PRIMARY_SCREEN" | tail -n1 | awk '{print $1}')

# Extrai largura e altura da tela principal
SCREEN_WIDTH=$(echo "$SCREEN_RESOLUTION" | cut -dx -f1 | tr -d '\n')
SCREEN_HEIGHT=$(echo "$SCREEN_RESOLUTION" | cut -dx -f2 | tr -d '\n')

# Calcula a posição e tamanho exatos para ocupar 1/4 da tela
HALF_WIDTH=$((SCREEN_WIDTH / 2))
HALF_HEIGHT=$((SCREEN_HEIGHT / 2))

# Define as posições exatas (x, y, largura, altura)
POSICOES=(
    "0,0,$HALF_WIDTH,$HALF_HEIGHT"                  # Superior esquerdo
    "$HALF_WIDTH,0,$HALF_WIDTH,$HALF_HEIGHT"         # Superior direito
    "0,$HALF_HEIGHT,$HALF_WIDTH,$HALF_HEIGHT"        # Inferior esquerdo
    "$HALF_WIDTH,$HALF_HEIGHT,$HALF_WIDTH,$HALF_HEIGHT"  # Inferior direito
)

# Contador de janelas
i=0

# Loop para abrir os terminais e conectar via SSH
for IP in "${IPS[@]}"; do
    $TERMINAL --geometry=80x24 -- bash -c "ssh $USER@$IP; exec bash" &  # Abre o terminal
    sleep 0.5  # Pequena pausa para garantir que a janela foi aberta

    # Obtém o ID da última janela aberta e ajusta posição/tamanho
    wmctrl -r ":ACTIVE:" -e "0,${POSICOES[i]}"
    
    ((i++))
done
