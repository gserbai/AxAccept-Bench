/*
 * Copyright 2025 Guilherme Saides Serbai
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


/*
 * Projeto: AxAccept-Bench
 * Autor: Guilherme Saides Serbai
 * Ano: 2025
 * Email: guilhermeserbai6@gmail.com
 */

#include <stdio.h>
#include <stdlib.h>

// --- A MÁGICA DO STB ---
// Estas duas linhas pedem ao compilador para incluir o código-fonte completo
// das bibliotecas aqui mesmo, tornando nosso programa autocontido.
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
// --------------------


int main(int argc, char *argv[]) {
    // --- PARÂMETROS DE CONFIGURAÇÃO ---
    const char* input_filename = "entrada.png";
    const char* output_filename = "saida.jpg";
    int quality = 80; // Valor padrão da qualidade, caso nenhum seja fornecido

    if (argc > 1) { // Se o usuário forneceu pelo menos um argumento
        // A função atoi() converte uma string (texto) para um inteiro.
        quality = atoi(argv[1]);
        
        // Validação: Garante que a qualidade esteja entre 1 e 100
        if (quality < 1 || quality > 100) {
            fprintf(stderr, "Erro: O parâmetro de qualidade deve ser um número entre 1 e 100.\n");
            fprintf(stderr, "Uso: %s <qualidade>\n", argv[0]);
            return 1;
        }
    } else {
        printf("Nenhum parâmetro de qualidade fornecido. Usando o valor padrão: %d\n", quality);
        printf("Dica: Você pode especificar a qualidade executando: %s <numero_de_1_a_100>\n\n", argv[0]);
    }
    // -------------------------------------------------------------

    int width, height, original_channels;

    printf("Passo 1: Carregando a imagem '%s'...\n", input_filename);

    // --- PASSO 1: LER A IMAGEM DE ENTRADA ---
    unsigned char *pixels = stbi_load(input_filename, &width, &height, &original_channels, 0);

    if (pixels == NULL) {
        fprintf(stderr, "Erro: Não foi possível carregar a imagem. Verifique se o arquivo '%s' existe na pasta.\n", input_filename);
        return 1;
    }

    printf("Imagem carregada com sucesso! Dimensões: %d x %d, Canais: %d\n", width, height, original_channels);
    printf("\nPasso 2: Comprimindo para JPEG com qualidade %d...\n", quality);

    // --- PASSO 2: APLICAR O JPEG E SALVAR O ARQUIVO ---
    int success = stbi_write_jpg(output_filename, width, height, original_channels, pixels, quality);

    if (!success) {
        fprintf(stderr, "Erro ao salvar a imagem JPEG.\n");
        stbi_image_free(pixels);
        return 1;
    }
    
    printf("Imagem salva com sucesso como '%s'!\n", output_filename);

    // --- PASSO 3: LIMPEZA ---
    stbi_image_free(pixels);
    printf("\nProcesso concluído.\n");

    return 0;
}