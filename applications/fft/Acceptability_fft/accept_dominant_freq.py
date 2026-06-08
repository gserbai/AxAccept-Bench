######################################################################
# accept_dominant_freq.py - Avaliação de Aceitabilidade
# Author: Guilherme Saides Serbai
# Year: 2026
#
# Compara o dataset golden (.bin) com o dataset aproximado (.bin)
# gerado pelo AxPike, avaliando:
#   - Qualidade: MAPE entre frequências
#   - Aceitabilidade: mesma nota MIDI (escala temperada)
######################################################################






# =====================================================================
# CONVERSÃO PARA MIDI (A "ZONA DE TOLERÂNCIA" DA APROXIMAÇÃO)
# Fórmula: nota = round( 12 * log2(freq / 440) + 69 )
#
# Resumo rápido para revisão:
# 1. (freq / 440): Compara a nossa frequência com o Lá padrão (440 Hz).
# 2. log2(...)   : Aplica a escala de oitavas (como o ouvido funciona).
# 3. * 12        : Espalha o resultado pelas 12 notas de uma oitava.
# 4. + 69        : Ajusta para que 440 Hz caia exatamente na nota 69.
#
# O SEGREDO DO "ROUND" (O FUNIL):
# O round() puxa os números quebrados para a "caixinha" do número inteiro.
# - Se o Golden deu 440.0 Hz -> a conta dá 69.00 -> vira 69.
# - Se o Approx errou e deu 445.0 Hz -> a conta dá 69.19 -> vira 69!
# 
# Conclusão: Se cair na mesma "caixinha" (mesma nota), o erro matemático 
# é perdoado e o resultado é marcado como ACEITÁVEL.
# =====================================================================




import numpy as np
import pandas as pd
import struct
from pathlib import Path

GOLDEN_DIR = Path("/home/guilherme/dataset_golden_bin")
APPROX_DIR = Path("/home/guilherme/dataset_approx_bin")  # saída do AxPike

def read_bin(path):
    """Lê o .bin no formato [int32: num_samples][int32: num_frames][float32: freq_hz]."""
    with open(path, "rb") as f:
        data = f.read(12)
    if len(data) < 12:
        return None, None, None
    num_samples, num_frames, freq = struct.unpack("iif", data)
    return num_samples, num_frames, freq

def hz_to_note_number(freq):
    """
    Converte frequência Hz para número de nota MIDI (escala temperada).
    Referência: A4 = 440 Hz = nota MIDI 69.
    """
    if freq <= 0:
        return -1000
    return np.round(12 * np.log2(freq / 440.0) + 69)

def evaluate_pipeline():
    print("Carregando datasets...")

    golden_files = sorted(GOLDEN_DIR.rglob("*.bin"))

    if not golden_files:
        print(f"Nenhum .bin encontrado em {GOLDEN_DIR}")
        return

    records = []
    missing = 0

    for golden_path in golden_files:
        # Pareia pelo caminho relativo — mantém hierarquia de pastas
        relative = golden_path.relative_to(GOLDEN_DIR)
        approx_path = APPROX_DIR / relative

        if not approx_path.exists():
            missing += 1
            continue

        _, _, freq_golden = read_bin(golden_path)
        _, _, freq_approx = read_bin(approx_path)

        if freq_golden is None or freq_approx is None:
            missing += 1
            continue

        instrument = golden_path.parent.name

        records.append({
            "instrument":   instrument,
            "file":         golden_path.name,
            "freq_golden":  freq_golden,
            "freq_approx":  freq_approx,
        })

    if not records:
        print("Nenhum par golden/aproximado encontrado.")
        return

    df = pd.DataFrame(records)

    # 1. Qualidade (MAPE)
    divisor = np.where(df["freq_golden"] == 0, 1e-9, df["freq_golden"])
    mape = np.abs(df["freq_approx"] - df["freq_golden"]) / divisor
    df["quality_perc"] = ((1.0 - mape) * 100).clip(lower=0, upper=100)

    # 2. Aceitabilidade (Mesma Nota MIDI)
    df["nota_golden"] = df["freq_golden"].apply(hz_to_note_number)
    df["nota_approx"] = df["freq_approx"].apply(hz_to_note_number)
    df["is_acceptable"] = df["nota_golden"] == df["nota_approx"]

    # ==========================================
    # RESULTADOS GLOBAIS
    # ==========================================
    total     = len(df)
    acc       = df["is_acceptable"].sum()
    unacc     = total - acc
    perc_acc  = acc / total * 100
    perc_unacc = unacc / total * 100

    print("\n" + "="*50)
    print(" RESULTADOS GLOBAIS DA SIMULAÇÃO")
    print("="*50)
    print(f"Total de Áudios Processados : {total}")
    print(f"Arquivos sem par (ignorados): {missing}")
    print(f"Resultados ACEITÁVEIS       : {perc_acc:.2f}% ({acc} amostras)")
    print(f"Resultados INACEITÁVEIS     : {perc_unacc:.2f}% ({unacc} amostras)")

    # ==========================================
    # ANÁLISE POR THRESHOLD DE QUALIDADE
    # ==========================================
    print("\n" + "="*50)
    print(" ANÁLISE POR THRESHOLD DE QUALIDADE")
    print("="*50)

    thresholds = [99, 95, 90, 80, 70, 60, 50]
    for t in thresholds:
        df_bin = df[df["quality_perc"] >= t]
        total_bin = len(df_bin)
        if total_bin > 0:
            acc_bin   = df_bin["is_acceptable"].sum()
            unacc_bin = total_bin - acc_bin
            print(f"Qualidade >= {t:3d}% (Total: {total_bin:4d} amostras)")
            print(f"  -> Aceitáveis   : {acc_bin/total_bin*100:.2f}%")
            print(f"  -> Inaceitáveis : {unacc_bin/total_bin*100:.2f}%\n")
        else:
            print(f"Qualidade >= {t:3d}% : 0 amostras nessa faixa.\n")

    # ==========================================
    # ANÁLISE POR INSTRUMENTO
    # ==========================================
    print("="*50)
    print(" ANÁLISE POR INSTRUMENTO")
    print("="*50)
    for inst, group in df.groupby("instrument"):
        inst_acc = group["is_acceptable"].sum()
        inst_total = len(group)
        inst_perc = inst_acc / inst_total * 100
        inst_quality = group["quality_perc"].mean()
        print(f"{inst:20s}: {inst_perc:6.2f}% aceitáveis | qualidade média: {inst_quality:.2f}%")

if __name__ == "__main__":
    evaluate_pipeline()