######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

"""
Lê o split_manifest.json gerado pelo split_ucmerced.py para garantir
que a conversão para CSV use exatamente as mesmas imagens do split,
na mesma ordem, em qualquer máquina.
"""

import json
import numpy as np
import os
from pathlib import Path
from PIL import Image

# Nome do manifesto (deve ser o mesmo definido no split_ucmerced.py)
MANIFEST_FILE = "split_manifest.json"


def convert_image_to_csv(img_path: Path, csv_path: Path):
    """Converte uma imagem TIF para o formato CSV esperado pelo AxPike."""
    try:
        img = Image.open(img_path).convert('RGB')
    except Exception as e:
        print(f"  [ERRO] Nao foi possivel abrir {img_path}: {e}")
        return False

    img_array = np.array(img, dtype=np.uint8)
    height, width = img_array.shape[:2]

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, 'w') as csv_file:
        # Cabeçalho customizado para o AxPike
        padding = " " * 64
        csv_file.write(f"{padding}{width},{height}\n")

        # Achata RGB para a mesma linha: (H, W, 3) -> (H, W*3)
        matriz_plana = img_array.reshape(height, width * 3)
        np.savetxt(csv_file, matriz_plana, fmt='%d', delimiter=',')

    return True


def convert_from_manifest(dataset_dir: Path, output_csv_dir: Path, manifest_path: Path):
    """
    Converte as imagens do split para CSV lendo o manifesto.
    Garante ordem e seleção 100% idênticas ao split original.
    """
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Manifesto nao encontrado: {manifest_path}\n"
            f"Execute split_ucmerced.py primeiro."
        )

    with open(manifest_path) as f:
        manifest = json.load(f)

    total_count = 0

    for split in ["train", "test"]:
        print(f"\n--- Convertendo split: {split} ---")
        split_count = 0

        for label, files in manifest["splits"].items():
            filenames = files[split]

            for fname in filenames:
                # Caminho da imagem original no dataset splitado
                img_path = dataset_dir / split / label / fname

                if not img_path.exists():
                    print(f"  [MISSING] {img_path}")
                    continue

                # Mantém hierarquia: train/harbor/harbor35.csv
                csv_name = Path(fname).stem + ".csv"
                csv_path = output_csv_dir / split / label / csv_name

                if convert_image_to_csv(img_path, csv_path):
                    split_count += 1
                    total_count += 1

            if total_count % 500 == 0 and total_count > 0:
                print(f"  {total_count} imagens convertidas...")

        print(f"  Split '{split}': {split_count} imagens convertidas.")

    return total_count


if __name__ == "__main__":
    # Ajuste os paths conforme necessário
    DATASET_DIR    = Path("./dataset")           # saída do split_ucmerced.py
    OUTPUT_CSV_DIR = Path("./dataset_csv")        # destino dos CSVs
    MANIFEST_PATH  = DATASET_DIR / MANIFEST_FILE  # manifesto gerado pelo split

    print("=" * 50)
    print("  Conversão UC Merced -> CSV (via Manifesto)")
    print("=" * 50)
    print(f"  Dataset   : {DATASET_DIR}")
    print(f"  Manifesto : {MANIFEST_PATH}")
    print(f"  CSV out   : {OUTPUT_CSV_DIR}")
    print("=" * 50)

    total = convert_from_manifest(DATASET_DIR, OUTPUT_CSV_DIR, MANIFEST_PATH)

    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50)
    print(f"  Total convertido : {total} imagens")
    print(f"  CSV em           : {OUTPUT_CSV_DIR}")
    print("=" * 50)
    print("Concluido!")
