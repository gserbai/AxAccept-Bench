######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

import os
import subprocess
from pathlib import Path

# Configurações de diretório
DATASET_DIR = Path("./src/dataset_csv")
OUTPUT_JPEG_DIR = Path("./src/dataset_error_rate_1.4e-1")

def run_conversion():
    # Garante que o diretório de saída existe
    OUTPUT_JPEG_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Busca todos os arquivos .csv recursivamente (similar ao find)
    csv_files = list(DATASET_DIR.rglob("*.csv"))
    
    if not csv_files:
        print(f"Nenhum arquivo .csv encontrado em {DATASET_DIR}")
        return

    print(f"Encontrados {len(csv_files)} arquivos para processar.")

    for input_csv in csv_files:
        # 2. Calcula o caminho relativo para espelhar a estrutura de pastas
        relative_path = input_csv.relative_to(DATASET_DIR)
        output_jpeg = OUTPUT_JPEG_DIR / relative_path.with_suffix(".jpeg")

        # 3. Cria a subpasta necessária
        output_jpeg.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processando: {relative_path} -> {output_jpeg.name}")

        # 4. Configuração do comando AxPike
        # Montamos como uma lista para evitar problemas com espaços ou caracteres especiais
        cmd = [
            "axpike",
            "--adele=mem_read_prob:1.4e-1,linesz:32",
            "--adele-activate=0:AXRAM",
            "--dc=128:8:32",
            "--ic=256:4:32",
            "--l2=1024:4:32",
            "pk",
            "./applications/jpeg/src/toojpeg_encoder",
            "100"
        ]

        try:
            # Execução segura:
            # f_in: fornece os pixels do CSV para o stdin do simulador
            # f_out: captura a imagem gerada (stdout) e salva no arquivo .jpeg
            with open(input_csv, "r") as f_in, open(output_jpeg, "wb") as f_out:
                result = subprocess.run(
                    cmd, 
                    stdin=f_in, 
                    stdout=f_out, 
                    stderr=subprocess.PIPE, 
                    text=False
                )
            
            if result.returncode != 0:
                print(f"  [!] Erro ao processar {input_csv.name}: {result.stderr.decode().strip()}")
                
        except Exception as e:
            print(f"  [!] Falha crítica no arquivo {input_csv.name}: {e}")

    print(f"\nConcluído! Estrutura de pastas mantida em {OUTPUT_JPEG_DIR}.")

if __name__ == "__main__":
    run_conversion()
