import os
import re
import io
import torch
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from PIL import Image, ImageFile
from tqdm import tqdm

ImageFile.LOAD_TRUNCATED_IMAGES = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# =====================================================
# CONFIGURA MANUALMENTE AQUI
# =====================================================
MODEL_PATH = "/home/guilherme/Pictures/R50_model_non-approx.pth"

DATASET_PATH = "/home/guilherme/Pictures/Datas/non-approx/test"
# ex:
# "/home/guilherme/Pictures/Datas/dataset_error_rate_1e-1/test"


def to_rgb(x):
    return x.convert("RGB")


# =====================================================
# BLOCK 1 — JPEG RESCUE
# =====================================================
PAYLOAD_MINIMO = 1024
MARCADORES_VALIDOS = [b'\xff\xe0', b'\xff\xe1', b'\xff\xdb']
PADRAO_CRASH = re.compile(
    br'z\s+[0-9a-fA-F]{16}\s+ra\s+[0-9a-fA-F]{16}'
)


def resgatar_jpeg_antes_do_crash(caminho_arquivo):

    try:
        if os.path.getsize(caminho_arquivo) == 0:
            return None, "empty"

        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        match_crash = PADRAO_CRASH.search(conteudo)

        if match_crash:
            dados_validos = conteudo[:match_crash.start()]
            teve_crash = True
        else:
            dados_validos = conteudo
            teve_crash = False

        inicio_jpeg = dados_validos.find(b'\xff\xd8')

        if inicio_jpeg == -1:
            return None, "no_ffd8"

        payload = len(dados_validos) - inicio_jpeg - 2

        if payload < PAYLOAD_MINIMO:
            return None, "corrompida_payload_pequeno"

        janela = dados_validos[
            inicio_jpeg+2:min(inicio_jpeg+22, len(dados_validos))
        ]

        if not any(m in janela for m in MARCADORES_VALIDOS):
            return None, "corrompida_sem_marcador"

        status = "rescued_crash" if teve_crash else "clean"

        return dados_validos[inicio_jpeg:], status

    except OSError:
        return None, "os_error"


# =====================================================
# BLOCK 2 — LOAD IMAGE
# =====================================================
def carregar_imagem_robusta(caminho_arquivo):

    if caminho_arquivo.lower().endswith((".tif", ".tiff")):
        try:
            img = Image.open(caminho_arquivo).convert("RGB")
            return img, "clean"
        except (OSError, SyntaxError, Image.UnidentifiedImageError):
            return None, "pil_rejected"

    bytes_imagem, status = resgatar_jpeg_antes_do_crash(
        caminho_arquivo
    )

    if bytes_imagem is None:
        return None, status

    try:
        img = Image.open(io.BytesIO(bytes_imagem)).convert("RGB")
        return img, status
    except (OSError, SyntaxError, Image.UnidentifiedImageError):
        return None, "pil_rejected"


# =====================================================
# DATASET
# =====================================================
class RobustImageFolder(torchvision.datasets.ImageFolder):

    def __getitem__(self, index):

        path, label = self.samples[index]

        img, _ = carregar_imagem_robusta(path)

        if img is None:
            return None

        if self.transform:
            img = self.transform(img)

        return img, label


def safe_collate(batch):

    batch = [b for b in batch if b is not None]

    if not batch:
        return torch.Tensor(), torch.Tensor()

    return torch.utils.data.dataloader.default_collate(batch)


# =====================================================
# TRANSFORM
# =====================================================
transform_eval = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Lambda(to_rgb),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225]
    )
])


# =====================================================
# MAIN
# =====================================================
print(f"\nDevice: {device}")
print(f"Model : {MODEL_PATH}")
print(f"Data  : {DATASET_PATH}\n")

model = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False
)

model.eval()

dataset = RobustImageFolder(
    root=DATASET_PATH,
    transform=transform_eval
)

loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=False,
    collate_fn=safe_collate
)

classes = dataset.classes

all_preds = []
all_labels = []

with torch.no_grad():

    for inputs, labels in tqdm(loader):

        if inputs.numel() == 0:
            continue

        inputs = inputs.to(device)

        outputs = model(inputs)

        _, predicted = outputs.max(1)

        all_preds.extend(predicted.cpu().tolist())
        all_labels.extend(labels.tolist())


correct = sum(
    p == l for p, l in zip(all_preds, all_labels)
)

acc = 100 * correct / len(all_labels)

print("\n==========================")
print(f"Overall Accuracy: {acc:.2f}%")
print("==========================\n")


for i, classe in enumerate(classes):

    total = 0
    hit = 0

    for p, l in zip(all_preds, all_labels):
        if l == i:
            total += 1
            if p == l:
                hit += 1

    class_acc = 100 * hit / total

    print(f"{classe:20} {class_acc:.2f}%")
