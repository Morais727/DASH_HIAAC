import tensorflow as tf
import flwr as fl
import os
import socket
import time
import random
import paho.mqtt.publish as publish
import requests
from model_definition import ModelCreation
from dataset_utils import ManageDatasets 
from prometheus_client import Gauge, start_http_server
import threading

class ClienteFlower(fl.client.NumPyClient):

    def __init__(self, cid):
        self.cid = cid
        self.x_treino, self.y_treino, self.x_teste, self.y_teste = self.load_data()
        self.modelo = self.cria_modelo()

        self.accuracy_metric = Gauge('fl_client_accuracy', 'Acurácia do cliente FL', ['client_id', 'tipo', 'round'])
        self.loss_metric = Gauge('fl_client_loss', 'Loss do cliente FL', ['client_id', 'tipo', 'round'])

    def _log_metrics(self, tipo, accuracy, loss, round_num):
        self.accuracy_metric.labels(client_id=str(self.cid), tipo=tipo, round=str(round_num)).set(accuracy)
        self.loss_metric.labels(client_id=str(self.cid), tipo=tipo, round=str(round_num)).set(loss)

    def load_data(self):
        dataset_name = os.environ.get("DATASET", "MNIST").upper()
        non_iid = os.environ.get("NON_IID", "False").lower() == "true"
        num_clients = int(os.environ.get("NUM_CLIENTS", "5"))
        alpha_env = os.environ.get("DIRICHLET_ALPHA", None)

        # Converte alpha se estiver presente e válido
        alpha = float(alpha_env) if alpha_env is not None else None

        dataset_manager = ManageDatasets(self.cid)

        print(f"Carregando dataset: {dataset_name} | non_iid={non_iid} | n_clients={num_clients} | alpha={alpha}")

        try:
            data = dataset_manager.select_dataset(
                dataset_name=dataset_name,
                n_clients=num_clients,
                non_iid=non_iid,
                alpha=alpha
            )
        except Exception as e:
            print(f"❌ Erro ao carregar dataset {dataset_name}: {e}")
            raise e

        if data is None:
            raise ValueError("❌ Nenhum dataset foi retornado!")

        x_train, y_train, x_test, y_test = data

        # Normaliza se for 2D
        if len(x_train.shape) == 2:
            x_train, x_test = dataset_manager.normalize_data(x_train, x_test)

        # Adiciona canal para CNN
        if len(x_train.shape) == 3:
            x_train = x_train[..., None]
            x_test = x_test[..., None]

        return x_train, y_train, x_test, y_test

    def cria_modelo(self):
        model_type = os.environ.get("MODEL_TYPE", "DNN").upper()
        hf_model_name = os.environ.get("HF_MODEL_URL", "").strip()
        num_classes = len(set(self.y_treino))
        input_shape = self.x_treino.shape

        creator = ModelCreation()

        if model_type == "CNN":
            return creator.create_CNN(input_shape, num_classes)
        elif model_type == "LOGISTICREGRESSION":
            return creator.create_LogisticRegression(input_shape, num_classes)
        elif model_type == "CUSTOM_HF_MODEL" and hf_model_name:
            return creator.create_HuggingFace(hf_model_name, input_shape, num_classes)
        else:
            return creator.create_DNN(input_shape, num_classes)

    def get_parameters(self, config):
        return self.modelo.get_weights()

    def fit(self, parameters, config):
        server_round = int(config['server_round'])

        self.modelo.set_weights(parameters)
        history = self.modelo.fit(self.x_treino, self.y_treino, epochs=1, verbose=1)
        accuracy = history.history["accuracy"][0]
        loss = history.history["loss"][0]
        
        self._log_metrics("train", accuracy, loss, server_round)
        
        return self.modelo.get_weights(), len(self.x_treino), {"accuracy": accuracy, "loss": loss}

    def evaluate(self, parameters, config):
        server_round = int(config['server_round'])

        self.modelo.set_weights(parameters)
        loss, accuracy = self.modelo.evaluate(self.x_teste, self.y_teste)
        
        self._log_metrics("test", accuracy, loss, server_round)

        # ✅ Delay antes de encerrar para garantir que Prometheus colete
        time.sleep(10) 
        
        return loss, len(self.x_teste), {"accuracy": accuracy}

# === Verifica conexão com servidor ===
def check_server_connection(server_ip, port=7070, timeout=10):
    try:
        with socket.create_connection((server_ip, port), timeout):
            return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

# === Main ===
def main():
    cid = int(os.environ.get("CLIENT_ID", 0))
    server_ip = os.environ.get("SERVER_IP", "100.127.13.111").split(":")[0]
    server_port = int(os.environ.get("SERVER_PORT", "7070"))

    while not check_server_connection(server_ip, server_port):
        print("🔁 Tentando reconectar em 30 segundos...")
        time.sleep(30)

    print("✅ Conectado ao servidor. Preparando para iniciar cliente...")

    wait_time = random.uniform(3, 10)
    print(f"⏳ Aguardando {int(wait_time)} segundos antes de iniciar o cliente...")
    time.sleep(wait_time)

    client = ClienteFlower(cid)
    start_http_server(9102)  # inicia servidor Prometheus após o registro das métricas

    try:
        fl.client.start_client(
            server_address=f"{server_ip}:{server_port}",
            client=client
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar cliente: {e}")

if __name__ == "__main__":
    main()
