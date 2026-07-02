######################################################################
# AxAccept-Bench (Audio FFT / Dominant Frequency)
# Author: Guilherme Saides Serbai
# Year: 2026
######################################################################

import csv
import math
import struct
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


# ===============================
# Experiment configuration
# ===============================

ERROR_RATE = "1e-4"

DATASET_DIR = Path("/home/guilherme/Music/dataset_iowa_music_bin")

OUTPUT_BIN_DIR = Path(f"./src/dataset_audio_error_rate_{ERROR_RATE}")
LOG_DIR = Path(f"./src/logs_audio_error_rate_{ERROR_RATE}")
SUMMARY_CSV = LOG_DIR / "summary.csv"

APP_BIN = "./dominant_freq"

INPUT_SUFFIX = ".bin"

# FFT input is raw float32 binary.
# 64 zero bytes = 16 float32 samples equal to 0.0.
ADD_PK_STDIN_PADDING = True
PK_STDIN_PADDING_BYTES = 64

# 1200 seconds = 20 minutes per file.
TIMEOUT_SEC = 1200

# Number of AxPike executions to run in parallel.
MAX_WORKERS = 4


# ===============================
# AxPike command
# ===============================

def build_cmd():
    return [
        "axpike",
        f"--adele=mem_read_prob:{ERROR_RATE},linesz:32",
        "--adele-activate=0:AXRAM",
        "--dc=128:8:32",
        "--ic=256:4:32",
        "--l2=1024:4:32",
        "pk",
        APP_BIN,
    ]


# ===============================
# Output classification
# ===============================

def midi_from_freq(freq_hz):
    if not math.isfinite(freq_hz) or freq_hz <= 0.0:
        return ""
    return int(round(69.0 + 12.0 * math.log2(freq_hz / 440.0)))


def classify_output_bytes(data: bytes):
    if len(data) == 0:
        return {
            "class": "TIMEOUT_OR_EMPTY",
            "crash": False,
            "status": "",
            "num_samples": "",
            "num_frames": "",
            "freq_hz": "",
            "midi": "",
        }

    crash_dump = (
        data.startswith(b"z  ")
        or b"User load segfault" in data
        or b"User store segfault" in data
        or b"User fetch segfault" in data
        or b"segfault" in data
    )

    if data.startswith(b"AXDFREQ1") and len(data) >= 24:
        _, status, num_samples, num_frames, freq_hz = struct.unpack("<8siiif", data[:24])

        if status != 0:
            cls = "APPLICATION_ERROR"
        elif not math.isfinite(freq_hz) or freq_hz <= 0.0 or freq_hz > 22050.0:
            cls = "INVALID_NUMERIC"
        elif crash_dump:
            cls = "RESULT_WITH_CRASH_DUMP"
        else:
            cls = "OK_RESULT"

        return {
            "class": cls,
            "crash": crash_dump,
            "status": status,
            "num_samples": num_samples,
            "num_frames": num_frames,
            "freq_hz": freq_hz,
            "midi": midi_from_freq(freq_hz),
        }

    if crash_dump:
        return {
            "class": "AXPIKE_CRASH_DUMP",
            "crash": True,
            "status": "",
            "num_samples": "",
            "num_frames": "",
            "freq_hz": "",
            "midi": "",
        }

    return {
        "class": "INVALID_OUTPUT",
        "crash": False,
        "status": "",
        "num_samples": "",
        "num_frames": "",
        "freq_hz": "",
        "midi": "",
    }


# ===============================
# One-file execution
# ===============================

def make_stdin_payload(input_path: Path) -> bytes:
    payload = bytearray()

    if ADD_PK_STDIN_PADDING:
        payload.extend(b"\x00" * PK_STDIN_PADDING_BYTES)

    payload.extend(input_path.read_bytes())
    return bytes(payload)


def run_one(input_path: Path, output_path: Path, log_path: Path):
    cmd = build_cmd()
    stdin_payload = make_stdin_payload(input_path)

    start = time.monotonic()

    try:
        proc = subprocess.run(
            cmd,
            input=stdin_payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SEC,
        )

        elapsed_sec = time.monotonic() - start

        output_data = proc.stdout if proc.stdout is not None else b""
        log_data = proc.stderr if proc.stderr is not None else b""

        output_path.write_bytes(output_data)
        log_path.write_bytes(log_data)

        outcome = classify_output_bytes(output_data)

        return {
            "returncode": proc.returncode,
            "elapsed_sec": elapsed_sec,
            "timeout": False,
            "output_bytes": len(output_data),
            **outcome,
        }

    except subprocess.TimeoutExpired as e:
        elapsed_sec = time.monotonic() - start

        output_path.write_bytes(b"")

        stderr_data = e.stderr if isinstance(e.stderr, (bytes, bytearray)) else b""
        with open(log_path, "wb") as f_log:
            if stderr_data:
                f_log.write(stderr_data)
            f_log.write(b"\nTIMEOUT\n")

        return {
            "returncode": 124,
            "elapsed_sec": elapsed_sec,
            "timeout": True,
            "output_bytes": 0,
            "class": "TIMEOUT_OR_EMPTY",
            "crash": False,
            "status": "",
            "num_samples": "",
            "num_frames": "",
            "freq_hz": "",
            "midi": "",
        }


# ===============================
# Summary
# ===============================

def write_summary(rows):
    if not rows:
        return

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "index",
        "relative_path",
        "input_file",
        "output_file",
        "log_file",
        "error_rate",
        "class",
        "crash",
        "returncode",
        "elapsed_sec",
        "timeout",
        "output_bytes",
        "status",
        "num_samples",
        "num_frames",
        "freq_hz",
        "midi",
    ]

    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ===============================
# Batch execution
# ===============================

def print_outcome(info):
    cls = info["class"]

    if cls == "OK_RESULT":
        print(
            f"  -> Finished: OK_RESULT "
            f"freq_hz={info['freq_hz']} midi={info['midi']} "
            f"time={info['elapsed_sec']:.2f}s"
        )

    elif cls == "AXPIKE_CRASH_DUMP":
        print(f"  -> Finished: AXPIKE_CRASH_DUMP time={info['elapsed_sec']:.2f}s")

    elif cls == "TIMEOUT_OR_EMPTY":
        print(f"  -> Finished: TIMEOUT_OR_EMPTY time={info['elapsed_sec']:.2f}s")

    else:
        print(
            f"  -> Finished: {cls} "
            f"returncode={info['returncode']} "
            f"bytes={info['output_bytes']} "
            f"time={info['elapsed_sec']:.2f}s"
        )


def process_one_file(index, input_bin):
    relative_path = input_bin.relative_to(DATASET_DIR)

    output_bin = OUTPUT_BIN_DIR / relative_path.with_suffix(".bin")
    output_log = LOG_DIR / relative_path.with_suffix(".log")

    output_bin.parent.mkdir(parents=True, exist_ok=True)
    output_log.parent.mkdir(parents=True, exist_ok=True)

    try:
        info = run_one(input_bin, output_bin, output_log)

    except Exception as e:
        info = {
            "returncode": "",
            "elapsed_sec": "",
            "timeout": "",
            "output_bytes": "",
            "class": "SCRIPT_ERROR",
            "crash": False,
            "status": "",
            "num_samples": "",
            "num_frames": "",
            "freq_hz": "",
            "midi": "",
        }

    row = {
        "index": index,
        "relative_path": str(relative_path),
        "input_file": str(input_bin),
        "output_file": str(output_bin),
        "log_file": str(output_log),
        "error_rate": ERROR_RATE,
        **info,
    }

    return row, info


def run_conversion():
    OUTPUT_BIN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    input_files = sorted(DATASET_DIR.rglob(f"*{INPUT_SUFFIX}"))

    if not input_files:
        print(f"No {INPUT_SUFFIX} files found in {DATASET_DIR}")
        return

    total = len(input_files)

    print(f"Found {total} audio files to process.")
    print(f"Error rate: {ERROR_RATE}")
    print(f"PK stdin padding: {ADD_PK_STDIN_PADDING} ({PK_STDIN_PADDING_BYTES} zero bytes)")
    print(f"Application: {APP_BIN}")
    print(f"Timeout: {TIMEOUT_SEC} seconds per file")
    print(f"Parallel workers: {MAX_WORKERS}")
    print(f"Outputs in: {OUTPUT_BIN_DIR}")
    print(f"Logs in:    {LOG_DIR}")
    print(f"Summary:    {SUMMARY_CSV}")

    rows = []
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_one_file, index, input_bin): (index, input_bin)
            for index, input_bin in enumerate(input_files, start=1)
        }

        for future in as_completed(futures):
            index, input_bin = futures[future]
            completed += 1

            try:
                row, info = future.result()

            except Exception as e:
                relative_path = input_bin.relative_to(DATASET_DIR)
                output_bin = OUTPUT_BIN_DIR / relative_path.with_suffix(".bin")
                output_log = LOG_DIR / relative_path.with_suffix(".log")

                info = {
                    "returncode": "",
                    "elapsed_sec": "",
                    "timeout": "",
                    "output_bytes": "",
                    "class": "SCRIPT_ERROR",
                    "crash": False,
                    "status": "",
                    "num_samples": "",
                    "num_frames": "",
                    "freq_hz": "",
                    "midi": "",
                }

                row = {
                    "index": index,
                    "relative_path": str(relative_path),
                    "input_file": str(input_bin),
                    "output_file": str(output_bin),
                    "log_file": str(output_log),
                    "error_rate": ERROR_RATE,
                    **info,
                }

                print(f"[{completed}/{total}] SCRIPT_ERROR: {relative_path} ({e})")
                rows.append(row)
                rows_sorted = sorted(rows, key=lambda r: int(r["index"]))
                write_summary(rows_sorted)
                continue

            rows.append(row)

            print(f"[{completed}/{total}] done: {row['relative_path']}")
            print_outcome(info)

            rows_sorted = sorted(rows, key=lambda r: int(r["index"]))
            write_summary(rows_sorted)

    print("\nCompleted.")
    print(f"Outputs in: {OUTPUT_BIN_DIR}")
    print(f"Logs in:    {LOG_DIR}")
    print(f"Summary:    {SUMMARY_CSV}")

if __name__ == "__main__":
    run_conversion()
