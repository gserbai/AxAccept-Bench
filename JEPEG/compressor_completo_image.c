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
 * Projeto: AxAccept-Bench (Versão stdin/stdout)
 * Autor: Guilherme Saides Serbai
 * Ano: 2025
 * Email: guilhermeserbai6@gmail.com
 */

#include <stdio.h>
#include <stdlib.h>

// --- A MÁGICA DO STB ---
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"


// --- FUNÇÕES DE CALLBACK PARA I/O ---

// 1. Callback de escrita: STB chama esta função para escrever o JPEG
void write_to_stdout_func(void *context, void *data, int size) {
    (void)context; 
    fwrite(data, 1, size, stdout);
}

// 2. Callbacks de leitura: STB chama estas para ler o PNG/JPG do stdin
int read_from_stdin(void *user, char *data, int size) {
    (void)user; 
    return fread(data, 1, size, stdin);
}

void skip_stdin(void *user, int n) {
    (void)user;
    fseek(stdin, n, SEEK_CUR);
}

int eof_stdin(void *user) {
    (void)user;
    return feof(stdin);
}
// --------------------


int main(int argc, char *argv[]) {
    // --- PARÂMETROS DE CONFIGURAÇÃO ---
    if (argc != 2) {
        fprintf(stderr, "Erro: Número incorreto de argumentos.\n");
        fprintf(stderr, "Uso: %s <qualidade_1_a_100>\n", argv[0]);
        return 1;
    }
    int quality = atoi(argv[1]); 
    if (quality < 1 || quality > 100) {
        fprintf(stderr, "Erro: O parâmetro de qualidade deve ser um número entre 1 e 100.\n");
        fprintf(stderr, "Uso: %s <qualidade_1_a_100>\n", argv[0]);
        return 1;
    }
    // -------------------------------------------------------------

    int width, height, original_channels;

    // Define a struct de callbacks para leitura
    stbi_io_callbacks callbacks;
    callbacks.read = read_from_stdin;
    callbacks.skip = skip_stdin;
    callbacks.eof  = eof_stdin;

    fprintf(stderr, "Passo 1: Carregando a imagem do STDIN...\n");

    // --- PASSO 1: LER A IMAGEM DO STDIN ---
    //
    // Usa stbi_load_from_callbacks para ler do stdin sem
    // carregar o arquivo inteiro na memória de uma vez.
    //
    unsigned char *pixels = stbi_load_from_callbacks(
        &callbacks, 
        NULL, 
        &width, 
        &height, 
        &original_channels, 
        0
    );

    if (pixels == NULL) {
        fprintf(stderr, "Erro: Não foi possível carregar a imagem do STDIN.\n");
        return 1;
    }

    fprintf(stderr, "Imagem carregada! Dimensões: %d x %d, Canais: %d\n", width, height, original_channels);
    fprintf(stderr, "\nPasso 2: Comprimindo para JPEG com qualidade %d (para STDOUT)...\n", quality);

    // --- PASSO 2: APLICAR O JPEG E "SALVAR" PARA STDOUT ---
    int success = stbi_write_jpg_to_func(
        write_to_stdout_func, 
        NULL,                       
        width, 
        height, 
        original_channels, 
        pixels, 
        quality
    );

    if (!success) {
        fprintf(stderr, "Erro ao comprimir a imagem JPEG.\n");
        stbi_image_free(pixels);
        return 1;
    }
    
    fprintf(stderr, "Compressão para STDOUT concluída com sucesso!\n");

    // --- PASSO 3: LIMPEZA ---
    stbi_image_free(pixels);
    fprintf(stderr, "\nProcesso concluído.\n");

    return 0;
}