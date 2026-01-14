# Converter BMP para CSV para JPEG Encoder

## Requisitos

```bash
pip install Pillow
```

## Como usar

### Opção 1: Converter para arquivo CSV e depois codificar

```bash
# Converter BMP para CSV
python3 bmp_to_csv.py input.bmp output.csv

# Depois passar para o encoder
cat output.csv | axpike pk ./teste 90 1> saida.jpg 2> logs.txt
```

### Opção 2: Pipeline direto (sem arquivo intermediário)

```bash
python3 bmp_to_csv.py input.bmp | axpike pk ./teste 90 1> saida.jpg 2> logs.txt
```

## Formato esperado

O converter transforma um BMP neste formato CSV:

```
<largura>,<altura>
<r>,<g>,<b>,<r>,<g>,<b>,...
<r>,<g>,<b>,<r>,<g>,<b>,...
...
metadata
```

## Exemplo completo

```bash
# Se tiver uma imagem test.bmp
python3 bmp_to_csv.py test.bmp | ./teste 75 1> resultado.jpg 2> debug.txt
```

## Notas

- O encoder JPEG converte para escala de cinza (Y)
- A qualidade aceita valores de 1-100
- A imagem será ajustada para múltiplos de 8 pixels
- Mensagens de debug vão para stderr (FD 2)
- A imagem comprimida vai para stdout (FD 1)
