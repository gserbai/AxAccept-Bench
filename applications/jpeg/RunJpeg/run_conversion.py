######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################
import os
import subprocess
from pathlib import Path

# Directory configurations
DATASET_DIR    = Path("/home/guilherme/UC_MERCED_LAND_USE/Datas/dataset_csv")
OUTPUT_JPEG_DIR = Path("./src/dataset_error_rate_1e-1")
LOG_DIR         = Path("./src/logs")
MEM_LOG_DIR     = Path("./src/mem_logs")

def run_conversion():
    # Ensure output directories exist
    OUTPUT_JPEG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    MEM_LOG_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list(DATASET_DIR.rglob("*.csv"))
    if not csv_files:
        print(f"No .csv files found in {DATASET_DIR}")
        return

    print(f"Found {len(csv_files)} files to process.")

    for input_csv in csv_files:
        # 1. Relative path mantendo estrutura do dataset (ex: test/monkey/img_05638.csv)
        relative_path = input_csv.relative_to(DATASET_DIR)

        # 2. Destinos mantendo hierarquia igual ao dataset
        output_jpeg = OUTPUT_JPEG_DIR / relative_path.with_suffix(".jpeg")
        output_log  = LOG_DIR         / relative_path.with_suffix(".log")
        output_mem  = MEM_LOG_DIR     / relative_path.with_suffix(".mem")

        # 3. Cria subpastas necessárias em todos os destinos
        output_jpeg.parent.mkdir(parents=True, exist_ok=True)
        output_log.parent.mkdir(parents=True, exist_ok=True)
        output_mem.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processing: {relative_path}")
        print(f"  -> Image  : {output_jpeg.relative_to(OUTPUT_JPEG_DIR)}")
        print(f"  -> Log    : {output_log.relative_to(LOG_DIR)}")
        print(f"  -> MemLog : {output_mem.relative_to(MEM_LOG_DIR)}")

        cmd = [
            "axpike",
            f"--adele=mem_read_prob:1e-1,linesz:32,mem_log:{output_mem}",
            "--adele-activate=0:AXRAM",
            "--dc=128:8:32",
            "--ic=256:4:32",
            "--l2=1024:4:32",
            "pk",
            "/home/guilherme/AxAccept-Bench/applications/jpeg/RunJpeg/src/toojpeg_encoder",
            "100"
        ]

        try:
            with open(input_csv,   "r")  as f_in,  \
                 open(output_jpeg, "wb") as f_out, \
                 open(output_log,  "w")  as f_log:
                subprocess.run(
                    cmd,
                    stdin=f_in,
                    stdout=f_out,
                    stderr=f_log,
                    text=True
                )
        except Exception as e:
            print(f"  [!] Critical failure {input_csv.name}: {e}")

    print(f"\nCompleted!")
    print(f"  Images  : {OUTPUT_JPEG_DIR}")
    print(f"  Logs    : {LOG_DIR}")
    print(f"  MemLogs : {MEM_LOG_DIR}")

if __name__ == "__main__":
    run_conversion()
