import tensorflow as tf
import numpy as np
import random
import pickle
import pandas as pd
from sklearn.preprocessing import Normalizer
import logging

logging.getLogger("tensorflow").setLevel(logging.ERROR)

class ManageDatasets:

    def __init__(self, cid):
        self.cid = cid

    def load_UCIHAR(self):
        with open(f'Client/data/UCI-HAR/{self.cid +1}_train.pickle', 'rb') as train_file:
            train = pickle.load(train_file)

        with open(f'./data/UCI-HAR/{self.cid+1}_test.pickle', 'rb') as test_file:
            test = pickle.load(test_file)

        train['label'] = train['label'].apply(lambda x: x -1)
        y_train = train['label'].values
        train.drop('label', axis=1, inplace=True)
        x_train = train.values

        test['label'] = test['label'].apply(lambda x: x -1)
        y_test = test['label'].values
        test.drop('label', axis=1, inplace=True)
        x_test = test.values

        return x_train, y_train, x_test, y_test

    def load_ExtraSensory(self):
        with open(f'./data/ExtraSensory/x_train_client_{self.cid+1}.pickle', 'rb') as x_train_file:
            x_train = pickle.load(x_train_file)

        with open(f'./data/ExtraSensory/x_test_client_{self.cid+1}.pickle', 'rb') as x_test_file:
            x_test = pickle.load(x_test_file)
        
        with open(f'./data/ExtraSensory/y_train_client_{self.cid+1}.pickle', 'rb') as y_train_file:
            y_train = pickle.load(y_train_file)

        with open(f'./data/ExtraSensory/y_test_client_{self.cid+1}.pickle', 'rb') as y_test_file:
            y_test = pickle.load(y_test_file)

        y_train = np.array(y_train) + 1
        y_test  = np.array(y_test) + 1

        return x_train, y_train, x_test, y_test

    def load_MotionSense(self):
        with open(f'./data/motion_sense/{self.cid+1}_train.pickle', 'rb') as train_file:
            train = pickle.load(train_file)
        
        with open(f'./data/motion_sense/{self.cid+1}_test.pickle', 'rb') as test_file:
            test = pickle.load(test_file)
        
        y_train = train['activity'].values
        train.drop('activity', axis=1, inplace=True)
        train['subject'] /= 24.0
        train['trial']   /= 16.0
        x_train = train.values

        y_test = test['activity'].values
        test.drop('activity', axis=1, inplace=True)
        test['subject'] /= 24.0
        test['trial']   /= 16.0
        x_test = test.values
        
        return x_train, y_train, x_test, y_test

    def load_MNIST(self, n_clients, non_iid=False, alpha=None):
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        if non_iid and alpha:
            x_train, y_train = self.partition_with_dirichlet(x_train, y_train, n_clients, alpha)
            x_test, y_test   = self.partition_with_dirichlet(x_test, y_test, n_clients, alpha)
        else:
            x_train, y_train, x_test, y_test = self.slipt_dataset(x_train, y_train, x_test, y_test, n_clients)

        return x_train, y_train, x_test, y_test

    def load_CIFAR100(self, n_clients, non_iid=False, alpha=None):
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar100.load_data()
        y_train, y_test = y_train.flatten(), y_test.flatten()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        if non_iid and alpha:
            x_train, y_train = self.partition_with_dirichlet(x_train, y_train, n_clients, alpha)
            x_test, y_test   = self.partition_with_dirichlet(x_test, y_test, n_clients, alpha)
        else:
            x_train, y_train, x_test, y_test = self.slipt_dataset(x_train, y_train, x_test, y_test, n_clients)

        return x_train, y_train, x_test, y_test

    def load_CIFAR10(self, n_clients, non_iid=False, alpha=None):
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
        y_train, y_test = y_train.flatten(), y_test.flatten()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        if non_iid and alpha:
            x_train, y_train = self.partition_with_dirichlet(x_train, y_train, n_clients, alpha)
            x_test, y_test   = self.partition_with_dirichlet(x_test, y_test, n_clients, alpha)
        else:
            x_train, y_train, x_test, y_test = self.slipt_dataset(x_train, y_train, x_test, y_test, n_clients)

        return x_train, y_train, x_test, y_test

    def slipt_dataset(self, x_train, y_train, x_test, y_test, n_clients):
        if x_train is None or y_train is None or x_test is None or y_test is None:
            raise ValueError("Erro: Os dados do dataset não foram carregados corretamente!")

        if n_clients is None:
            raise ValueError("Erro: n_clients está como None!")

        print(f"Dividindo dataset: {len(x_train)} amostras entre {n_clients} clientes.")

        p_train = int(len(x_train)/n_clients)
        p_test  = int(len(x_test)/n_clients)

        random.seed(self.cid)
        selected_train = random.sample(range(len(x_train)), p_train)

        random.seed(self.cid)
        selected_test  = random.sample(range(len(x_test)), p_test)
        
        x_train  = x_train[selected_train]
        y_train  = y_train[selected_train]

        x_test   = x_test[selected_test]
        y_test   = y_test[selected_test]

        return x_train, y_train, x_test, y_test

    def partition_with_dirichlet(self, x_data, y_data, n_clients, alpha):
        classes = np.unique(y_data)
        client_indices = [[] for _ in range(n_clients)]
        class_indices = {cls: np.where(y_data == cls)[0] for cls in classes}

        for cls in classes:
            idxs = class_indices[cls]
            np.random.shuffle(idxs)
            proportions = np.random.dirichlet(alpha * np.ones(n_clients))

            splits = (proportions * len(idxs)).astype(int)

            while np.sum(splits) < len(idxs):
                splits[np.random.randint(0, n_clients)] += 1
            while np.sum(splits) > len(idxs):
                splits[np.random.randint(0, n_clients)] -= 1

            start = 0
            for i in range(n_clients):
                end = start + splits[i]
                client_indices[i].extend(idxs[start:end])
                start = end

        selected_idx = client_indices[self.cid]
        return x_data[selected_idx], y_data[selected_idx]

    def select_dataset(self, dataset_name, n_clients, non_iid=False, alpha=None):
        if dataset_name == 'MNIST':
            return self.load_MNIST(n_clients, non_iid, alpha)
        elif dataset_name == 'CIFAR100':
            return self.load_CIFAR100(n_clients, non_iid, alpha)
        elif dataset_name == 'CIFAR10':
            return self.load_CIFAR10(n_clients, non_iid, alpha)
        elif dataset_name == 'MotionSense':
            return self.load_MotionSense()
        elif dataset_name == 'ExtraSensory':
            return self.load_ExtraSensory()
        elif dataset_name == 'UCIHAR':
            return self.load_UCIHAR()

    def normalize_data(self, x_train, x_test):
        x_train = Normalizer().fit_transform(np.array(x_train))
        x_test  = Normalizer().fit_transform(np.array(x_test))
        return x_train, x_test
