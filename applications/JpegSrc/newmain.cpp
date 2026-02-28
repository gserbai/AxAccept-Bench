// //////////////////////////////////////////////////////////
// main.cpp - versão robusta para bare metal
// Guilherme Saides Serbai 2025-2026
// //////////////////////////////////////////////////////////

#include <iostream>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include "toojpeg.h"

void myOutput(unsigned char byte) {
    putchar(byte);
}

// ===============================
// Parser baseado em buffer
// ===============================
int readNextIntFromBuffer(const std::vector<char>& buffer, size_t& cursor) {
    int value = 0;
    bool started = false;

    while (cursor < buffer.size()) {
        char c = buffer[cursor++];

        if (c >= '0' && c <= '9') {
            value = value * 10 + (c - '0');
            started = true;
        } else if (started) {
            break;
        }
    }

    if (!started)
        return -1;

    return value;
}

int main(int argc, char* argv[]) {

    // ===============================
    // 1. Qualidade
    // ===============================
    unsigned char quality = 90;
    if (argc >= 2) {
        int q = std::atoi(argv[1]);
        if (q < 1)   q = 1;
        if (q > 100) q = 100;
        quality = (unsigned char)q;
    }

    // ===============================
    // 2. Ler TODA a entrada primeiro
    // ===============================
    std::vector<char> inputBuffer;
    char temp[4096];

    while (true) {
        size_t n = fread(temp, 1, sizeof(temp), stdin);
        if (n == 0)
            break;

        inputBuffer.insert(inputBuffer.end(), temp, temp + n);
    }

    if (inputBuffer.empty()) {
        fprintf(stderr, "Erro: Nenhuma entrada recebida.\n");
        return 1;
    }

    // ===============================
    // 3. Parsing começa aqui
    // ===============================
    size_t cursor = 0;

    int width  = readNextIntFromBuffer(inputBuffer, cursor);
    int height = readNextIntFromBuffer(inputBuffer, cursor);

    if (width <= 0 || height <= 0) {
        fprintf(stderr, "Erro: Falha ao ler resolução do CSV.\n");
        return 1;
    }

    size_t totalBytesEsperados = (size_t)width * height * 3;

    std::vector<unsigned char> pixels;
    pixels.reserve(totalBytesEsperados);

    while (pixels.size() < totalBytesEsperados) {
        int val = readNextIntFromBuffer(inputBuffer, cursor);
        if (val == -1)
            break;

        pixels.push_back((unsigned char)val);
    }

    if (pixels.size() < totalBytesEsperados) {
        fprintf(stderr,
                "Erro: Pixels insuficientes (%zu / %zu).\n",
                pixels.size(),
                totalBytesEsperados);
        return 1;
    }

    // ===============================
    // 4. Compressão JPEG
    // ===============================
    const bool isRGB = true;
    const bool downsample = false;

    bool ok = TooJpeg::writeJpeg(
        myOutput,
        pixels.data(),
        width,
        height,
        isRGB,
        quality,
        downsample,
        NULL
    );

    if (!ok) {
        fprintf(stderr, "Erro interno na biblioteca toojpeg.\n");
        return 1;
    }

    return 0;
}