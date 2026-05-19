# AxAccept-Bench

Benchmark suite for evaluating acceptability of approximate computing techniques.
Tests approximation parameters using a RISC-V simulation stack, measuring
trade-offs between energy, performance, and output quality via neural network
acceptability analysis.

---

## Dependencies

- [axpike-isa-sim](https://github.com/VArchC/axpike-isa-sim.git) — Spike fork with approximate instruction support
- [axpike-pk](https://github.com/VArchC/axpike-pk.git) — proxy kernel for RISC-V execution
- [riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain.git) — cross-compiler toolchain
- ResNet-50 — He et al., Deep Residual Learning for Image Recognition, CVPR 2016

---

## Build

**riscv-gnu-toolchain** (example):
```bash
# this is an example — configure flags may vary for your system
sudo mkdir -p /opt/riscv
./configure --prefix=/opt/riscv
make
echo 'export PATH=$PATH:/opt/riscv/bin' >> ~/.bashrc
source ~/.bashrc
```

```bash
git clone --recursive https://github.com/your/AxAccept-Bench.git
```

**pk:**
```bash
cd axpike-pk && mkdir build && cd build
../configure --prefix=$RISCV --host=riscv64-unknown-elf
make && sudo make install
```

**AxPike:**
```bash
cd axpike-isa-sim && mkdir build && cd build
../configure --prefix=$RISCV
make -j && sudo make install
```

---

## Usage

See [applications/jpeg/usage.md](applications/jpeg/usage.md).