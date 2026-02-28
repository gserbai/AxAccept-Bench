import numpy as np
import os

def convert_stl10_to_csv(bin_X, bin_y, output_root):
    # Nomes das classes oficiais do STL-10
    classes = ['airplane', 'bird', 'car', 'cat', 'deer', 'dog', 'horse', 'monkey', 'ship', 'truck']
    WIDTH, HEIGHT, CHANNELS = 96, 96, 3
    IMG_SIZE = WIDTH * HEIGHT * CHANNELS

    # Carregar labels (y) - são uint8 de 1 a 10
    labels = np.fromfile(bin_y, dtype=np.uint8) - 1 # Ajusta para 0-9
    
    # Abrir arquivo de imagens (X)
    with open(bin_X, 'rb') as f:
        for i, label in enumerate(labels):
            data = f.read(IMG_SIZE)
            if not data: break
            
            # 1. Ler e Intercalar (Column-major para RGB)
            raw_pixels = np.frombuffer(data, dtype=np.uint8)
            # O STL-10 é gravado como: [todos R, todos G, todos B]
            # Reshape e transpose para (Altura, Largura, Canais)
            img = raw_pixels.reshape(3, HEIGHT, WIDTH).transpose(1, 2, 0)
            
            # 2. Criar Pasta da Classe
            class_name = classes[label]
            class_dir = os.path.join(output_root, class_name)
            os.makedirs(class_dir, exist_ok=True)
            
            # 3. Salvar o CSV com o cabeçalho que seu C++ espera
            csv_path = os.path.join(class_dir, f'img_{i:05d}.csv')
            with open(csv_path, 'w') as csv_file:
                padding = " " * 50
                csv_file.write(f"{padding}{WIDTH},{HEIGHT}\n") # Cabeçalho do AxAccept-Bench
                for row in img:
                    # Linha formatada: R,G,B,R,G,B...
                    line = ",".join([f"{p[0]},{p[1]},{p[2]}" for p in row])
                    csv_file.write(line + "\n")
            
            if i % 500 == 0:
                print(f"Processando {output_root}: {i} imagens concluídas...")

# --- EXECUÇÃO NO SEU ARCH ---
# Certifique-se de que os caminhos abaixo apontam para onde você extraiu o dataset
base_path = './stl10_binary'

print("--- Iniciando Conjunto de TREINO ---")
convert_stl10_to_csv(f'{base_path}/train_X.bin', f'{base_path}/train_y.bin', './dataset_csv/train')

print("\n--- Iniciando Conjunto de TESTE ---")
convert_stl10_to_csv(f'{base_path}/test_X.bin', f'{base_path}/test_y.bin', './dataset_csv/test')

print("\nConcluído! Agora você tem pastas por classe com os CSVs de pixels puros.")
