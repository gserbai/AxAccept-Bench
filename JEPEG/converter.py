import sys
import os

if len(sys.argv) != 4:
    print(f"Uso: python3 {sys.argv[0]} <nome_do_array> <ficheiro_de_entrada> <ficheiro_de_saida>")
    sys.exit(1)

array_name = sys.argv[1]
input_file = sys.argv[2]
output_file = sys.argv[3]

try:
    with open(input_file, 'rb') as f_in:
        data = f_in.read()
    
    with open(output_file, 'w') as f_out:
        # Escreve o início do array C
        f_out.write(f"/* Ficheiro gerado automaticamente por converter.py */\n")
        f_out.write(f"unsigned char {array_name}[] = {{\n  ")
        
        # Escreve os bytes em formato hexadecimal
        for i, byte in enumerate(data):
            f_out.write(f"0x{byte:02x}, ")
            # Quebra a linha a cada 12 bytes para ficar legível
            if (i + 1) % 12 == 0:
                f_out.write("\n  ")
        
        # Fecha o array e escreve o tamanho
        f_out.write("\n};\n")
        f_out.write(f"unsigned int {array_name}_len = {len(data)};\n")
    
    print(f"Convertido '{input_file}' ({len(data)} bytes) para '{output_file}' com sucesso.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
    sys.exit(1)