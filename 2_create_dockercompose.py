import os
import argparse
import random


def add_server_info(clients, rounds, algorithm, solution, dataset, model, poc, decay):
    server_str = f"""version: '3'
services:
  server:
    image: 'acsp-fl-server:latest'
    container_name: fl_server
    environment:
      - SERVER_IP=0.0.0.0:8080  # O servidor escutará em todas as interfaces
      - NUM_CLIENTS={clients}
      - NUM_ROUNDS={rounds}
      - ALGORITHM={algorithm}
      - POC={poc}
      - SOLUTION_NAME={solution}
      - DATASET={dataset}
      - MODEL={model}
      - DECAY={decay}
    volumes:
      - ./logs:/logs
    ports:
      - "8080:8080"  # Expõe a porta para permitir conexões externas
    networks:
      - fl_network

networks:
  fl_network:
    driver: bridge
    \n\n
"""
    return server_str


def add_client_info(num_clients, id_client, server_ip, model, client_selection, local_epochs, solution, algorithm,
                    dataset, poc, decay, transmittion_threshold, personalization, shared_layers):
    client_str = f"""version: '3'
services:
  client-{id_client}:
    image: 'acsp-fl-client:latest'
    environment:
      - SERVER_IP={server_ip}:8080
      - CLIENT_ID={id_client}
      - N_CLIENTS={num_clients}
      - MODEL={model}
      - CLIENT_SELECTION={client_selection}
      - LOCAL_EPOCHS={local_epochs}
      - SOLUTION_NAME={solution}
      - ALGORITHM={algorithm}
      - DATASET={dataset}
      - POC={poc}
      - DECAY={decay}
      - TRANSMISSION_THRESHOLD={transmittion_threshold}
      - PERSONALIZATION={personalization}
      - SHARED_LAYERS={shared_layers}
      - TIME2STARTMIN=0   # 🔹 Adicionado para evitar erro
      - TIME2STARTMAX=30  # 🔹 Adicionado para evitar erro
    volumes:
      - ./logs:/logs
    networks:
      - fl_network
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: "{random.uniform(0.01, 4.00)}"

networks:
  fl_network:
    driver: bridge
    \n\n
"""
    return client_str



def main():
    parser = argparse.ArgumentParser(description="Generate Docker Compose files for FL deployment")

    parser.add_argument("-c", "--clients", type=int, required=True, help="Number of clients")
    parser.add_argument("-m", "--model", type=str, default='LR', help="Model type")
    parser.add_argument("--client-selection", type=str, required=True, help="Client selection method")
    parser.add_argument("-e", "--local-epochs", type=int, default=1, help="Number of local epochs")
    parser.add_argument("-s", "--solution", type=str, default="ACSP-FL", help="Solution name")
    parser.add_argument("-a", "--algorithm", type=str, default="DEEV", help="Federated algorithm")
    parser.add_argument("-d", "--dataset", type=str, required=True, help="Dataset to use")
    parser.add_argument("-r", "--rounds", type=int, default=100, help="Number of communication rounds")
    parser.add_argument("--poc", type=float, default=0, help="Percentage of clients selected using PoC")
    parser.add_argument("--decay", type=float, default=0, help="Decay factor for DEEV and ACSP-FL")
    parser.add_argument("-t", "--threshold", type=float, default=0.2, help="Transmission threshold")
    parser.add_argument("-p", "--personalization", action='store_true', help="Enable personalization")
    parser.add_argument("--shared-layers", type=int, default=0, help="Number of layers to share in personalization")
    parser.add_argument("--server-ip", type=str, required=True, help="IP address of the server FL")

    args = parser.parse_args()

    # Gera o arquivo do SERVIDOR
    server_filename = "docker-compose-server.yml"
    with open(server_filename, 'w') as server_file:
        server_str = add_server_info(args.clients, args.rounds, args.algorithm, args.solution,
                                     args.dataset, args.model, args.poc, args.decay)
        server_file.write(server_str)

    print(f"Docker Compose file for SERVER '{server_filename}' generated successfully.")

    # Gera o arquivo dos CLIENTES
    client_filename = "docker-compose-client.yml"
    with open(client_filename, 'w') as client_file:
        for id_client in range(args.clients):
            client_str = add_client_info(args.clients, id_client, args.server_ip, args.model,
                                         args.client_selection, args.local_epochs, args.solution,
                                         args.algorithm, args.dataset, args.poc, args.decay,
                                         args.threshold, args.personalization, args.shared_layers)
            client_file.write(client_str)

    print(f"Docker Compose file for CLIENTS '{client_filename}' generated successfully.")


if __name__ == '__main__':
    main()


