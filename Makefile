.PHONY: setup axpike-pk axpike-isa-sim

setup:
    git submodule update --init --recursive

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
    



