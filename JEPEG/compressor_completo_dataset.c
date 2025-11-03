/*
 * Projeto: AxAccept-Bench
 * Autor: Guilherme Saides Serbai
 * Ano: 2025
 * Email: guilhermeserbai6@gmail.com
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h> 
#include <errno.h> 

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Função auxiliar: verifica se um arquivo termina com determinada extensão
int tem_extensao(const char *filename, const char *ext) {
    const char *dot = strrchr(filename, '.');
    if (!dot) return 0;
    return strcasecmp(dot, ext) == 0;
}

int main(int argc, char *argv[]) {
    // 1. Atualiza a checagem de argumentos
    if (argc < 4) { 
        printf("Uso: %s <diretorio_entrada> <diretorio_saida> <qualidade>\n", argv[0]);
        printf("Exemplo: %s imagens imagens_processadas 85\n", argv[0]);
        return 1;
    }

    const char *dir_path_entrada = argv[1];           
    const char *dir_path_saida = argv[2];             
    int quality = atoi(argv[3]);                      

    if (quality < 1 || quality > 100) {
        fprintf(stderr, "Erro: qualidade deve estar entre 1 e 100.\n");
        return 1;
    }

    // 2. Tenta criar o diretório de saída
    if (mkdir(dir_path_saida, 0755) == -1) {
        if (errno != EEXIST) { 
            perror("Erro ao criar diretório de saída");
            return 1;
        }
    }

    DIR *dir = opendir(dir_path_entrada); 
    if (!dir) {
        perror("Erro ao abrir diretório de entrada");
        return 1;
    }

    struct dirent *entry;
    char input_path[512];
    char output_path[512];
    
    struct stat path_stat; 

    while ((entry = readdir(dir)) != NULL) {

        // Monta o caminho de ENTRADA
        snprintf(input_path, sizeof(input_path), "%s/%s", dir_path_entrada, entry->d_name);

        if (stat(input_path, &path_stat) != 0) {
            continue;
        }
        if (S_ISDIR(path_stat.st_mode)) { 
            continue; // Pula se for diretório
        }

        // Verifica se é um arquivo de imagem suportado
        if (!tem_extensao(entry->d_name, ".png") &&
            !tem_extensao(entry->d_name, ".bmp") &&
            !tem_extensao(entry->d_name, ".jpg") &&
            !tem_extensao(entry->d_name, ".jpeg"))
            continue;

        // 3. Monta o caminho de SAÍDA
        snprintf(output_path, sizeof(output_path), "%s/%s", dir_path_saida, entry->d_name);

        // Gera nome de saída substituindo extensão por .jpg
        char *dot = strrchr(output_path, '.');
        if (dot) strcpy(dot, ".jpg");
        else strcat(output_path, ".jpg");

        // Carrega a imagem (do input_path)
        int width, height, channels;
        unsigned char *pixels = stbi_load(input_path, &width, &height, &channels, 0);
        if (!pixels) {
            fprintf(stderr, "Falha ao carregar '%s'\n", input_path);
            continue;
        }

        // Salva como JPEG (no output_path)
        if (!stbi_write_jpg(output_path, width, height, channels, pixels, quality)) {
            fprintf(stderr, "Erro ao salvar '%s'\n", output_path);
        } else {
            printf("Convertido: %s → %s (qualidade %d)\n", input_path, output_path, quality);
        }

        stbi_image_free(pixels);
    }

    closedir(dir);
    printf("\nProcessamento concluído!\n");
    return 0;
}