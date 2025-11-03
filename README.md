# AxAccept-Bench (Benchmark for Acceptability of Approximation)

`AxAccept-Bench` is a benchmark suite designed to evaluate the **acceptability levels** of approximate computing techniques.

This project provides a set of applications and scripts to test different approximation parameters using a complete RISC-V simulation stack. The goal is to explore the trade-offs between hardware approximation, performance, and the perceptual quality (acceptability) of the final result.

---

## 🚀 Core Architecture & Components

This benchmark environment relies on three main components developed by the VArchC research group and the RISC-V community.

* **1. Approximate Hardware Simulator:**
    * **Repo:** [VArchC/axpike-isa-sim](https://github.com/VArchC/axpike-isa-sim.git)
    * **Description:** A modified ISA-level simulator (based on Spike) that understands and executes approximate instructions.

* **2. Proxy Kernel (OS Layer):**
    * **Repo:** [VArchC/axpike-pk](https://github.com/VArchC/axpike-pk.git)
    * **Description:** The modified Proxy Kernel (PK) that acts as a simple operating system, managing the approximate hardware features and running the applications on top of the simulator.

* **3. Compiler Toolchain:**
    * **Repo:** [riscv-collab/riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain.git)
    * **Description:** The standard RISC-V GNU Toolchain (GCC) used to compile the benchmark applications into RISC-V binaries.

---

## 🔧 Setup & Installation

*(Aqui você deve adicionar as instruções de como compilar. A ordem é crucial)*

1.  **Build the Toolchain:**
    ```bash
    # [TODO: Adicionar o comando para compilar o riscv-gnu-toolchain]
    # ex: ./configure --prefix=/opt/riscv && make
    ```

2.  **Build the Proxy Kernel (PK):**
    ```bash
    # [TODO: Adicionar o comando para compilar o axpike-pk]
    # ex: mkdir build && cd build && ../configure --prefix=/opt/riscv ...
    ```

3.  **Build the Simulator (AxPike):**
    ```bash
    # [TODO: Adicionar o comando para compilar o axpike-isa-sim]
    ```

---

## 🏃‍♀️ How to Run the Benchmark

*(Aqui você coloca o comando final para rodar o seu experimento)*

```bash
# Exemplo de como rodar uma aplicação
/path/to/axpike-sim /path/to/axpike-pk /path/to/benchmark-application.elf
