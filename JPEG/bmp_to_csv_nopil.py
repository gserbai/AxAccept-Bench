#!/usr/bin/env python3
"""
Conversor BMP (sem Pillow) -> CSV para o encoder JPEG
Suporta BMP 24-bit, sem compressão (BI_RGB).
Uso: python3 bmp_to_csv_nopil.py input.bmp [output.csv]
Se output.csv não for informado, escreve em stdout.
"""

import sys
import struct


def read_u16(b, off):
    return struct.unpack_from('<H', b, off)[0]

def read_u32(b, off):
    return struct.unpack_from('<I', b, off)[0]


def convert_bmp_to_csv(in_path, out_path=None):
    try:
        with open(in_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Erro ao abrir '{in_path}': {e}", file=sys.stderr)
        return False

    if len(data) < 54:
        print("Arquivo BMP muito pequeno ou inválido", file=sys.stderr)
        return False

    # BITMAPFILEHEADER
    if data[0:2] != b'BM':
        print("Não é BMP (assinatura BM faltando)", file=sys.stderr)
        return False

    file_size = read_u32(data, 2)
    pixel_offset = read_u32(data, 10)

    # BITMAPINFOHEADER (assumimos tamanho 40)
    dib_header_size = read_u32(data, 14)
    if dib_header_size < 40:
        print("Formato BMP não suportado (DIB header < 40)", file=sys.stderr)
        return False

    width = struct.unpack_from('<i', data, 18)[0]
    height = struct.unpack_from('<i', data, 22)[0]
    planes = read_u16(data, 26)
    bpp = read_u16(data, 28)
    compression = read_u32(data, 30)

    if compression != 0:
        print("BMP comprimido não suportado", file=sys.stderr)
        return False

    # Handle 24-bit RGB or 8-bit paletted grayscale/color
    if bpp not in (24, 8):
        print(f"Somente BMP 24-bit ou 8-bit suportado (encontrado {bpp} bits por pixel)", file=sys.stderr)
        return False

    abs_height = abs(height)

    # cada linha tem padding para múltiplo de 4 bytes
    bytes_per_pixel = 3 if bpp == 24 else 1
    row_bytes = (width * bytes_per_pixel)
    padding = (4 - (row_bytes % 4)) % 4

    # onde começa os pixels
    if pixel_offset >= len(data):
        print("Offset de pixel inválido", file=sys.stderr)
        return False

    out = open(out_path, 'w') if out_path else sys.stdout

    # escrever dimensões
    out.write(f"{width},{abs_height}\n")

    # BMP armazena pixels de baixo para cima se height > 0
    bottom_up = height > 0

    # If 8-bit, read palette (color table) between headers and pixel data
    palette = None
    if bpp == 8:
        # Palette starts immediately after DIB header (offset 14 + dib_header_size)
        palette_start = 14 + dib_header_size
        # Number of palette colors: computed from available bytes until pixel_offset
        palette_bytes = pixel_offset - palette_start
        num_colors = palette_bytes // 4
        if num_colors <= 0:
            num_colors = 256
        palette = []
        for i in range(num_colors):
            off = palette_start + i * 4
            if off + 3 >= len(data):
                break
            b = data[off]
            g = data[off + 1]
            r = data[off + 2]
            palette.append((r, g, b))

    for row in range(abs_height):
        y = (abs_height - 1 - row) if bottom_up else row
        row_start = pixel_offset + (y * (row_bytes + padding))
        vals = []
        for x in range(width):
            off = row_start + x * (3 if bpp == 24 else 1)
            if off >= len(data):
                print("Dados do pixel truncados", file=sys.stderr)
                if out_path:
                    out.close()
                return False
            if bpp == 24:
                b = data[off]
                g = data[off + 1]
                r = data[off + 2]
            else:
                idx = data[off]
                if idx >= len(palette):
                    # if palette incomplete, map grayscale via index
                    r = g = b = idx
                else:
                    r, g, b = palette[idx]
            vals.append(f"{r},{g},{b}")
        out.write(','.join(vals) + '\n')

    out.write("BMP\n")

    if out_path:
        out.close()
        print(f"Convertido: {in_path} -> {out_path}", file=sys.stderr)
    else:
        # se stdout, flush
        sys.stdout.flush()

    return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 bmp_to_csv_nopil.py input.bmp [output.csv]", file=sys.stderr)
        sys.exit(1)

    inp = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else None
    ok = convert_bmp_to_csv(inp, outp)
    sys.exit(0 if ok else 2)

if __name__ == '__main__':
    main()
