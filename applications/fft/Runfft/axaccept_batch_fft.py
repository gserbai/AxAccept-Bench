######################################################################
# AxAccept-Bench (Audio FFT Pitch Recognition)
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

import os
import subprocess
from pathlib import Path

# Configurações de Diretório (Ajuste para a pasta onde salvou os CSVs de áudio)
DATASET_DIR = Path("/home/guilherme/AUDIO_DATASET/Datas/dataset_csv")
OUTPUT_BIN_DIR = Path("./src/dataset_audio_error_rate_1e-1")
LOG_DIR = Path("./src/logs_audio")

def run_conversion():
    # Garante que os diretórios de saída existam
    OUTPUT_BIN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list(DATASET_DIR.rglob("*.csv"))
    
    if not csv_files:
        print(f"Nenhum arquivo .csv encontrado em {DATASET_DIR}")
        return

    print(f"Encontrados {len(csv_files)} arquivos para processar.")

    for input_csv in csv_files:
        # 1. Calcula o caminho relativo para manter a hierarquia de pastas
        relative_path = input_csv.relative_to(DATASET_DIR)
        
        # 2. Define os destinos: agora a saída é .bin (contendo o float da frequência)
        output_bin = OUTPUT_BIN_DIR / relative_path.with_suffix(".bin")
        output_log = LOG_DIR / relative_path.with_suffix(".log")

        # 3. Cria as subpastas necessárias
        output_bin.parent.mkdir(parents=True, exist_ok=True)
        output_log.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processando: {relative_path}")
        print(f"  -> Binário: {output_bin.relative_to(OUTPUT_BIN_DIR)}")
        print(f"  -> Log:     {output_log.relative_to(LOG_DIR)}")

        # Comando do AxPike ajustado para rodar o fft_app
        cmd = [
              "axpike",
              "--adele=mem_read_prob:1e-1,linesz:32",
              "--adele-activate=0:AXRAM",
              "--dc=128:8:32",
              "--ic=256:4:32",
              "--l2=1024:4:32",
              "pk",
              "./src/fft_app" # Seu binário compilado em C++
        ]

        try:
            # Redirecionamento triplo:
            # stdin  <- CSV do áudio
            # stdout -> Arquivo .bin (12 bytes: int32 num_samples, int32 num_frames, float32 freq_hz)
            # stderr -> Arquivo .log (Estatísticas do AxPike)
            with open(input_csv, "r") as f_in, \
                 open(output_bin, "wb") as f_out, \
                 open(output_log, "w") as f_log:
                
                # Removido o text=True para garantir que o stdout grave os 4 bytes brutos perfeitamente
                result = subprocess.run(
                    cmd, 
                    stdin=f_in, 
                    stdout=f_out, 
                    stderr=f_log
                )
            
            if result.returncode != 0:
                pass # Erros do simulador já estarão no .log
                
        except Exception as e:
            print(f"  [!] Falha crítica no arquivo {input_csv.name}: {e}")

    print(f"\nConcluído!")
    print(f"Frequências salvas em: {OUTPUT_BIN_DIR}")
    print(f"Logs salvos em:        {LOG_DIR}")

if __name__ == "__main__":
    run_conversion()