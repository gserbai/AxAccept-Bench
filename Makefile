4. Adicione uma imagem:

Coloque qualquer imagem (PNG, BMP, JPG) na pasta e renomeie-a para entrada.png (ou altere o nome no código).

Como Compilar e Executar

Abra o seu terminal na pasta do projeto e execute os seguintes comandos:

    Compilar:
    Bash

gcc compressor_completo.c -o compressor -lm

(A flag -lm é adicionada por precaução, pois algumas operações de imagem podem precisar da biblioteca matemática).

Executar:
Bash

    ./compressor

O que vai acontecer:
O programa irá carregar o arquivo entrada.png, comprimi-lo com qualidade 80 e salvar o resultado como saida.jpg na mesma pasta. Agora você tem um conversor JPEG completo e funcional em um único arquivo!



#riscv64-unknown-elf-gcc compressor_completo.c -o compressor_riscv -static -lm#