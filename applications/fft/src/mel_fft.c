// //////////////////////////////////////////////////////////////////////////
// main.cpp - Mel Spectrogram usando a biblioteca kissfft
// Guilherme Saides Serbai 2026
// //////////////////////////////////////////////////////////////////////////
// Copyright (c) 2026 Guilherme Saides Serbai
// //////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "kiss_fft.h"

#define SAMPLE_RATE 16000
#define N_FFT 512
#define HOP_LENGTH 256
#define N_MELS 40
#define PI 3.14159265358979323846

// ===============================
// 1. Estruturas e I/O Bare Metal
// ===============================
typedef struct {
    char* data;
    size_t size;
    size_t capacity;
} ByteBuffer;

void append_buffer(ByteBuffer* buf, const char* temp, size_t n) {
    if (buf->size + n > buf->capacity) {
        buf->capacity = (buf->size + n) * 2; 
        buf->data = (char*)realloc(buf->data, buf->capacity);
    }
    for (size_t i = 0; i < n; i++) {
        buf->data[buf->size + i] = temp[i];
    }
    buf->size += n;
}

void write_bytes(const void* data, size_t len) {
    const unsigned char* bytes = (const unsigned char*)data;
    for (size_t i = 0; i < len; i++) {
        putchar(bytes[i]);
    }
}

int readNextInt(const char* buffer, size_t size, size_t* cursor) {
    int value = 0;
    int started = 0;
    while (*cursor < size) {
        char c = buffer[(*cursor)++];
        if (c >= '0' && c <= '9') {
            value = value * 10 + (c - '0');
            started = 1;
        } else if (started) {
            break;
        }
    }
    return started ? value : -1;
}

float readNextFloat(const char* buffer, size_t size, size_t* cursor) {
    float value = 0.0f, fraction = 0.0f, divisor = 1.0f;
    int sign = 1, started = 0, in_fraction = 0;

    while (*cursor < size) {
        char c = buffer[(*cursor)++];
        if (!started) {
            if (c == '-') { sign = -1; started = 1; }
            else if (c >= '0' && c <= '9') { value = (c - '0'); started = 1; }
            else if (c == '.') { in_fraction = 1; started = 1; }
        } else {
            if (c >= '0' && c <= '9') {
                if (in_fraction) {
                    divisor *= 10.0f;
                    fraction += (c - '0') / divisor;
                } else {
                    value = value * 10.0f + (c - '0');
                }
            } else if (c == '.' && !in_fraction) {
                in_fraction = 1;
            } else {
                break;
            }
        }
    }
    return sign * (value + fraction);
}

// =======================================
// 2. Matemática do Banco de Filtros Mel
// =======================================
float hz_to_mel(float hz) {
    return 2595.0f * log10f(1.0f + hz / 700.0f);
}

float mel_to_hz(float mel) {
    return 700.0f * (powf(10.0f, mel / 2595.0f) - 1.0f);
}

// Constroi a matriz de pesos dos filtros Mel (N_MELS x (N_FFT/2 + 1))
// Essa matriz é fixa, só calculamos uma vez
void create_mel_filterbank(float* filterbank, int num_bins) {
    float min_mel = hz_to_mel(0.0f);
    float max_mel = hz_to_mel((float)SAMPLE_RATE / 2.0f);
    float mel_step = (max_mel - min_mel) / (N_MELS + 1);

    // Frequências centrais dos filtros em Hz
    float center_freqs[N_MELS + 2];
    for (int i = 0; i < N_MELS + 2; i++) {
        center_freqs[i] = mel_to_hz(min_mel + i * mel_step);
    }

    // Calcula os pesos triangulares para cada bin da FFT
    for (int m = 0; m < N_MELS; m++) {
        for (int k = 0; k < num_bins; k++) {
            float freq = (k * (float)SAMPLE_RATE) / N_FFT;
            float weight = 0.0f;

            if (freq >= center_freqs[m] && freq <= center_freqs[m+1]) {
                weight = (freq - center_freqs[m]) / (center_freqs[m+1] - center_freqs[m]);
            } else if (freq > center_freqs[m+1] && freq <= center_freqs[m+2]) {
                weight = (center_freqs[m+2] - freq) / (center_freqs[m+2] - center_freqs[m+1]);
            }
            // Vetor 1D achatado: índice = m * num_bins + k
            filterbank[m * num_bins + k] = weight;
        }
    }
}

// ===============================
// 3. O Workload Principal
// ===============================
void compute_mel_spectrogram(const float* audio_data, int num_samples, float** out_mel, int* out_frames) {
    // 1. Calcular frames (descartamos o final se não couber uma janela inteira)
    int num_frames = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1; 
    *out_frames = num_frames;

    // Alocar a matriz de saída achatada (num_frames * N_MELS)
    float* mel_matrix = (float*)calloc(num_frames * N_MELS, sizeof(float));
    *out_mel = mel_matrix;

    // 2. Preparar Kiss FFT e Banco Mel
    kiss_fft_cfg cfg = kiss_fft_alloc(N_FFT, 0, NULL, NULL);
    kiss_fft_cpx cx_in[N_FFT];
    kiss_fft_cpx cx_out[N_FFT];

    int num_bins = N_FFT / 2 + 1; // Só metade do espectro importa (Nyquist)
    float* power_spectrum = (float*)malloc(num_bins * sizeof(float));
    float* mel_filters = (float*)malloc(N_MELS * num_bins * sizeof(float));
    
    create_mel_filterbank(mel_filters, num_bins);

    // 3. Processar cada frame
    for (int f = 0; f < num_frames; f++) {
        int start_idx = f * HOP_LENGTH;

        // Copiar audio pro buffer de entrada da FFT e aplicar janela de Hann
        for (int i = 0; i < N_FFT; i++) {
            float sample = 0.0f;
            if (start_idx + i < num_samples) {
                sample = audio_data[start_idx + i];
            }
            // Janela de Hann: 0.5 * (1 - cos(2*pi*n / (N-1)))
            float hann_window = 0.5f * (1.0f - cosf((2.0f * PI * i) / (N_FFT - 1)));
            
            cx_in[i].r = sample * hann_window;
            cx_in[i].i = 0.0f; // Parte imaginária é zero
        }

        // Executar FFT
        kiss_fft(cfg, cx_in, cx_out);

        // Calcular espectro de potência (|X(k)|^2)
        for (int k = 0; k < num_bins; k++) {
            power_spectrum[k] = (cx_out[k].r * cx_out[k].r) + (cx_out[k].i * cx_out[k].i);
        }

        // Aplicar filtros Mel e somar as energias
        for (int m = 0; m < N_MELS; m++) {
            float mel_energy = 0.0f;
            for (int k = 0; k < num_bins; k++) {
                mel_energy += power_spectrum[k] * mel_filters[m * num_bins + k];
            }
            
            // Transformada logarítmica (evitando log de zero com constante pequena)
            // Usa-se log10 na maioria dos sistemas, ou log natural
            mel_matrix[f * N_MELS + m] = log10f(mel_energy + 1e-9f);
        }
    }

    free(power_spectrum);
    free(mel_filters);
    free(cfg);
}

// ===============================
// MAIN
// ===============================
int main() {
    ByteBuffer inputBuffer = {NULL, 0, 4096};
    inputBuffer.data = (char*)malloc(inputBuffer.capacity);
    char temp[4096];

    // LER DA ENTRADA PADRÃO
    while (1) {
        size_t n = fread(temp, 1, sizeof(temp), stdin);
        if (n == 0) break;
        append_buffer(&inputBuffer, temp, n);
    }

    if (inputBuffer.size == 0) {
        fprintf(stderr, "Erro: Nenhuma entrada recebida via stdin.\n");
        return 1;
    }

    // EXTRAIR OS DADOS DO BUFFER
    size_t cursor = 0;
    int num_samples = readNextInt(inputBuffer.data, inputBuffer.size, &cursor);
    
    if (num_samples <= 0) {
        fprintf(stderr, "Erro: falha ao ler o numero de samples.\n");
        return 1;
    }

    float* audio_data = (float*)malloc(num_samples * sizeof(float));
    for (int i = 0; i < num_samples; i++) {
        audio_data[i] = readNextFloat(inputBuffer.data, inputBuffer.size, &cursor);
    }

    free(inputBuffer.data);

    // EXECUTAR WORKLOAD APROXIMADO
    int num_frames;
    float* mel_matrix;
    compute_mel_spectrogram(audio_data, num_samples, &mel_matrix, &num_frames);

    // ESCREVER SAÍDA BINÁRIA
    int n_mels = N_MELS;
    write_bytes(&num_frames, sizeof(int));
    write_bytes(&n_mels, sizeof(int));
    write_bytes(mel_matrix, num_frames * n_mels * sizeof(float));

    free(audio_data);
    free(mel_matrix);
    
    return 0;
}