```markdown
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

```

Recebe filename (local /tmp)
Monta filename equivalente no /Volumes (replace "/tmp" -> "/Volumes/...")

candidates = [todos os caminhos que existem]

Se candidates vazio:
retorna False

Para cada caminho em candidates:
tenta abrir com xarray
valida presença de dims: time + (lat/latitude) + (lon/longitude)
se params fornecido, valida se variável existe
força leitura (mean no tempo) para garantir integridade
se OK -> retorna True

Se nenhum candidato válido:
retorna False

```

### `generate_tiles(lat_min, lat_max, lon_min, lon_max, step=10)`

```

Para lat de lat_min até lat_max em passos step:
Para lon de lon_min até lon_max em passos step:
yield (lat0, lat1, lon0, lon1)

```

### `generate_daily_intervals(start_date, end_date, max_days=366)`

```

Divide o intervalo [start_date..end_date] em subintervalos de no máximo 366 dias:
yield (sub_start, sub_end)

```

### `mosaic_metadata_only(files, out_nc, var)`

```

Lê apenas metadados (lat/lon/time) de cada tile file
Define regiões (no código atual: slice(None) para tudo)
Abre cada dataset, seleciona somente a variável var
Remove "cell_methods" se existir
Combina por coordenadas (combine_by_coords)
Salva o mosaico em out_nc
Fecha datasets

```

### `create_all_mosaics()`

```

Para cada param em PARAMS:
Lista tiles .nc em:
/tmp/nasa_power/raw/<param>/
/Volumes/.../nasa_power/raw/<param>/
Une listas sem duplicar

Agrupa arquivos por (sub_start, sub_end) extraídos do nome

Para cada grupo (sub_start, sub_end):
out = /tmp/nasa_power/raw/<param>*mosaico*<start>_<end>.nc

```
Se mosaico existe e está mais novo que os tiles:
  pula
Senão:
  cria mosaico com mosaic_metadata_only()
```

```

### `process_netcdf()`

```

Para cada var em PARAMS:
in_files = listar /tmp/nasa_power/raw/<var>*mosaico**.nc
Se vazio: log e continua

ref_file = primeiro arquivo (referência de lat/lon)
ref_shape = (len(lat_ref), len(lon_ref))

Para cada input_nc em in_files:
output_nc = input_nc + "_proc.nc"
Se output_nc já é válido (check_and_validate_file):
pula

```
Abre input_nc
Se var não existe: fecha e continua

Se shape lat/lon maior que referência:
  corta (isel) para ref_shape

Salva temp_proc.nc

Aplica CDO:
  - WS2M: *3.6
  - ALLSKY_*: /3.6
  - Outros: copy

Escreve output_nc e remove temp_proc
```

```

### `write_incremental_icechunk_by_year(overwrite=False)`

```

Define:
out_path local (/tmp/.../nasapower_dataset.zarr)
out_path_vol (/Volumes/.../nasapower_dataset.zarr)
params_dir = "/tmp/nasa_power/raw"
compressor = Blosc(zstd)

Se overwrite:
remove out_path e out_path_vol

Cria/abre repo local em out_path
Sincroniza out_path -> out_path_vol
Abre repo no volume (repo_vol)

Descobre anos disponíveis:
para cada param:
lista **mosaico**_*_proc.nc
extrai ano e adiciona em years

Se years vazio:
retorna NOOP

Para cada year em years:
abre sessão gravável (ic_session) no branch main
wrote_this_year = False

Para cada param:
lista arquivos anuais daquele param e year
se não tem: continua

```
abre cada arquivo anual
remove duplicatas de lat/lon/time (clean_dataset_duplicates)
concatena no tempo e remove duplicatas de time

cria dataset final (float32 + attrs + CRS EPSG:4326)
ordena e remove duplicatas (time/lat/lon)

group_path = "variables/<param>"

Se grupo existe:
  lê existing_times
  escreve apenas novos times (append no tempo)
Senão:
  cria grupo (write) com encoding/chunks

wrote_this_year = True
```

Se wrote_this_year:
commit e reset do branch main para o snapshot
gc.collect()

Retorna WROTE com snapshot se escreveu algo; senão NOOP

```

---

## 2) `orchestrate_download()` — download por variável com data inicial baseada no Zarr

```

orchestrate_download():
tiles_to_download = []
BR_RECT = bounding box do Brasil

start_by_param = {param: START_DATE}  # fallback

Se ZARR_VOL existe:
abre Icechunk repo (readonly main)
para cada param:
abre grupo variables/<param>
se não existe time: continue

```
  lê time cru (int)
  lê attrs units/calendar
  decodifica (decode_cf_datetime)
  tmax = maior data existente
  start_eff = (tmax + 1 dia) em YYYYMMDD
  start_by_param[param] = start_eff
```

loga start_by_param

Para cada param:
param_start = start_by_param[param]
se param_start > END_DATE: pula param

```
Para cada tile espacial (10x10) que intersecta BR_RECT:
  Para cada intervalo temporal anual em [param_start..END_DATE]:
    monta params_dict (make_parameters)
    monta filename do tile
    adiciona (param_path, params_dict, filename) em tiles_to_download
```

Para cada item em tiles_to_download:
download_single_tile() com retry
valida arquivo baixado (check_and_validate_file)

```

---

## 3) Fluxo principal `main()`

```

main():
orchestrate_download()                # baixa tiles NASA POWER
create_all_mosaics()                  # mosaicos por variável/intervalo
process_netcdf()                      # padroniza shape + CDO -> *_proc.nc
write_incremental_icechunk_by_year()  # escreve incremental no Icechunk/Zarr

delete_local_nc_files()               # limpeza local
sync_volume(DOWNLOAD_PATH, TARGET_DIR)# sincroniza /tmp -> volume/dbfs

print snapshot final

```
```
