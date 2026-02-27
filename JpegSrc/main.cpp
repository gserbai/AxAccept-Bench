// //////////////////////////////////////////////////////////
// main.c from toojpeg.cpp
// written by Guilherme Saides Serbai, 2025-2026
// see https://create.stephan-brumme.com/toojpeg/
//


#include <iostream>
#include <vector>
#include <cstdio>
#include <cstdlib> 
#include "toojpeg.h"

void myOutput(unsigned char byte) {
    putchar(byte);
}

// O nosso trator de extrair números da stream
int readNextInt() {
    int c;
    int value = 0;
    bool started = false;
    
    while ((c = getchar()) != EOF) {
        if (c >= '0' && c <= '9') {
            value = value * 10 + (c - '0');
            started = true;
        } else if (started) {
            break; 
        }
    }
    if (!started) return -1;
    return value;
}

// Agora a main recebe os argumentos do terminal
int main(int argc, char* argv[]) {
    
    // 1. Lógica da Qualidade (Lê do terminal ou usa 90 por padrão)
    unsigned char quality = 90; 
    if (argc >= 2) {
        int q = std::atoi(argv[1]);
        if (q < 1) q = 1;      // Trava de segurança: minimo 1
        if (q > 100) q = 100;  // Trava de segurança: maximo 100
        quality = (unsigned char)q;
    }

    // 2. Lê a resolução no topo do arquivo
    int width = readNextInt();
    int height = readNextInt();
    
    if (width <= 0 || height <= 0) {
        fprintf(stderr, "Erro: Falha ao ler resolução do CSV.\n");
        return 1;
    }

    // 3. Prepara a RAM
    std::vector<unsigned char> pixels;
    pixels.reserve(width * height * 3);

    // 4. Lê os pixels


    //int val;
    //while ((val = readNextInt()) != -1) {
        //pixels.push_back((unsigned char)val);
    //}

    //if (pixels.size() < (size_t)(width * height * 3)) {
        //fprintf(stderr, "Aviso: O CSV tem menos pixels (%zu bytes) do que a resolucao %dx%d exige.\n", pixels.size(), width, height);
    //}

    size_t totalBytesEsperados = (size_t)width * height * 3;
    int val;

    // O loop agora só roda enquanto não atingir o limite de pixels
    while (pixels.size() < totalBytesEsperados && (val = readNextInt()) != -1) {
           pixels.push_back((unsigned char)val);
    }

    // Pequeno check de segurança para o seu benchmark
    if (pixels.size() < totalBytesEsperados) {
        fprintf(stderr, "Erro: O arquivo acabou antes de preencher todos os pixels!\n");
    }

    // 5. Configurações e Compressão
    const bool isRGB = true;
    const bool downsample = false; 
    
    // Passa a variável 'quality' que nós capturamos do terminal
    bool ok = TooJpeg::writeJpeg(myOutput, pixels.data(), width, height, isRGB, quality, downsample, NULL);
    
    if (!ok) {
        fprintf(stderr, "Erro interno na biblioteca toojpeg.\n");
        return 1;
    }

    return 0;
}