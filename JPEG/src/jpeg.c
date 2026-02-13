/*
 * jpeg.c
 * 
 * Created on: Sep 9, 2013
 * 			Author: Amir Yazdanbakhsh <a.yazdanbakhsh@gatech.edu>
 * 
 * Modified by Guilherme Saides Serbai on : Nov 17, 2025
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "datatype.h"
#include "jpegconfig.h"
#include "prototype.h"

#include "rgbimage.h"

#if defined(_WIN32)
#include <io.h>
#include <fcntl.h>
#else
#include <unistd.h>
#endif

#define OUT_BUFFER_SIZE 5000000
//#define OUT_BUFFER_SIZE 500000 // in bytes


int main (int argc, const char* argv[]) {
    setvbuf(stderr, NULL, _IONBF, 0);

    #if defined(_WIN32)
    _setmode(_fileno(stdin), _O_BINARY);
    _setmode(_fileno(stdout), _O_BINARY);
    #endif
    
    if (argc < 2) {
        fprintf(stderr, "Erro: Argumentos faltando.\n");
        fprintf(stderr, "Uso: %s <qualidade_1_a_100> [rgb|gray]\n", argv[0]);
        fprintf(stderr, "  qualidade_1_a_100: Fator de qualidade JPEG (1-100)\n");
        fprintf(stderr, "  rgb|gray: Modo de codificação (padrão: gray)\n");
        return 1;
    }

    
    int quality_1_to_100 = atoi(argv[1]);
    if (quality_1_to_100 < 1 || quality_1_to_100 > 100) {
        fprintf(stderr, "Erro: O parâmetro de qualidade deve ser um número entre 1 e 100.\n");
        return 1;
    }
    
    // Determina o modo de imagem (RGB ou GRAY)
    UINT32 imageFormat = GRAY;
    if (argc >= 3) {
        if (strcmp(argv[2], "rgb") == 0) {
            imageFormat = RGB;
            fprintf(stderr, "Modo: RGB (4:2:0)\n");
        } else if (strcmp(argv[2], "gray") == 0) {
            imageFormat = GRAY;
            fprintf(stderr, "Modo: Escala de Cinza\n");
        }
    }
    
    // 3. Calcula o fator de qualidade: Q=1 -> tabelas pequenas (pior qualidade, arquivo maior)
    // Q=100 -> tabelas grandes (melhor qualidade, arquivo menor)
    UINT32 qualityFactor = (UINT32)((quality_1_to_100 * 1024) / 100);
    
    fprintf(stderr, "Usando qualidade %d/100 (Fator AxBench: %u)\n", quality_1_to_100, (unsigned int)qualityFactor);

    UINT8 *outputBuffer;
    UINT8 *outputBufferPtr;

    RgbImage srcImage;
    initRgbImage(&srcImage);
    fprintf(stderr, "Lendo imagem do stdin...\n");
    if (loadRgbImageFromStream(stdin, &srcImage) == 0) {
        fprintf(stderr, "Error! Oops: Cannot load the input image from stdin!\n");
        return -1;
    }

    // Se for modo grayscale, converte para grayscale
    if (imageFormat == GRAY) {
        makeGrayscale(&srcImage);
    }
    // Se for RGB, mantém os valores RGB originais

    outputBuffer = (UINT8 *) malloc(OUT_BUFFER_SIZE * sizeof(UINT8));


    outputBufferPtr = outputBuffer;
    outputBufferPtr = encodeImage(
        &srcImage, outputBufferPtr, qualityFactor, imageFormat
    );


    freeRgbImage(&srcImage);

    long bytesEscritos = (long)(outputBufferPtr - outputBuffer);
    fprintf(stderr, "Escrevendo %ld bytes para stdout...\n", bytesEscritos);
    fflush(stderr);  // Garante que todo stderr seja escrito antes do JPEG

    // Escreve bytes JPEG diretamente no stdout usando syscall write (evita buffering)
    #if defined(_WIN32)
    for (long i = 0; i < bytesEscritos; i++) {
        fputc(outputBuffer[i], stdout);
    }
    #else
    write(STDOUT_FILENO, outputBuffer, bytesEscritos);
    #endif

    free(outputBuffer);
    //fprintf(stderr, "Concluído.\n");
    return 0; 
}