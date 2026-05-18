import os
import torch
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.models import resnet50, ResNet50_Weights
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from PIL import Image, ImageFile
import csv

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ──────────────────────────────────────────────
# Detecção de arquivos corrompidos pelo AxPike
# Mesmo critério do analytic_segfault.py
# ──────────────────────────────────────────────
def is_invalid(path):
    try:
        if os.path.getsize(path) == 0:
            return True
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        content_lower = content.lower()
        return "segfault" in content_lower and "pc" in content_lower and "va/inst" in content_lower
    except OSError:
        return False

# ──────────────────────────────────────────────
# Dataset robusto
# ──────────────────────────────────────────────
class RobustImageFolder(torchvision.datasets.ImageFolder):
    def __getitem__(self, index):
        path, label = self.samples[index]
        if is_invalid(path):
            return None
        try:
            img = Image.open(path).convert("RGB")
        except (OSError, SyntaxError, Image.UnidentifiedImageError):
            return None
        if self.transform:
            img = self.transform(img)
        return img, label

def safe_collate(batch):
    batch = [b for b in batch if b is not None]
    if not batch:
        return torch.Tensor(), torch.Tensor()
    return torch.utils.data.dataloader.default_collate(batch)

# ──────────────────────────────────────────────
# Contagem antecipada de inválidos (roda uma vez)
# Separa segfault/vazio do que o PIL rejeitou
# ──────────────────────────────────────────────
def count_invalid(dataset):
    segfault_count = 0
    pil_count      = 0
    for path, _ in dataset.samples:
        if is_invalid(path):
            segfault_count += 1
            continue
        try:
            with Image.open(path) as img:
                img.convert("RGB")
        except (OSError, SyntaxError, Image.UnidentifiedImageError):
            pil_count += 1
    return segfault_count, pil_count

# ──────────────────────────────────────────────
# Configurações
# ──────────────────────────────────────────────
device        = torch.device("cuda" if torch.cuda.is_available() else "cpu")
batch_size    = 64
epochs        = 50

# ──────────────────────────────────────────────
# Transformações (Ajustadas)
# ──────────────────────────────────────────────
train_transforms = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

test_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ──────────────────────────────────────────────
# Dataset e DataLoader
# ──────────────────────────────────────────────
train_dataset = RobustImageFolder(root="/home/aGuilhermeSerbai/AxAccept-Bench/DataSets/dataset_error_rate_1e-4/src/dataset_error_rate_1e-4/train",transform=train_transforms)
test_dataset = RobustImageFolder(root="/home/aGuilhermeSerbai/AxAccept-Bench/DataSets/dataset_error_rate_1e-4/src/dataset_error_rate_1e-4/test",transform=test_transforms)

# Contagem antecipada — roda uma vez antes do treino
print("Verificando integridade do dataset...")
train_segfault, train_pil = count_invalid(train_dataset)
test_segfault,  test_pil  = count_invalid(test_dataset)

total_segfault = train_segfault + test_segfault
total_pil      = train_pil      + test_pil
total_invalid  = total_segfault + total_pil

print(f"  Segfault/vazio treino : {train_segfault}  |  PIL rejeitou: {train_pil}")
print(f"  Segfault/vazio teste  : {test_segfault}  |  PIL rejeitou: {test_pil}")
print(f"  Total segfault/vazio  : {total_segfault}")
print(f"  Total PIL rejeitado   : {total_pil}")
print(f"  Total descartado      : {total_invalid}")
print()

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,  collate_fn=safe_collate)
test_loader  = DataLoader(test_dataset,  batch_size=batch_size, shuffle=False, collate_fn=safe_collate)

# ──────────────────────────────────────────────
# Modelo
# ──────────────────────────────────────────────
model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(model.fc.in_features, 10)
model = model.to(device)

criterion = nn.CrossEntropyLoss()

# ──────────────────────────────────────────────
# Otimizador e Scheduler (Ajustados para SGD)
# ──────────────────────────────────────────────
optimizer = optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=5e-4)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=15, gamma=0.1)

# ──────────────────────────────────────────────
# Treinamento
# ──────────────────────────────────────────────
def train(model, dataloader, optimizer, criterion):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for inputs, labels in tqdm(dataloader):
        if inputs.numel() == 0:
            continue
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    accuracy = 100. * correct / total
    return running_loss / len(dataloader), accuracy

# ──────────────────────────────────────────────
# Validação
# ──────────────────────────────────────────────
def validate(model, dataloader, criterion):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in tqdm(dataloader):
            if inputs.numel() == 0:
                continue
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    accuracy = 100. * correct / total
    return running_loss / len(dataloader), accuracy

# ──────────────────────────────────────────────
# Loop principal
# ──────────────────────────────────────────────
best_val_acc   = 0.0
best_model_wts = model.state_dict()

# Cria cabeçalho só se o arquivo não existir
write_header = not os.path.exists('log_1e-4.csv')
with open('log_1e-4.csv', 'a', newline='') as f:
    if write_header:
        csv.writer(f).writerow(['epoch', 'train_loss', 'train_acc', 'val_loss', 'val_acc','discarded_total', 'discarded_segfault/0B', 'discarded_pil', 'is_best'])

for epoch in range(epochs):
    train_loss, train_acc = train(model, train_loader, optimizer, criterion)
    val_loss, val_acc     = validate(model, test_loader, criterion)
    scheduler.step()

    is_best = val_acc > best_val_acc
    if is_best:
        best_val_acc   = val_acc
        best_model_wts = model.state_dict()
        torch.save(model, "R50_model_error_rate_1e-4.pth")
        print(f"  ✓ Melhor modelo salvo — Epoch {epoch+1} | Val Acc: {val_acc:.2f}%")

    print(f"Epoch [{epoch+1}/{epochs}] "
          f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
          f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")

    with open('log_1e-4.csv', 'a', newline='') as f:
        csv.writer(f).writerow([epoch + 1, train_loss, train_acc, val_loss, val_acc,total_invalid, total_segfault, total_pil,int(is_best)])
