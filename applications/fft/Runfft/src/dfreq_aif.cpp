// ///////////////////////////////////////////////////////////////////
// dfreq_aif.c - Dominant Frequency (Pitch Recognition) via STFT
// Versão C Puro (Bare-Metal / Bypass C++)
// //////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "kiss_fft.h"

// Parâmetros padrão MIREX para pitch de instrumentos acústicos
#define SAMPLE_RATE 44100
#define N_FFT       4096
#define HOP_LENGTH  512

#define PI 3.14159265358979323846

// ===============================
// Output Binário Bare-Metal
// ===============================
void writeFloatBinary(float val) {
    unsigned char* bytes = (unsigned char*)&val;
    for (size_t i = 0; i < sizeof(float); i++) {
        putchar(bytes[i]);
    }
}

// ==============================================================
// Parser AIFF Bare-Metal (C Puro)
// ==============================================================
uint32_t read_be32(FILE* f) {
    uint8_t b[4];
    if (fread(b, 1, 4, f) != 4) return 0;
    return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3];
}

uint16_t read_be16(FILE* f) {
    uint8_t b[2];
    if (fread(b, 1, 2, f) != 2) return 0;
    return (b[0] << 8) | b[1];
}

int read_string(FILE* f, int len, char* out_str) {
    if (fread(out_str, 1, len, f) != len) return 0;
    out_str[len] = '\0';
    return 1;
}

float* load_aiff_native(const char* filename, int* out_num_samples) {
    FILE* file = fopen(filename, "rb");
    if (!file) {
        *out_num_samples = 0;
        return NULL;
    }

    char str_buf[5];
    if (!read_string(file, 4, str_buf) || strcmp(str_buf, "FORM") != 0) { fclose(file); return NULL; }
    read_be32(file); // Pula tamanho total
    if (!read_string(file, 4, str_buf) || strcmp(str_buf, "AIFF") != 0) { fclose(file); return NULL; }

    uint16_t numChannels = 1;
    uint32_t numSampleFrames = 0;
    uint16_t sampleSize = 16;
    float* audio_data = NULL;

    while (!feof(file)) {
        if (!read_string(file, 4, str_buf)) break;
        uint32_t chunkSize = read_be32(file);

        if (strcmp(str_buf, "COMM") == 0) {
            numChannels = read_be16(file);
            numSampleFrames = read_be32(file);
            sampleSize = read_be16(file);
            fseek(file, 10, SEEK_CUR); // Pula float 80-bits Apple
            if (chunkSize % 2 != 0) fseek(file, 1, SEEK_CUR);
        }
        else if (strcmp(str_buf, "SSND") == 0) {
            uint32_t offset = read_be32(file);
            read_be32(file); // Pula blockSize
            fseek(file, offset, SEEK_CUR);

            audio_data = (float*)malloc(numSampleFrames * sizeof(float));
            for (uint32_t i = 0; i < numSampleFrames; i++) {
                float sample_sum = 0.0f;
                for (int c = 0; c < numChannels; c++) {
                    if (sampleSize == 16) {
                        int16_t val = (int16_t)read_be16(file);
                        sample_sum += (float)val / 32768.0f; // Normaliza
                    }
                }
                audio_data[i] = sample_sum / numChannels; // Mixa pra mono
            }
            *out_num_samples = numSampleFrames;
            break;
        }
        else {
            fseek(file, chunkSize + (chunkSize % 2), SEEK_CUR);
        }
    }
    fclose(file);
    return audio_data;
}

// ==============================================================
// Workload: STFT + HPS + Interpolação Parabólica
// ==============================================================
float compute_dominant_frequency(float* audio_data, int num_samples) {
    int num_frames = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1;

    kiss_fft_cfg cfg = kiss_fft_alloc(N_FFT, 0, NULL, NULL);
    kiss_fft_cpx* cx_in = (kiss_fft_cpx*)malloc(N_FFT * sizeof(kiss_fft_cpx));
    kiss_fft_cpx* cx_out = (kiss_fft_cpx*)malloc(N_FFT * sizeof(kiss_fft_cpx));

    int num_bins = N_FFT / 2 + 1;
    float* total_power = (float*)calloc(num_bins, sizeof(float));

    for (int f = 0; f < num_frames; f++) {
        int start_idx = f * HOP_LENGTH;

        for (int i = 0; i < N_FFT; i++) {
            float sample = (start_idx + i < num_samples) ? audio_data[start_idx + i] : 0.0f;
            float hann_window = 0.5f * (1.0f - cos((2.0f * PI * i) / (N_FFT - 1)));
            cx_in[i].r = sample * hann_window;
            cx_in[i].i = 0.0f;
        }

        kiss_fft(cfg, cx_in, cx_out);

        for (int k = 0; k < num_bins; k++) {
            total_power[k] += (cx_out[k].r * cx_out[k].r) + (cx_out[k].i * cx_out[k].i);
        }
    }

    float* hps = (float*)malloc(num_bins * sizeof(float));
    for (int k = 1; k < num_bins; k++) {
        hps[k] = total_power[k];
        if (k * 2 < num_bins) hps[k] *= total_power[k * 2];
        if (k * 3 < num_bins) hps[k] *= total_power[k * 3];
    }

    int max_bin = 1;
    float max_power = 0.0f;
    for (int k = 1; k < num_bins; k++) {
        if (hps[k] > max_power) {
            max_power = hps[k];
            max_bin = k;
        }
    }

    float refined_bin = (float)max_bin;
    if (max_bin > 1 && max_bin < num_bins - 1) {
        float alpha = hps[max_bin - 1];
        float beta  = hps[max_bin];
        float gamma = hps[max_bin + 1];
        float denom = alpha - 2.0f * beta + gamma;
        if (denom != 0.0f) {
            refined_bin = max_bin + 0.5f * (alpha - gamma) / denom;
        }
    }

    free(cfg);
    free(cx_in);
    free(cx_out);
    free(total_power);
    free(hps);

    return (refined_bin * (float)SAMPLE_RATE) / N_FFT;
}

// ===============================
// MAIN
// ===============================
int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <arquivo.aif>\n", argv[0]);
        return 1;
    }

    int num_samples = 0;
    float* audio_data = load_aiff_native(argv[1], &num_samples);

    if (!audio_data || num_samples == 0) {
        fprintf(stderr, "Erro: Falha ao ler o arquivo %s ou formato invalido.\n", argv[1]);
        return 1;
    }

    float dominant_freq = compute_dominant_frequency(audio_data, num_samples);

    int num_frames  = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1;

    unsigned char* p;
    p = (unsigned char*)&num_samples;
    for (size_t i = 0; i < sizeof(int); i++) putchar(p[i]);

    p = (unsigned char*)&num_frames;
    for (size_t i = 0; i < sizeof(int); i++) putchar(p[i]);

    writeFloatBinary(dominant_freq);

    free(audio_data);
    return 0;
}