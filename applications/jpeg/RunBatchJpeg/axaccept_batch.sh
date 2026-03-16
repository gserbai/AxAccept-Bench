######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################


#!/bin/bash

DATASET_DIR="./src/dataset_csv"
OUTPUT_JPEG_DIR="./src/dataset_error_rate_1e-1"

# 1. Busca todos os arquivos .csv, inclusive dentro de subpastas
find "$DATASET_DIR" -type f -name "*.csv" | while read -r input_csv; do

    # 2. Descobre qual é a subpasta para espelhar a estrutura
    # Remove a parte "./dataset/" do caminho
    caminho_relativo="${input_csv#$DATASET_DIR/}"
    # Pega apenas o nome da subpasta (ex: pasta1/subpasta2)
    subpasta=$(dirname "$caminho_relativo")
    # Pega o nome do arquivo (ex: imagem)
    nome_base=$(basename "$caminho_relativo" .csv)

    # 3. Cria a mesma estrutura de subpastas dentro do diretório de saída
    mkdir -p "$OUTPUT_JPEG_DIR/$subpasta"

    # Define o caminho final do JPEG
    output_jpeg="$OUTPUT_JPEG_DIR/$subpasta/${nome_base}.jpeg"

    echo "Processando: $caminho_relativo -> $output_jpeg"

    # 4. Executa o simulador
    # A imagem (stdout) vai para a pasta espelhada.
    # Os logs gerados na execução ficarão no diretório atual de onde você chamou o .sh
    axpike --adele=mem_read_prob:1e-1,linesz:32 \
           --adele-activate=0:AXRAM \
           --dc=128:8:32 \
           --ic=256:4:32 \
           --l2=1024:4:32 \
           pk ./applications/jpeg/src/toojpeg_encoder 100 < "$input_csv" > "$output_jpeg"

done

echo "Concluído! Estrutura de pastas mantida em $OUTPUT_JPEG_DIR."
