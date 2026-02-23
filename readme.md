# Pseudocódigo — Pipeline NASA POWER → mosaicos → processamento → Icechunk/Zarr

Este pseudocódigo descreve o fluxo principal do script: baixar dados diários do NASA POWER por tiles espaciais e intervalos de tempo, gerar mosaicos, padronizar os NetCDF e escrever incrementalmente em um repositório Icechunk/Zarr.

---

## 0) Inicialização e configuração

- Adiciona o `workspace_root` ao `sys.path`
- Importa bibliotecas (xarray, geopandas, icechunk, zarr, requests, etc.)
- Define regex `_TIME_RE` para extrair datas `(start, end)` do nome do `.nc`

Define caminhos:
- `TMP_PATH = "/tmp/nasa_power"`
- `DOWNLOAD_PATH = TMP_PATH + "/raw"`
- `LOG_PATH = TMP_PATH + "/process_nasapower.log"`
- `ZARR_VOL = "/Volumes/.../nasapower_dataset.zarr"`
- `TARGET_DIR = "dbfs:/Volumes/.../nasa_power/raw"`

Define parâmetros NASA POWER:
- `BASE_API`, `COMMUNITY`, `OUT_FORMAT`, `UNITS`, `TIME_STANDARD`
- `PARAMS = [lista de variáveis]`
- `START_DATE = "19990101"`
- `END_DATE = hoje - 3 dias`

Cria sessão HTTP (`requests.Session`) com User-Agent

Carrega shapefile do Brasil (EPSG:4326):
- Obtém `total_bounds` (minx, miny, maxx, maxy)
- Ajusta limites para múltiplos de 10 graus (tiles 10x10)
- `MAX_DEG = 10.0`

---

## 1) Funções auxiliares (resumo)

### `check_and_validate_file(filename, params=None)`
