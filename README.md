# AxAccept-Bench
AxAccept-Bench is a benchmark developed to evaluate tolerance levels and the viability of hardware-level approximate computing. The infrastructure integrates two main components: the AxPIKE simulator, which enables controlled fault injection at the instruction level in RISC-V environments; and AxRAM, a resilient memory model that exploits application error tolerance to maximize energy savings. By simulating low-voltage operation through probabilistic models, the environment enables the quantification of the trade-off between structural data degradation and semantic validity within the application context, correlating these metrics with precise energy-gain estimations through integration with Ramulator and Vampire.
---

## Dependencies

- [axpike-isa-sim](https://github.com/VArchC/axpike-isa-sim.git) — Spike fork with approximate instruction support
- [axpike-pk](https://github.com/VArchC/axpike-pk.git) — proxy kernel for RISC-V execution
- [riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain.git) — cross-compiler toolchain

---

## Build

**riscv-gnu-toolchain** (example):
```bash
# this is an example — configure flags may vary for your system
$ sudo apt-get install autoconf automake autotools-dev curl python3 python3-pip python3-tomli libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build git cmake libglib2.0-dev libslirp-dev libncurses-dev
$ sudo mkdir -p /opt/riscv
$ ./configure --prefix=/opt/riscv
$ make
$ echo 'export PATH=$PATH:/opt/riscv/bin' >> ~/.bashrc
$ source ~/.bashrc
```

```bash
$ git clone --recursive https://github.com/your/AxAccept-Bench.git
```

**pk:**
```bash
$ cd axpike-pk 
$ mkdir build 
$ cd build
$ ../configure --prefix=$RISCV --host=riscv64-unknown-elf
$ make 
$ sudo make install
```

**AxPike:**
```bash
$ apt-get install device-tree-compiler libboost-regex-dev libboost-system-dev
$ mkdir build
$ cd build
$ ../configure --prefix=$RISCV
$ make -j
$ [sudo] make install
``` 
---

## Usage

See [applications/jpeg/usage.md](applications/jpeg/usage.md).