.PHONY: setup risc-v axpike-pk axpike-isa-sim

setup:
    git submodule update --init --recursive

risc-v:
    cd riscv-gnu-toolchain && \
    sudo apt-get install -y autoconf automake autotools-dev curl python3 python3-pip python3-tomli libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build git cmake libglib2.0-dev libslirp-dev && \
    sudo mkdir /opt/riscv && \
    ./configure --prefix=/opt/riscv && \
    make && \
    echo 'export PATH=$$PATH:/opt/riscv/bin' >> ~/.bashrc

axpike-pk:
    cd axpike-pk && \
    mkdir build && \
    cd build && \
    ../configure --prefix=$RISCV --host=riscv64-unknown-elf && \
    sudo make && \
    sudo make install 

axpike-isa-sim:
    cd axpike-isa-sim && \
    apt-get install device-tree-compiler libboost-regex-dev libboost-system-dev && \
    mkdir build && \
    cd build && \
    ../configure --prefix=$RISCV && \
    sudo make -j && \
    sudo make install && \
    



transformer da imagem 
python3 converter.py dataimage X.... embeddedimage.h


compilacao 

riscv64-unknown-elf-gcc -static -o teste compressor_completo_image.c -lm



execução

cat lena3.tif | axpike pk ./teste  90 2> saida_comprimida.jpg
ou 
axpike pk ./teste 40 < lena3.tif 1> saida.jpeg
