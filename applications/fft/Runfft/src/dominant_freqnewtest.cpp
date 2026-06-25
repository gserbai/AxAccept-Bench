// ///////////////////////////////////////////////////////////////////
// dominant_freq.cpp - Dominant Frequency (Pitch Recognition) via STFT
// Guilherme Saides Serbai 2026
// //////////////////////////////////////////////////////////////////

#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cmath>
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
    const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&val);
    for (size_t i = 0; i < sizeof(float); i++) {
        putchar(bytes[i]);
    }
}

// =========================================
// Parser CSV via strtof — robusto e sem
// erro de acúmulo de fração manual
// =========================================
bool readNextFloatFromBuffer(const std::vector<char>& buffer, size_t& cursor, float& out_val) {
    const char* data = buffer.data();
    const size_t size = buffer.size();

    // Pula separadores e espaços
    while (cursor < size) {
        char c = data[cursor];
        if (c == ',' || c == '\n' || c == '\r' || c == ';' || c == ' ') {
            cursor++;
        } else {
            break;
        }
    }

    if (cursor >= size) return false;

    // strtof já lida corretamente com sinal, ponto decimal e notação científica
    char* end = nullptr;
    float val = strtof(data + cursor, &end);

    if (end == data + cursor) {
        // Não parseou nada: pula até próxima linha
        while (cursor < size && data[cursor] != '\n') cursor++;
        return false;
    }

    cursor = (size_t)(end - data);
    out_val = val;
    return true;
}

// ==============================================================
// Workload: STFT + HPS + Interpolação Parabólica
// ==============================================================
float compute_dominant_frequency(const std::vector<float>& audio_data) {
    int num_samples = audio_data.size();
    int num_frames = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1;

    kiss_fft_cfg cfg = kiss_fft_alloc(N_FFT, 0, NULL, NULL);
    std::vector<kiss_fft_cpx> cx_in(N_FFT);
    std::vector<kiss_fft_cpx> cx_out(N_FFT);

    int num_bins = N_FFT / 2 + 1;
    // double para acumulação: evita perda de precisão (bins somam ~222 parcelas de ~1e5
    // cada, chegando a ~5e16 no pico — float32 perde dígitos significativos nessa faixa)
    std::vector<double> total_power(num_bins, 0.0);

    for (int f = 0; f < num_frames; f++) {
        int start_idx = f * HOP_LENGTH;

        for (int i = 0; i < N_FFT; i++) {
            float sample = (start_idx + i < num_samples) ? audio_data[start_idx + i] : 0.0f;
            float hann_window = 0.5f * (1.0f - std::cos((2.0f * PI * i) / (N_FFT - 1)));
            cx_in[i].r = sample * hann_window;
            cx_in[i].i = 0.0f;
        }

        kiss_fft(cfg, cx_in.data(), cx_out.data());

        for (int k = 0; k < num_bins; k++) {
            total_power[k] += (double)(cx_out[k].r * cx_out[k].r)
                            + (double)(cx_out[k].i * cx_out[k].i);
        }
    }

    // HPS (Harmonic Product Spectrum) — reforça o fundamental
    // Ref: Noll, A.M. (1969). Pitch determination of human speech by harmonic product spectrum
    // double também no HPS: produto triplo de valores ~5e16 caberia em double (max ~1.7e308)
    std::vector<double> hps(num_bins, 0.0);
    for (int k = 1; k < num_bins; k++) {
        hps[k] = total_power[k];
        if (k * 2 < num_bins) hps[k] *= total_power[k * 2];
        if (k * 3 < num_bins) hps[k] *= total_power[k * 3];
    }

    // Ignora bin 0 (DC) — começa do bin 1
    int max_bin = 1;
    double max_power = 0.0;
    for (int k = 1; k < num_bins; k++) {
        if (hps[k] > max_power) {
            max_power = hps[k];
            max_bin = k;
        }
    }

    // Interpolação Parabólica — refina frequência para precisão sub-bin
    // Ref: Smith & Serra (1987). Improvements to the Fundamental Frequency Estimator
    double refined_bin = (double)max_bin;
    if (max_bin > 1 && max_bin < num_bins - 1) {
        double alpha = hps[max_bin - 1];
        double beta  = hps[max_bin];
        double gamma = hps[max_bin + 1];
        double denom = alpha - 2.0 * beta + gamma;
        if (denom != 0.0) {
            refined_bin = max_bin + 0.5 * (alpha - gamma) / denom;
        }
    }

    free(cfg);

    return (float)(refined_bin * SAMPLE_RATE / N_FFT);
}

// ===============================
// MAIN
// ===============================
int main(int argc, char* argv[]) {

    std::vector<char> inputBuffer;
    char temp[4096];

    while (true) {
        size_t n = fread(temp, 1, sizeof(temp), stdin);
        if (n == 0) break;
        inputBuffer.insert(inputBuffer.end(), temp, temp + n);
    }

    if (inputBuffer.empty()) {
        fprintf(stderr, "Erro: Nenhuma entrada recebida.\n");
        return 1;
    }

    size_t cursor = 0;
    std::vector<float> audio_data;
    float val;
    while (readNextFloatFromBuffer(inputBuffer, cursor, val)) {
        audio_data.push_back(val);
    }

    if (audio_data.empty()) {
        fprintf(stderr, "Erro: Falha ao extrair amostras de audio do CSV.\n");
        return 1;
    }

    float dominant_freq = compute_dominant_frequency(audio_data);

    // Saída binária: [int32: num_samples] [int32: num_frames] [float32: freq_hz]
    int num_samples = (int)audio_data.size();
    int num_frames  = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1;

    const unsigned char* p;
    p = reinterpret_cast<const unsigned char*>(&num_samples);
    for (size_t i = 0; i < sizeof(int); i++) putchar(p[i]);

    p = reinterpret_cast<const unsigned char*>(&num_frames);
    for (size_t i = 0; i < sizeof(int); i++) putchar(p[i]);

    writeFloatBinary(dominant_freq);

    return 0;
}