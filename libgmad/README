-----

# Biblioteca gpu-memory-approxdata

Uma breve descrição do que esta biblioteca faz. Ex: "Uma biblioteca C++ para gerenciamento e manipulação de dados aproximados em memória de GPU."

## Pré-requisitos

Para compilar e utilizar esta biblioteca, você precisará de:

  * `g++` (compilador C++)
  * `make` (ferramenta de automação de compilação)
  * `ar` (ferramenta para criar arquivos estáticos, geralmente já vem com as ferramentas de compilação)

## Passo 1: Como Compilar a Biblioteca

Antes de usar a biblioteca em outros projetos, você precisa compilá-la. O processo gera um arquivo de biblioteca estática (`libgmad.a`).

1.  **Navegue até o diretório da biblioteca:**

    ```bash
    cd /caminho/para/sua/biblioteca/gpu-memory-approxdata
    ```

2.  **Execute o comando `make`:**

    ```bash
    make
    ```

Ao final do processo, você terá a biblioteca compilada em `build/libgmad.a` e os headers públicos disponíveis em `include/`.

## Passo 2: Como Usar a Biblioteca em um Projeto Externo

Depois que a `libgmad.a` foi gerada, você pode vinculá-la a qualquer um dos seus programas C++.

Imagine a seguinte estrutura de diretórios:

```
/home/usuario/dev/libs/gpu-memory-approxdata/  <-- Onde a biblioteca foi compilada
    ├── include/
    │   └── gmad.hpp
    └── build/
        └── libgmad.a

/home/usuario/dev/meu_projeto_incrivel/         <-- Seu novo projeto que usará a biblioteca
    └── main.cpp
```

Aqui está um exemplo de `main.cpp` que utiliza uma função da nossa biblioteca:

**`/home/usuario/dev/meu_projeto_incrivel/main.cpp`**

```cpp
#include <iostream>
#include "gmad.hpp" // Inclui o header da nossa biblioteca

int main() {
    // Supondo que sua biblioteca tenha uma função de exemplo como esta:
    gmad::initialize(); 

    std::cout << "Meu programa foi executado com sucesso usando a biblioteca gmad!" << std::endl;

    // Supondo que tenha uma função para finalizar:
    gmad::shutdown();

    return 0;
}
```

Para compilar o `main.cpp`, você tem duas opções:

-----

### Opção A: Compilando diretamente pela Linha de Comando

Você pode compilar seu programa passando os caminhos para os headers e para a biblioteca manualmente.

Abra o terminal no diretório do seu novo projeto (`/home/usuario/dev/meu_projeto_incrivel/`) e execute o comando abaixo, **substituindo o caminho de exemplo pelo caminho real** da sua biblioteca.

```bash
g++ main.cpp -I/home/usuario/dev/libs/gpu-memory-approxdata/include -L/home/usuario/dev/libs/gpu-memory-approxdata/build -lgmad -o meu_programa
```

**Entendendo o comando:**

  * `-I/caminho/para/include`: (`I` de "Include") Aponta para o diretório onde estão os arquivos de cabeçalho (`.hpp`).
  * `-L/caminho/para/build`: (`L` de "Library") Aponta para o diretório onde está o arquivo da biblioteca (`.a` ou `.so`).
  * `-lgmad`: Instrui o linker a procurar e vincular a biblioteca `libgmad.a`. O linker adiciona automaticamente o prefixo `lib` e o sufixo `.a`.

-----

### Opção B: Usando um Makefile (Recomendado)

Para projetos maiores ou para automatizar o processo, a melhor abordagem é criar um `Makefile` para o seu programa externo.

Crie um arquivo chamado `Makefile` dentro de `/home/usuario/dev/meu_projeto_incrivel/` com o seguinte conteúdo:

**`/home/usuario/dev/meu_projeto_incrivel/Makefile`**

```makefile
# Compilador
CXX = g++

# Flags de compilação
# Adiciona o diretório de headers da nossa biblioteca
CXXFLAGS = -Wall -Wextra -std=c++17

# Nome do executável final
EXECUTABLE = meu_programa

# === CONFIGURAÇÃO DA BIBLIOTECA GMAD ===
# Edite esta linha para apontar para o local onde você compilou a lib gmad
GMAD_PATH = /home/usuario/dev/libs/gpu-memory-approxdata

# Adiciona os caminhos de include e de biblioteca usando a variável acima
CXXFLAGS += -I$(GMAD_PATH)/include
LDFLAGS  = -L$(GMAD_PATH)/build -lgmad
# =======================================

# Arquivos fonte do seu projeto
SOURCES = main.cpp

# Regra principal para construir o executável
all: $(EXECUTABLE)

$(EXECUTABLE): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(EXECUTABLE) $(LDFLAGS)

# Regra para limpar os arquivos compilados
clean:
	rm -f $(EXECUTABLE)

```

**Como usar este Makefile:**

1.  **Ajuste a variável `GMAD_PATH`** para o caminho correto do seu projeto `gpu-memory-approxdata`.
2.  No terminal, dentro do diretório `/home/usuario/dev/meu_projeto/`, execute:
    ```bash
    make
    ```
3.  Para limpar os arquivos gerados, execute:
    ```bash
    make clean
    ```
