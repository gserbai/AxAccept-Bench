# 📘 Master Guide: JPEG Encoder (RISC-V/AxAccept-Bench)

This guide unifies the commands for compilation, execution, log cleaning, and RGB tests.

## 1. 🛠️ Compilation (Required first)

Before running, you need to compile the C source code for RISC-V.

```bash
cd src
riscv64-unknown-elf-gcc -static -o ../jpeg_encoder *.c -lm
cd ..

```

*This generates the `jpeg_encoder` binary in the JPEG root folder.*

---

## 2. ⭐ Automatic Execution (Recommended)

Uses the `jpeg_wrapper.sh` script. It does everything: runs the encoder, removes junk (BBL logs), and generates the clean final JPEG.

**Syntax:**

```bash
./jpeg_wrapper.sh <input.csv> <output.jpg> [quality] [mode]

```

**Usage Examples:**

```bash
# Grayscale Mode (Default: quality 90)
./jpeg_wrapper.sh image.csv output_gray.jpg 90 gray

# RGB Mode (Quality 85)
./jpeg_wrapper.sh image.csv output_rgb.jpg 85 rgb

```

---

## 3. ⚙️ Manual Execution (Step by Step)

Useful if you need to debug or don't want to use the wrapper. The process is divided into **Generate** and **Clean**.

### Step A: Generate the JPEG (Dirty)

`axpike` mixes logs (text) with the image (binary).

```bash
# Syntax: cat CSV | axpike pk ./binary QUALITY MODE > OUTPUT
cat image.csv | axpike pk ./jpeg_encoder 90 rgb > dirty_output.jpg

```

*Note: You can use `2>/dev/null` to ignore errors, but the output file may still contain the BBL header.*

### Step B: Clean the JPEG

Removes the "bbl loader" text and other junk before the JPEG `FFD8` marker.

```bash
./clean_jpeg.sh dirty_output.jpg final_output.jpg

```

---

## 4. 🧪 Useful Tools & Tests

### Convert BMP to CSV

The encoder doesn't read BMP directly; it needs to convert to CSV (text) first.

```bash
python3 bmp_to_csv_nopil.py image.bmp > image.csv

```

## 5. 📝 Technical Parameter Summary

| Parameter | Values | Description |
| --- | --- | --- |
| **Quality** | `1` to `100` | Defines quantization. `1` = Worst quality/Smallest size. `100` = Best quality. |
| **Mode** | `gray` | Converts to grayscale (Y component only). |
| **Mode** | `rgb` | Keeps colors. Uses YCbCr with 4:2:0 downsampling (1 Y + ¼ Cb + ¼ Cr). |

### Expected Directory Structure

* `src/`: `.c` codes (encoder, huffman, rgbimage).
* `jpeg_wrapper.sh`: Main script.
* `clean_jpeg.sh`: Cleaning script (removes BBL logs).
* `jpeg_encoder`: Compiled binary (RISC-V).

---

### 💡 Quick Tip

If you get a permission error on any script:

```bash
chmod +x *.sh

```