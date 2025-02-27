FROM python:3.9-slim
#FROM arm64v8/python:3.9

ADD data ./data
ADD client.py .


ADD dataset_utils.py .
ADD model_definition.py .

# Atualiza o gerenciador de pacotes e instala dependências essenciais
RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*

# Cria um ambiente virtual para evitar conflitos de pacotes
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install -U pip

# Atualiza o pip
RUN pip install --upgrade pip

# Instala versões compatíveis das bibliotecas
RUN pip install --no-cache-dir numpy==1.23.5 pandas==1.5.3 tensorflow==2.10.1 flwr==1.2.0 scikit-learn


CMD ["python", "-u", "client.py"]
