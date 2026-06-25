// ///////////////////////////////////////////////////////////////////
// dominant_freq_bin.cpp - Dominant Frequency (Pitch Recognition) via STFT
// Versão com input binário float32 raw (sem parser CSV)
// Guilherme Saides Serbai 2026
//
// Formato de entrada (stdin):
//   Stream de float32 little-endian raw, sem cabeçalho.
//   Cada amostra = 4 bytes. Ex: gerado por
//     python3 -c "import numpy as np; np.array(data, dtype=np.float32).tofile('/dev/stdout')"
//
// Formato de saída (stdout, 12 bytes):
//   [int32 LE: num_samples] [int32 LE: num_frames] [float32 LE: freq_hz]
// ///////////////////////////////////////////////////////////////////

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
void writeInt32Binary(int val) {
    const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&val);
    for (size_t i = 0; i < sizeof(int); i++) putchar(bytes[i]);
}

void writeFloatBinary(float val) {
    const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&val);
    for (size_t i = 0; i < sizeof(float); i++) putchar(bytes[i]);
}

// ==============================================================
// Workload: STFT + HPS + Interpolação Parabólica
// ==============================================================
float compute_dominant_frequency(const std::vector<float>& audio_data) {
    int num_samples = (int)audio_data.size();
    int num_frames = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1;

    kiss_fft_cfg cfg = kiss_fft_alloc(N_FFT, 0, NULL, NULL);
    std::vector<kiss_fft_cpx> cx_in(N_FFT);
    std::vector<kiss_fft_cpx> cx_out(N_FFT);

    int num_bins = N_FFT / 2 + 1;

    // double para acumulação: bins somam ~222 parcelas chegando a ~5e16 no pico
    // float32 perderia dígitos significativos nessa faixa
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

    // Lê float32 raw diretamente do stdin — sem parser de texto
    // Um bit flipado pelo AxRAM corrompe no máximo 1 amostra,
    // não quebra a estrutura do stream
    std::vector<float> audio_data;
    float sample;

    while (fread(&sample, sizeof(float), 1, stdin) == 1) {
        audio_data.push_back(sample);
    }

    if (audio_data.empty()) {
        fprintf(stderr, "Erro: Nenhuma amostra recebida no stdin.\n");
        return 1;
    }

    float dominant_freq = compute_dominant_frequency(audio_data);

    // Saída binária: [int32: num_samples] [int32: num_frames] [float32: freq_hz]
    int num_samples = (int)audio_data.size();
    int num_frames  = 1 + (num_samples - N_FFT) / HOP_LENGTH;
    if (num_frames < 1) num_frames = 1;

    writeInt32Binary(num_samples);
    writeInt32Binary(num_frames);
    writeFloatBinary(dominant_freq);

    return 0;
}
