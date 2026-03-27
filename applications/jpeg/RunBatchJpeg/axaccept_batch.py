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
OUTPUT_JPEG_DIR = Path("./src/dataset_error_rate_1e-4")
# Nova raiz para os logs de simulação
LOG_DIR = Path("./src/logs")

def run_conversion():
    # Garante que os diretórios de saída existam
    OUTPUT_JPEG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list(DATASET_DIR.rglob("*.csv"))
    
    if not csv_files:
        print(f"Nenhum arquivo .csv encontrado em {DATASET_DIR}")
        return

    print(f"Encontrados {len(csv_files)} arquivos para processar.")

    for input_csv in csv_files:
        # 1. Calcula o caminho relativo (ex: test/monkey/img_05638.csv)
        relative_path = input_csv.relative_to(DATASET_DIR)
        
        # 2. Define o destino da imagem e do log mantendo a hierarquia
        output_jpeg = OUTPUT_JPEG_DIR / relative_path.with_suffix(".jpeg")
        output_log = LOG_DIR / relative_path.with_suffix(".log")

        # 3. Cria as subpastas necessárias em ambos os destinos
        output_jpeg.parent.mkdir(parents=True, exist_ok=True)
        output_log.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processando: {relative_path}")
        print(f"  -> Imagem: {output_jpeg.relative_to(OUTPUT_JPEG_DIR)}")
        print(f"  -> Log:    {output_log.relative_to(LOG_DIR)}")

        cmd = [
            "axpike",
            "--adele=mem_read_prob:1e-4,linesz:32",
            "--adele-activate=0:AXRAM",
            "--dc=128:8:32",
            "--ic=256:4:32",
            "--l2=1024:4:32",
            "pk",
            "./src/toojpeg_encoder",
            "100"
        ]

        try:
            # Redirecionamento triplo:
            # stdin  <- arquivo CSV original
            # stdout -> arquivo JPEG (imagem codificada)
            # stderr -> arquivo LOG (estatísticas do AxPike)
            with open(input_csv, "r") as f_in, \
                 open(output_jpeg, "wb") as f_out, \
                 open(output_log, "w") as f_log:
                
                result = subprocess.run(
                    cmd, 
                    stdin=f_in, 
                    stdout=f_out, 
                    stderr=f_log, 
                    text=True
                )
            
            if result.returncode != 0:
                # O log já contém os detalhes do erro/aviso
                pass 
                
        except Exception as e:
            print(f"  [!] Falha crítica no arquivo {input_csv.name}: {e}")

    print(f"\nConcluído!")
    print(f"Imagens em: {OUTPUT_JPEG_DIR}")
    print(f"Logs em:    {LOG_DIR}")

if __name__ == "__main__":
    run_conversion()