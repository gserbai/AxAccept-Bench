# AxAccept-Bench: Benchmark for Acceptability of Approximation

**AxAccept-Bench** is a benchmark suite designed to evaluate the **acceptability levels** of approximate computing techniques.

This project provides a set of applications and scripts to test different approximation parameters using a complete RISC-V simulation stack. The goal is to explore the trade-offs between hardware approximation, software, performance, and the perceptual quality (acceptability) of the final result. 

---

## Core Architecture & Components

This benchmark environment is built upon key components developed by the **VArchC research group**, the RISC-V community, and the original AxBench suite.

### 1. Approximate Hardware Simulator
* **Repository:** [VArchC/axpike-isa-sim](https://github.com/VArchC/axpike-isa-sim.git)
* **Description:** A modified version of the Spike simulator supporting approximate instructions.

### 2. Proxy Kernel (OS Layer)
* **Repository:** [VArchC/axpike-pk](https://github.com/VArchC/axpike-pk.git)
* **Description:** A lightweight application execution environment (proxy kernel) adapted for the approximate hardware.

### 3. Compiler Toolchain
* **Repository:** [riscv-collab/riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain.git)
* **Description:** The standard GCC toolchain for cross-compiling RISC-V applications.

### 5. TooJpeg (Image Compression Engine)
* **Author:** Stephan Brumme.
* **Project:** "TooJpeg: A very small C++ class to write JPEG files".
* **URL:** https://github.com/stbrumme/toojpeg
* **License:** Zlib License.

---

## Setup & Installation

This project assumes you already have the riscv-gnu-toolchain configured. If not, please refer to https://github.com/riscv-collab/riscv-gnu-toolchain.git for more information. You can clone the repository and follow the steps below:
RISC-V Toolchain Build:

example from comands to shell to you need run

```bash
    sudo mkdir -p /opt/riscv && \
    ./configure --prefix=/opt/riscv && \
    make && \
    echo 'export PATH=$PATH:/opt/riscv/bin' >> ~/.bashrc
    source ~/.bashrc
```

### You can install the environment by following the steps below.

> ⚠️ **CAUTION**
> Remember to use `git clone --recursive` when cloning the repository because it includes required submodule dependencies.

##### 1. AxPike Proxy Kernel (pk)

Builds the lightweight OS layer.

```bash
cd axpike-pk
mkdir build && cd build
../configure --prefix=$RISCV --host=riscv64-unknown-elf
make
sudo make install

```

##### 2. AxPike ISA Simulator (Spike)

Builds the hardware simulator.

```bash
cd axpike-isa-sim
mkdir build && 
cd build
../configure --prefix=$RISCV
make -j
sudo make install

```

---

## How to Run

Detailed instructions on how to execute the benchmarks and analyze results can be found in the documentation:

**[See Usage.md](applications/jpeg/src/usage.md)**


