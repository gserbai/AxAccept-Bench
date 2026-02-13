#!/bin/bash
# Script para limpar arquivo JPEG removendo lixo inicial

if [ $# -ne 2 ]; then
    echo "Uso: $0 <arquivo_sujo.jpg> <arquivo_limpo.jpg>"
    exit 1
fi

INPUT="$1"
OUTPUT="$2"

if [ ! -f "$INPUT" ]; then
    echo "❌ Erro: Arquivo $INPUT não encontrado"
    exit 1
fi

python3 << EOF
import sys

with open('$INPUT', 'rb') as f:
    data = f.read()
    
# Procura por FFD8 (SOI - Start of Image)
idx = data.find(b'\xff\xd8')

if idx == -1:
    print("❌ Erro: Marcador JPEG FFD8 não encontrado")
    sys.exit(1)

print(f"✅ Marcador FFD8 encontrado no offset: {idx}")

# Extrai a partir de FFD8
jpeg_data = data[idx:]
print(f"✅ Tamanho original: {len(data)} bytes")
print(f"✅ Tamanho limpo: {len(jpeg_data)} bytes")
print(f"✅ Removido: {idx} bytes")

# Salva
with open('$OUTPUT', 'wb') as f:
    f.write(jpeg_data)
    
print(f"✅ Arquivo salvo: $OUTPUT")
EOF

# Verifica se o arquivo é JPEG válido
file "$OUTPUT"
