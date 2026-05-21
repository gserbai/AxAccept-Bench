# Execution and Compilation Guide: AxPike JPEG Encoder

This guide covers the steps to compile and execute the RISC-V JPEG encoder using the **AxPike** simulator with **ADELE** (Approximate Computing) support.

## 1. Important: Pre-Execution Steps

To ensure the output image is not corrupted by system logs, you must handle the Proxy Kernel (PK) output.

### Option A: Modify the Proxy Kernel (Recommended)

You need to silence the bootloader messages in the `axpike-pk` source:

1. Open the file: `axpike-pk/machine/minit.c`
2. **Comment out** the following line:
```c
// printm("bbl loader");

```


3. Recompile the `axpike-pk`.

### Option B: Post-Processing

If you do not modify the kernel, you must use the `clean_jpeg` tool to strip the logs from your final image. This is necessary because the `axpike-pk` logs will otherwise prevent the image from opening in standard viewers.

```bash
./clean_jpeg.sh dirty_output.jpg final_output.jpg

```
---

## 2. Compiling the Application

Use the RISC-V cross-compiler to generate a static binary with high-level optimization:

```bash
cd applications/jpeg/RunJpeg/src
riscv64-unknown-elf-g++ -O3 -static -o ./toojpeg_encoder main.cpp toojpeg.cpp

```

* **`-O3`**: High optimization level for performance.
* **`-static`**: Required for bare-metal/simulator execution to include all libraries.

---

## 3. Executing the Application

Run the simulation using **AxPike** with the following parameters for cache and approximate memory (AXRAM) attention you can alter the parameters:

to you use the parameter de errors you need set for on the variavel initial in /axpike-isa-sim/adele/adf/AxRAM.adf


```bash
axpike --adele=mem_read_prob:1e-2,linesz:32 --adele-activate=0:AXRAM --dc=128:8:32 --ic=256:4:32 --l2=1024:4:32 pk ./home/guilherme/AxAccept-Bench/applications/jpeg/RunJpeg/src/toojpeg_encoder 100 < path.csv > output.jpeg

```

### Batch Processing

If you want to process a large number of images (e.g., the imagenette dataset)
in batch mode, follow the instructions available in:

See [RunJpeg/usagerunjpeg.md](RunJpeg/usagerunjpeg.md)

The commands described in that document will automatically execute
the JPEG encoder over the dataset and generate a new dataset using
the specified approximation parameters.

### Parameter Breakdown:

* **`--adele`**: Sets memory read error probability and line size.
* **`--adele-activate`**: Activates **AXRAM** for the specified memory region.
* **`--dc / --ic / --l2`**: Configures Data, Instruction, and L2 caches (Size:Ways:LineSize).
* **`pk`**: The Proxy Kernel used to load and run the binary.
* **`1 < lena.csv`**: Pass the quality factor (1) and redirect the input image data.
* **`> output.jpeg`**: Redirects the application output to the JPEG file.

---

## 4. Troubleshooting

If the `output.jpeg` is not opening, ensure that:

1. The `printm` line was successfully commented out.
2. You are using the correct `xxx.csv` format for the encoder.

---
