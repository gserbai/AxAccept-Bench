# 📘 Guia Mestre: JPEG Encoder (RISC-V/AxAccept-Bench)

Este guia unifica os comandos de compilação, execução, limpeza de logs e testes de RGB.

## 1. 🛠️ Compilação (Necessário antes de tudo)

Antes de rodar, você precisa compilar o código fonte C para RISC-V.

```bash
cd src
riscv64-unknown-elf-gcc -static -o ../jpeg_encoder *.c -lm
cd ..

```

*Isso gera o binário `jpeg_encoder` na raiz da pasta JPEG.*

---

## 2. ⭐ Execução Automática (Recomendado)

Usa o script `jpeg_wrapper.sh`. Ele faz tudo: executa o encoder, remove o lixo (logs do BBL) e gera o JPEG final limpo.

**Sintaxe:**

```bash
./jpeg_wrapper.sh <entrada.csv> <saida.jpg> [qualidade] [modo]

```

**Exemplos de uso:**

```bash
# Modo Grayscale (Padrão: qualidade 90)
./jpeg_wrapper.sh image.csv saida_gray.jpg 90 gray

# Modo RGB (Qualidade 85)
./jpeg_wrapper.sh image.csv saida_rgb.jpg 85 rgb

```

---

## 3. ⚙️ Execução Manual (Passo a Passo)

Útil se você precisa debugar ou não quer usar o wrapper. O processo é dividido em **Gerar** e **Limpar**.

### Passo A: Gerar o JPEG (Sujo)

O `axpike` mistura logs (texto) com a imagem (binário).

```bash
# Sintaxe: cat CSV | axpike pk ./binario QUALIDADE MODO > SAIDA
cat image.csv | axpike pk ./jpeg_encoder 90 rgb > saida_suja.jpg

```

*Nota: Você pode usar `2>/dev/null` para ignorar erros, mas o arquivo de saída ainda pode conter o cabeçalho do BBL.*

### Passo B: Limpar o JPEG

Remove o texto "bbl loader" e outros lixos antes do marcador `FFD8` do JPEG.

```bash
./clean_jpeg.sh saida_suja.jpg saida_final.jpg

```

---

## 4. 🧪 Ferramentas Úteis & Testes

### Converter BMP para CSV

O encoder não lê BMP direto, precisa converter para CSV (texto) primeiro.

```bash
python3 bmp_to_csv_nopil.py imagem.bmp > image.csv

```

### Testar Comparação (Gray vs RGB)

Roda os dois modos e compara os tamanhos dos arquivos gerados.

```bash
./test_rgb.sh

```

*Expectativa: O arquivo RGB deve ser ~10-15% maior que o Grayscale devido aos componentes de cor (Cb/Cr com downsampling 4:2:0).*

---

## 5. 📝 Resumo Técnico dos Parâmetros

| Parâmetro | Valores | Descrição |
| --- | --- | --- |
| **Qualidade** | `1` a `100` | Define a quantização. `1` = Pior qualidade/Menor tamanho. `100` = Melhor qualidade. |
| **Modo** | `gray` | Converte para escala de cinza (apenas componente Y). |
| **Modo** | `rgb` | Mantém cores. Usa YCbCr com downsampling 4:2:0 (1 Y + ¼ Cb + ¼ Cr). |

### Estrutura de Diretórios Esperada

* `src/`: Códigos `.c` (encoder, huffman, rgbimage).
* `jpeg_wrapper.sh`: Script principal.
* `clean_jpeg.sh`: Script de limpeza (remove logs BBL).
* `jpeg_encoder`: Binário compilado (RISC-V).

---

### 💡 Dica Rápida

Se der erro de permissão em qualquer script:

```bash
chmod +x *.sh

```