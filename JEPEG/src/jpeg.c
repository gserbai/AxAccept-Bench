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
#endif

#define OUT_BUFFER_SIZE 5000000
//#define OUT_BUFFER_SIZE 500000 // in bytes


int main (int argc, const char* argv[]) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);


    #if defined(_WIN32)
    _setmode(_fileno(stdin), _O_BINARY);
    _setmode(_fileno(stdout), _O_BINARY);
    #endif
    
    if (argc != 2) {
        fprintf(stderr, "Erro: Argumento de qualidade faltando.\n");
        fprintf(stderr, "Uso: %s <qualidade_1_a_100>\n", argv[0]);
        return 1;
    }

    
    int quality_1_to_100 = atoi(argv[1]);
    if (quality_1_to_100 < 1 || quality_1_to_100 > 100) {
        fprintf(stderr, "Erro: O parâmetro de qualidade deve ser um número entre 1 e 100.\n");
        return 1;
    }
    
    // 3. Converte a escala 1-100 para a escala do AxBench (1-1024)
    // (ex: 90 se torna 921)
    UINT32 qualityFactor = (UINT32)((quality_1_to_100 * 1024) / 100);
    
    fprintf(stderr, "Usando qualidade %d/100 (Fator AxBench: %u)\n", quality_1_to_100, (unsigned int)qualityFactor);



    UINT32 imageFormat;
    UINT8 *outputBuffer;
    UINT8 *outputBufferPtr;

    imageFormat = GRAY;


    RgbImage srcImage;
    initRgbImage(&srcImage);
    fprintf(stderr, "Lendo imagem do stdin...\n");
    if (loadRgbImageFromStream(stdin, &srcImage) == 0) {
        fprintf(stderr, "Error! Oops: Cannot load the input image from stdin!\n");
        return -1;
    }

    makeGrayscale(&srcImage);

    outputBuffer = (UINT8 *) malloc(OUT_BUFFER_SIZE * sizeof(UINT8));


    outputBufferPtr = outputBuffer;
    outputBufferPtr = encodeImage(
        &srcImage, outputBufferPtr, qualityFactor, imageFormat
    );


    freeRgbImage(&srcImage);

    long bytesEscritos = (long)(outputBufferPtr - outputBuffer);
    fprintf(stderr, "Escrevendo %ld bytes para stdout...\n", bytesEscritos);

    fwrite(outputBuffer, 1, bytesEscritos, stdout);

    free(outputBuffer);
    //fprintf(stderr, "Concluído.\n");
    return 0; 
}