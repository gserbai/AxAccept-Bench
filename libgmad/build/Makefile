# Nome da biblioteca e programa
LIB_NAME = gmad
PROGRAM = main_program

# Compilador e flags
CXX = g++
CXXFLAGS = -Iinclude -Wall -O2 -std=c++17
LDFLAGS = -Lbuild -l$(LIB_NAME)

# Arquivos
SRC = src/$(LIB_NAME).cpp
OBJ = build/$(LIB_NAME).o
MAIN = main.cpp

# Targets principais
all: static dynamic run

# Compila objeto da biblioteca
$(OBJ): $(SRC)
	mkdir -p build
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Biblioteca estática (.a)
static: $(OBJ)
	ar rcs build/lib$(LIB_NAME).a $(OBJ)
	@echo "Biblioteca estática criada: build/lib$(LIB_NAME).a"

# Biblioteca dinâmica (.so)
dynamic: $(OBJ)
	$(CXX) -shared -fPIC $(OBJ) -o build/lib$(LIB_NAME).so
	@echo "Biblioteca dinâmica criada: build/lib$(LIB_NAME).so"

# Compila programa de teste e roda
run: static
	$(CXX) $(CXXFLAGS) $(MAIN) -Lbuild -l$(LIB_NAME) -o $(PROGRAM)
	@echo "Executando o programa de teste..."
	./$(PROGRAM)

# Limpeza
clean:
	rm -rf build/* $(PROGRAM)
	@echo "Arquivos compilados removidos."
