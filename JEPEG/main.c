#include <stdio.h>
#include <stdlib.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include "embeddedimage.h"  
#include "base64.h" // << AQUI

// Função que recebe o JPEG em memória
void output_jpeg(void *context, void *data, int size) {
    base64_encode((unsigned char*)data, size);
}

int main(int argc, char *argv[]) {

    if (argc != 2) {
        printf("Uso: %s <qualidade_1_100>\n", argv[0]);
        return 1;
    }

    int quality = atoi(argv[1]);

    int w, h, c;

    unsigned char *pixels = stbi_load_from_memory(
        dataimage, dataimage_len,
        &w, &h, &c, 3
    );

    if (!pixels) {
        printf("Erro ao carregar a imagem.\n");
        return 1;
    }

    printf("BEGINJPEG\n");

    stbi_write_jpg_to_func(
        output_jpeg,
        NULL,
        w, h, 3,
        pixels,
        quality
    );

    printf("\nENDJPEG\n");

    stbi_image_free(pixels);
    return 0;
}
