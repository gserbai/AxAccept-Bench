# AUDITORIA BARE METAL - JPEG/src

## Conclusão: ✅ 100% BARE METAL COMPATIBLE

Seu código JPEG/src está completamente pronto para rodar em ambiente bare metal sem dependências de filesystem (fopen/fclose).

---

## Análise Detalhada

### 1. **jpeg.c** ✅ PERFEITO
- ✅ **Entrada**: `loadRgbImageFromStream(stdin, &srcImage)` — lê DIRETAMENTE de stdin
- ✅ **Saída**: Loop com `putchar()` escreve DIRETAMENTE em stdout
- ✅ **Logs**: `fprintf(stderr, ...)` envia mensagens para stderr
- ✅ **Sem fopen/fclose**: Nenhuma operação de arquivo
- ✅ **Bufferização controlada**: `setvbuf(stdout, NULL, _IONBF, 0)` desativa buffer

```c
// Stdin:
loadRgbImageFromStream(stdin, &srcImage)

// Stdout (JPEG bytes):
for (long i = 0; i < bytesEscritos; i++) {
    putchar(outputBuffer[i]);
}

// Stderr (logs):
fprintf(stderr, "Usando qualidade %d/100...\n", ...);
```

---

### 2. **rgbimage.c** ✅ SAFE (sem fopen)
- ✅ `loadRgbImageFromStream(FILE* stream, ...)` — recebe `stdin` como parâmetro
- ✅ `readCell(FILE *fp, ...)` — usa apenas `fgetc(fp)` do stream passado
- ✅ `saveRgbImageToStream(FILE* stream, ...)` — não é usado no main (apenas stdout via putchar)
- ✅ **Sem fopen/fclose**: Apenas manipula streams passados
- ✅ `malloc/free` — OK para bare metal com heap disponível

Fluxo:
```c
fp = stream;  // fp = stdin (passado do main)
c = readCell(fp, w);  // lê de stdin
```

---

### 3. **quant.c** ✅ SEGURO
- ✅ `extern FILE*` está DENTRO de `#ifdef RANDOM_DATA_COLLECTION`
- ✅ NÃO é compilado por padrão (compilador ignora)
- ✅ Sem impacto para bare metal

```c
#ifdef RANDOM_DATA_COLLECTION
	extern FILE* dct_data ;           // ← Não compilado
	extern FILE* quantization_data ;  // ← Não compilado
#endif
```

---

### 4. **Outros Arquivos (.c)** ✅ LIMPOS
- **dct.c**: Apenas computações matemáticas
- **encoder.c**: Apenas processamento de dados em buffer
- **huffman.c**: Apenas processamento de dados em buffer
- **marker.c**: Apenas geração de headers em buffer

Resultado grep para `fopen|fclose|FILE*`:
```
0 matches em: dct.c, encoder.c, huffman.c, marker.c
```

---

### 5. **Headers (.h)** ✅ LIMPOS
Nenhuma declaração de `fopen`, `fclose`, ou I/O de arquivo.

---

## Fluxo de Dados (Bare Metal)

```
stdin (CSV format)
  ↓
readCell() + fgetc()   [rgbimage.c]
  ↓
loadRgbImageFromStream()  [rgbimage.c]
  ↓
makeGrayscale()  [rgbimage.c]
  ↓
encodeImage()  [encoder.c]
  → dct() [dct.c]
  → quantization() [quant.c]
  → huffman() [huffman.c]
  → writeMarkers() [marker.c]
  ↓
outputBuffer (RAM)
  ↓
putchar() loop  [jpeg.c]
  ↓
stdout (JPEG bytes)
```

---

## Checklist Final

| Item | Status | Notas |
|------|--------|-------|
| `fopen` | ✅ Nenhum | |
| `fclose` | ✅ Nenhum | |
| `fwrite` | ✅ Trocado por `putchar()` loop | |
| `fread` | ✅ Nenhum | |
| `FILE*` não-ifdef | ✅ Apenas parâmetros (stdin) | |
| stdin | ✅ Usado via `loadRgbImageFromStream(stdin, ...)` | |
| stdout | ✅ Usado via `putchar()` loop | |
| stderr | ✅ Usado via `fprintf(stderr, ...)` | |
| malloc/free | ✅ OK | Adequado para bare metal com heap |
| setvbuf | ✅ Desativa buffer | Melhor para bare metal |

---

## Como Rodar

### Local (com axpike pk):
```bash
cd /home/guilherme/AxAccept-Bench/JPEG/src
riscv64-unknown-elf-gcc -static -o teste *.c -lm
python3 ../bmp_to_csv_nopil.py ../imagesTest/lena_gray.bmp | axpike pk ./teste 90 1> saida.jpg 2> logs.txt
```

### Bare Metal (sem axpike):
```bash
# Seu bootloader/kernel faz:
stdin_redirect("image.csv");    // redireciona stdin
stdout_redirect("output.jpg");  // redireciona stdout
stderr_redirect("debug.txt");   // redireciona stderr
run_program("teste", "90");     // executa teste 90
```

---

## Conclusão

✅ **Seu código JPEG/src está 100% pronto para bare metal!**

- Sem dependências de filesystem
- Sem `fopen/fclose/fread/fwrite`
- Entrada via stdin
- Saída via stdout
- Logs via stderr
- Totalmente portável para RISC-V bare metal

**Pronto para submeter no AxAccept-Bench!** 🚀

---

Criado: 15 de dezembro de 2025
