# AxAccept-Bench: Benchmark for Acceptability of Approximation

**AxAccept-Bench** is a benchmark suite designed to evaluate the **acceptability levels** of approximate computing techniques.

This project provides a set of applications and scripts to test different approximation parameters using a complete RISC-V simulation stack. The goal is to explore the trade-offs between hardware approximation, performance, and the perceptual quality (acceptability) of the final result.

---

## 🏗️ Core Architecture & Components

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

## 🚀 Setup & Installation

This project assumes you already have the riscv-gnu-toolchain configured. If not, please refer to riscv-collab/riscv-gnu-toolchain for more information. You can clone the repository and follow the steps below:
RISC-V Toolchain Build:

```bash
    cd riscv-gnu-toolchain && \
    sudo apt-get install -y autoconf automake autotools-dev curl python3 python3-pip python3-tomli libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build git cmake libglib2.0-dev libslirp-dev && \
    sudo mkdir -p /opt/riscv && \
    ./configure --prefix=/opt/riscv && \
    make && \
    echo 'export PATH="/opt/riscv/bin:$PATH"' >> ~/.bashrc
```
You can install the environment **automatically** using the provided Makefile or set it up **manually** by following the steps below.


### Option A: Automatic Installation (Recommended)
If you have the `Makefile` configured, simply run:

```bash
make run

```

---

### Option B: Manual Installation

If you prefer to build each component manually, follow these steps in order.

#### 1. Install Dependencies (Ubuntu/Debian)

Before starting, ensure you have all necessary packages:

```bash
sudo apt-get update
sudo apt-get install -y autoconf automake autotools-dev curl python3 python3-pip \
    python3-tomli libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison \
    flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build \
    git cmake libglib2.0-dev libslirp-dev device-tree-compiler \
    libboost-regex-dev libboost-system-dev

```

#### 2. RISC-V GNU Toolchain

This will build the cross-compiler. *Note: This process may take some time.*

```bash
git clone [https://github.com/riscv-collab/riscv-gnu-toolchain.git](https://github.com/riscv-collab/riscv-gnu-toolchain.git)
cd riscv-gnu-toolchain

sudo mkdir -p /opt/riscv
./configure --prefix=/opt/riscv
make

# Add to PATH (Permanent)
echo 'export PATH=$PATH:/opt/riscv/bin' >> ~/.bashrc
source ~/.bashrc

```

#### 3. AxPike Proxy Kernel (pk)

Builds the lightweight OS layer.

```bash
git clone [https://github.com/VArchC/axpike-pk.git](https://github.com/VArchC/axpike-pk.git)
cd axpike-pk
mkdir build && cd build

../configure --prefix=$RISCV --host=riscv64-unknown-elf
sudo make
sudo make install

```

#### 4. AxPike ISA Simulator (Spike)

Builds the hardware simulator.

```bash
git clone [https://github.com/VArchC/axpike-isa-sim.git](https://github.com/VArchC/axpike-isa-sim.git)
cd axpike-isa-sim
mkdir build && cd build

../configure --prefix=$RISCV
sudo make -j$(nproc)
sudo make install

```

---

## 📖 How to Run

Detailed instructions on how to execute the benchmarks and analyze results can be found in the documentation:

👉 **[See Usage.md](JPEG/USAGE.md)**


