######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

#!/bin/bash

DATASET_DIR="./src/dataset_csv"
OUTPUT_JPEG_DIR="./src/dataset_error_rate_1e-1"

# 1. Find all .csv files, including those in subfolders
find "$DATASET_DIR" -type f -name "*.csv" | while read -r input_csv; do

    # 2. Figure out the subfolder to mirror the structure
    # Remove the "./dataset_csv/" part from the path
    relative_path="${input_csv#$DATASET_DIR/}"
    # Get only the subfolder name (e.g., folder1/subfolder2)
    subfolder=$(dirname "$relative_path")
    # Get the file name (e.g., image)
    base_name=$(basename "$relative_path" .csv)

    # 3. Create the same subfolder structure inside the output directory
    mkdir -p "$OUTPUT_JPEG_DIR/$subfolder"

    # Define the final JPEG path
    output_jpeg="$OUTPUT_JPEG_DIR/$subfolder/${base_name}.jpeg"

    echo "Processing: $relative_path -> $output_jpeg"

    # 4. Run the simulator
    # The image (stdout) goes to the mirrored folder.
    # The logs generated during execution will stay in the current directory where you called the .sh from
    axpike --adele=mem_read_prob:1e-1,linesz:32 \
           --adele-activate=0:AXRAM \
           --dc=128:8:32 \
           --ic=256:4:32 \
           --l2=1024:4:32 \
           pk ./applications/jpeg/src/toojpeg_encoder 100 < "$input_csv" > "$output_jpeg"

done

echo "Completed! Folder structure maintained in $OUTPUT_JPEG_DIR."