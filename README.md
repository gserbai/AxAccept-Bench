# AxAccept-Bench (Benchmark for Acceptability of Approximation)

`AxAccept-Bench` is a benchmark suite designed to evaluate the **acceptability levels** of approximate computing techniques.

This project provides a set of applications and scripts to test different approximation parameters using a complete RISC-V simulation stack. The goal is to explore the trade-offs between hardware approximation, performance, and the perceptual quality (acceptability) of the final result.

---

## Core Architecture & Components

This benchmark environment have how to main components developed by the VArchC research group and the RISC-V community and STB repository.

* **1. Approximate Hardware Simulator:**
    * **Repo:** [VArchC/axpike-isa-sim](https://github.com/VArchC/axpike-isa-sim.git)

* **2. Proxy Kernel (OS Layer):**
    * **Repo:** [VArchC/axpike-pk](https://github.com/VArchC/axpike-pk.git)

* **3. Compiler Toolchain:**
    * **Repo:** [riscv-collab/riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain.git)


* **4. AxBench:**
    A. Yazdanbakhsh, D. Mahajan, P. Lotfi-Kamran, H. Esmaeilzadeh, "AXBENCH: A Multi-Platform Benchmark Suite for Approximate Computing", IEEE Design and Test, special issue on Computing in the Dark Silicon Era 2016.
---

## Setup & Installation

IF YOU WANT MAKE MANUALLY THE REQUISITES FOLLOW THE PATHS:

1.  **Build the Toolchain:**
   

2.  **Build the Proxy Kernel (PK):**
   

3.  **Build the Simulator (AxPike):**


SETUP AND INSTALATION AUTOMATIC: 



## How to Run the Benchmark


