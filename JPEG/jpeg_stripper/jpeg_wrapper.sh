#!/bin/bash
# Wrapper para gerar JPEG e limpar automaticamente

ENCODER="/home/guilherme/AxAccept-Bench/JPEG/jpeg_encoder"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 2 ]; then
    echo "Uso: $0 <entrada.csv> <saida.jpg> [qualidade] [modo]"
    echo "  entrada.csv: Arquivo CSV de entrada"
    echo "  saida.jpg: Arquivo JPEG de saída (será limpo automaticamente)"
    echo "  qualidade: Fator de qualidade 1-100 (padrão: 90)"
    echo "  modo: 'gray' ou 'rgb' (padrão: gray)"
    echo ""
    echo "Exemplos:"
    echo "  $0 input.csv output.jpg 90 gray"
    echo "  $0 input.csv output.jpg 85 rgb"
    exit 1
fi

INPUT="$1"
OUTPUT="$2"
QUALITY="${3:-90}"
MODE="${4:-gray}"

if [ ! -f "$INPUT" ]; then
    echo "❌ Erro: Arquivo $INPUT não encontrado"
    exit 1
fi

if [ ! -f "$ENCODER" ]; then
    echo "❌ Erro: Encoder não encontrado em $ENCODER"
    exit 1
fi

echo "═══════════════════════════════════════════════"
echo "Gerando JPEG..."
echo "═══════════════════════════════════════════════"
echo "Entrada:   $INPUT"
echo "Saída:     $OUTPUT"
echo "Qualidade: $QUALITY"
echo "Modo:      $MODE"
echo ""

# Gera JPEG (pode ter lixo)
TEMP_FILE=$(mktemp)
cat "$INPUT" | axpike pk "$ENCODER" "$QUALITY" "$MODE" 2>/dev/null > "$TEMP_FILE"

# Limpa (remove "bbl loader" e outros logs)
python3 << EOF
import sys

with open('$TEMP_FILE', 'rb') as f:
    data = f.read()

# Procura por FFD8 (SOI - Start of Image)
idx = data.find(b'\xff\xd8')

if idx == -1:
    print("❌ Erro: Marcador JPEG FFD8 não encontrado", file=sys.stderr)
    sys.exit(1)

# Extrai JPEG válido
jpeg_data = data[idx:]

with open('$OUTPUT', 'wb') as f:
    f.write(jpeg_data)

print(f"✅ Tamanho total:   {len(data):,} bytes")
print(f"✅ Lixo removido:   {idx} bytes")
print(f"✅ JPEG final:      {len(jpeg_data):,} bytes")
print(f"✅ Arquivo salvo:   $OUTPUT")
EOF

# Valida
echo ""
file "$OUTPUT"

# Limpa arquivo temporário
rm -f "$TEMP_FILE"

echo "═══════════════════════════════════════════════"
echo "✅ Concluído!"
echo "═══════════════════════════════════════════════"
