######################################################################
# AxAccept-Bench
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

"""
Uso:
    # Se o dataset estiver em outro lugar:
    python split_ucmerced.py --src /caminho/completo/para/UCMerced_LandUse/Images

    # Se quiser que a pasta de saida tenha outro nome:
    python split_ucmerced.py --src /caminho/para/Images --out /caminho/para/saida
"""

import json
import shutil
import random
import argparse
from pathlib import Path

# Configuracoes
SEED    = 42
TRAIN_N = 80
TEST_N  = 20

# Nome do arquivo de manifesto gerado na pasta de saida
MANIFEST_FILE = "split_manifest.json"


def split_dataset(src_dir: Path, out_dir: Path):
    random.seed(SEED)

    train_dir = out_dir / "train"
    test_dir  = out_dir / "test"

    classes = sorted([d for d in src_dir.iterdir() if d.is_dir()], key=lambda x: x.name)
    if not classes:
        raise ValueError(f"Nenhuma subpasta encontrada em: {src_dir}")

    print(f"\n{'Classe':<25} {'Train':>6} {'Test':>6}")
    print("-" * 40)

    # Manifesto: registra exatamente quais arquivos foram para cada split
    manifest = {
        "seed": SEED,
        "train_n": TRAIN_N,
        "test_n": TEST_N,
        "splits": {}
    }

    for cls_dir in classes:
        label = cls_dir.name

        # key=lambda garante ordem deterministica independente do filesystem
        images = sorted([
            f for f in cls_dir.iterdir()
            if f.suffix.lower() in {".tif", ".tiff", ".jpg", ".jpeg", ".png"}
        ], key=lambda x: x.name)

        if len(images) < TRAIN_N + TEST_N:
            print(f"  AVISO: {label} tem so {len(images)} imagens, pulando...")
            continue

        random.shuffle(images)
        train_imgs = images[:TRAIN_N]
        test_imgs  = images[TRAIN_N:TRAIN_N + TEST_N]

        # Salva no manifesto (só o nome do arquivo, sem path absoluto)
        manifest["splits"][label] = {
            "train": [f.name for f in train_imgs],
            "test":  [f.name for f in test_imgs]
        }

        for imgs, split_dir in [(train_imgs, train_dir), (test_imgs, test_dir)]:
            dest_cls = split_dir / label
            dest_cls.mkdir(parents=True, exist_ok=True)
            for img in imgs:
                shutil.copy2(img, dest_cls / img.name)

        print(f"  {label:<23} {len(train_imgs):>6} {len(test_imgs):>6}")

    # Grava o manifesto na pasta de saida
    manifest_path = out_dir / MANIFEST_FILE
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nSplit concluido!")
    print(f"  Train    -> {train_dir}")
    print(f"  Test     -> {test_dir}")
    print(f"  Manifesto-> {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split UC Merced 80/20 por classe")
    parser.add_argument(
        "--src",
        type=Path,
        default=Path("UCMerced_LandUse/Images"),
        help="Caminho para a pasta Images do dataset (default: UCMerced_LandUse/Images)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("dataset"),
        help="Pasta de saida (default: dataset/)"
    )
    args = parser.parse_args()

    if not args.src.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {args.src}")

    split_dataset(args.src, args.out)
