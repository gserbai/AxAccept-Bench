.PHONY: setup axpike-pk axpike-isa-sim


RISCV_PATH = /opt/riscv

setup:
	git submodule update --init --recursive

axpike-pk:
	cd axpike-pk && \
	mkdir -p build && \
	cd build && \
	../configure --prefix=$(RISCV_PATH) --host=riscv64-unknown-elf && \
	make && \
	make install 


axpike-isa-sim:
	cd axpike-isa-sim && \
	sudo dnf install -y dtc boost-devel && \
	mkdir -p build && \
	cd build && \
	../configure --prefix=$(RISCV_PATH) && \
	make -j$$(nproc) && \
	make install