import os
import argparse
import random


def add_server_info(clients, rounds, algorithm, solution, dataset, model, poc, decay):
    server_str = f"  server:\n\
    image: 'acsp-fl-server:latest'\n\
    container_name: fl_server\n\
    environment:\n\
      - SERVER_IP=172.18.0.1:8080\n\
      - NUM_CLIENTS={clients}\n\
      - NUM_ROUNDS={rounds}\n\
      - ALGORITHM={algorithm}\n\
      - POC={poc}\n\
      - SOLUTION_NAME={solution}\n\
      - DATASET={dataset}\n\
      - MODEL={model}\n\
      - DECAY={decay}\n\
    volumes:\n\
      - ./logs:/logs\n\
    networks:\n\
      - default\n\
    deploy:\n\
      replicas: 1\n\
      placement:\n\
        constraints:\n\
          - node.role==manager\n\
    \n\n"

    return server_str


def add_client_info(num_clients, id_client, model, client_selection, local_epochs, solution, algorithm,
                    dataset, poc, decay, transmittion_threshold, personalization, shared_layers):
    client_str = f"  client-{id_client}:\n\
    image: 'acsp-fl-client:latest'\n\
    environment:\n\
      - SERVER_IP=fl_server:8080\n\
      - CLIENT_ID={id_client}\n\
      - N_CLIENTS={num_clients}\n\
      - MODEL={model}\n\
      - CLIENT_SELECTION={client_selection}\n\
      - LOCAL_EPOCHS={local_epochs}\n\
      - SOLUTION_NAME={solution}\n\
      - ALGORITHM={algorithm}\n\
      - DATASET={dataset}\n\
      - POC={poc}\n\
      - DECAY={decay}\n\
      - TRANSMISSION_THRESHOLD={transmittion_threshold}\n\
      - PERSONALIZATION={personalization}\n\
      - SHARED_LAYERS={shared_layers}\n\
      - TIME2STARTMIN=0\n\
      - TIME2STARTMAX=30\n\
    volumes:\n\
      - ./logs:/logs\n\
    networks:\n\
      - default\n\
    deploy:\n\
      replicas: 1\n\
      resources:\n\
        limits:\n\
          cpus: \"{random.uniform(0.01, 6)}\"\n\
      placement:\n\
        constraints:\n\
          - node.role==worker\n\
          \n\n"

    return client_str


def main():
    parser = argparse.ArgumentParser(description="Generate Docker Compose file for FL simulation")

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

    args = parser.parse_args()

    # Geração correta do nome do arquivo
    filename = f"{args.client_selection}-{args.clients}-{args.dataset}.yaml"

    with open(filename, 'w') as dockercompose_file:
        header = f"version: '3'\nservices:\n\n"
        dockercompose_file.write(header)

        server_str = add_server_info(args.clients, args.rounds, args.algorithm, args.solution,
                                     args.dataset, args.model, args.poc, args.decay)

        dockercompose_file.write(server_str)

        for id_client in range(args.clients):
            client_str = add_client_info(args.clients, id_client, args.model, args.client_selection, args.local_epochs,
                                         args.solution, args.algorithm, args.dataset, args.poc, args.decay,
                                         args.threshold, args.personalization, args.shared_layers)

            dockercompose_file.write(client_str)

    print(f"Docker Compose file '{filename}' generated successfully.")


if __name__ == '__main__':
    main()
