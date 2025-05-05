import os
import shutil
import hashlib
import time

ORIGEM_DIR = os.path.abspath(".")
DESTINO_DIR = "/mnt/fl_clients"
PASTAS = ["Server", "Client"]

INTERVALO_CHECAGEM = 30  # segundos

def calcular_md5(caminho_arquivo):
    hash_md5 = hashlib.md5()
    try:
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return None

def sincronizar_pasta(origem, destino, forcar_copia=False):
    for root, _, files in os.walk(origem):
        for file in files:
            caminho_origem = os.path.join(root, file)
            caminho_relativo = os.path.relpath(caminho_origem, origem)
            caminho_destino = os.path.join(destino, caminho_relativo)

            copiar = False

            if forcar_copia:
                copiar = True
            else:
                origem_hash = calcular_md5(caminho_origem)
                destino_hash = calcular_md5(caminho_destino)
                if origem_hash != destino_hash:
                    copiar = True

            if copiar:
                os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"🔄 Arquivo copiado/atualizado: {caminho_relativo}")

def sincronizacao_inicial():
    print("🚀 Realizando sincronização completa inicial...")
    for pasta in PASTAS:
        origem = os.path.join(ORIGEM_DIR, pasta)
        destino = os.path.join(DESTINO_DIR, pasta)

        if not os.path.exists(origem):
            print(f"⚠️ Diretório de origem não encontrado: {origem}")
            continue

        sincronizar_pasta(origem, destino, forcar_copia=True)

def monitorar_e_sincronizar():
    print("👀 Iniciando monitoramento por mudanças... (Ctrl+C para parar)")
    while True:
        for pasta in PASTAS:
            origem = os.path.join(ORIGEM_DIR, pasta)
            destino = os.path.join(DESTINO_DIR, pasta)

            if not os.path.exists(origem):
                print(f"⚠️ Diretório de origem não encontrado: {origem}")
                continue

            sincronizar_pasta(origem, destino)

        time.sleep(INTERVALO_CHECAGEM)

if __name__ == "__main__":
    try:
        sincronizacao_inicial()
        monitorar_e_sincronizar()
    except KeyboardInterrupt:
        print("\n⏹️ Monitoramento encerrado pelo usuário.")