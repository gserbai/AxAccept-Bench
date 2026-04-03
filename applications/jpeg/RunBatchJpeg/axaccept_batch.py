######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

import os
import subprocess
from pathlib import Path

# Directory configurations
DATASET_DIR = Path("./src/dataset_csv")
OUTPUT_JPEG_DIR = Path("./src/dataset_error_rate_1e-4")
LOG_DIR = Path("./src/logs")

def run_conversion():
    # Ensure output directories exist
    OUTPUT_JPEG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list(DATASET_DIR.rglob("*.csv"))
    
    if not csv_files:
        print(f"No .csv files found in {DATASET_DIR}")
        return

    print(f"Found {len(csv_files)} files to process.")

    for input_csv in csv_files:
        # 1. Calculate relative path (e.g., test/monkey/img_05638.csv)
        relative_path = input_csv.relative_to(DATASET_DIR)
        
        # 2. Define image and log destinations maintaining hierarchy
        output_jpeg = OUTPUT_JPEG_DIR / relative_path.with_suffix(".jpeg")
        output_log = LOG_DIR / relative_path.with_suffix(".log")

        # 3. Create necessary subfolders in both destinations
        output_jpeg.parent.mkdir(parents=True, exist_ok=True)
        output_log.parent.mkdir(parents=True, exist_ok=True)

        print(f"processing: {relative_path}")
        print(f"  -> Image: {output_jpeg.relative_to(OUTPUT_JPEG_DIR)}")
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
            # Triple redirection:
            # stdin  <- original CSV file
            # stdout -> JPEG file (encoded image)
            # stderr -> LOG file (AxPike statistics)
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
                # The log already contains the error/warning details
                pass 
                
        except Exception as e:
            print(f"  [!] Critical file failure {input_csv.name}: {e}")

    print(f"\nCompleted!")
    print(f"Images in: {OUTPUT_JPEG_DIR}")
    print(f"Logs in:    {LOG_DIR}")

if __name__ == "__main__":
    run_conversion()