# Formato de Entrada do JPEG Encoder

## Resposta Direta

**Sua aplicação JPEG NÃO aceita BMP diretamente!**

Ela aceita um **formato CSV/texto customizado**.

---

## Formato Aceito

### Estrutura

```
<largura>,<altura>
<r1>,<g1>,<b1>,<r2>,<g2>,<b2>,...,<rN>,<gN>,<bN>
<r1>,<g1>,<b1>,<r2>,<g2>,<b2>,...,<rN>,<gN>,<bN>
...
<r1>,<g1>,<b1>,<r2>,<g2>,<b2>,...,<rN>,<gN>,<bN>
<metadata>
```

### Partes

1. **Linha 1**: `<largura>,<altura>` — dimensões em pixels
2. **Linhas 2 a (altura+1)**: RGB de cada pixel, separados por vírgula
   - Cada pixel = `<R>,<G>,<B>` (valores 0-255)
   - Cada linha tem `largura * 3` valores (RGB para cada pixel)
3. **Última linha**: metadata (texto qualquer, ex: "BMP")

### Exemplo (2×2 pixels)

```
2,2
255,0,0,0,255,0
0,0,255,255,255,0
BMP
```

Isto representa:
```
Linha 1: [vermelho (255,0,0)]    [verde (0,255,0)]
Linha 2: [azul (0,0,255)]        [amarelo (255,255,0)]
```

---

## Restrições

### De Entrada

| Restrição | Valor | Notas |
|-----------|-------|-------|
| Formato | CSV texto | Separador: `,` e `\n` |
| Valores RGB | 0-255 | Inteiros |
| Dimensões | Qualquer | Serão ajustadas para múltiplo de 8 |
| Espaços | Ignorados (fora de quoted strings) | `readCell()` pula espaços/tabs |

### De Processamento

```c
image->w = (image->w / 8) * 8;  // Ajusta largura para múltiplo de 8
image->h = (image->h / 8) * 8;  // Ajusta altura para múltiplo de 8
```

Se você passar 513×513, será processado como 512×512 (descarta bordas).

---

## Conversão: BMP → CSV

Use o script `bmp_to_csv_nopil.py`:

```bash
python3 bmp_to_csv_nopil.py input.bmp output.csv
```

Isto lê BMP (8-bit ou 24-bit) e escreve no formato CSV aceito.

---

## Como Usar

### Pipeline (Recomendado)

```bash
python3 bmp_to_csv_nopil.py imagem.bmp | axpike pk ./teste 90 1> saida.jpg 2> logs.txt
```

### Com Arquivo Intermediário

```bash
# Gerar CSV
python3 bmp_to_csv_nopil.py imagem.bmp imagem.csv

# Usar CSV
cat imagem.csv | axpike pk ./teste 90 1> saida.jpg 2> logs.txt
```

---

## Limitações e Observações

1. **Formato texto**: Muito maior que binário
   - BMP 512×512: ~1.5 MB
   - CSV equivalente: ~5-6 MB (3× maior)
   
2. **Conversão de cor**: O encoder converte para escala de cinza (Y)
   - Mesmo que passe RGB, será processado em cinza
   
3. **Valores inválidos**: Se não for número válido, `atoi()` retorna 0
   
4. **Sem validação strict**: Se passar valores > 255, não há erro (comportamento undefined)

---

## Checklist: O que Você Precisa Passar

- ✅ Arquivo em formato CSV (ou gerar via `bmp_to_csv_nopil.py`)
- ✅ Primeira linha: `largura,altura`
- ✅ Próximas `altura` linhas: RGB de cada pixel (separados por vírgula)
- ✅ Última linha: metadata (qualquer texto)
- ✅ Valores RGB: 0-255
- ✅ Enviar via stdin (pipe ou redireccionamento)

---

## Resumo

| Item | Suportado | Detalhes |
|------|-----------|----------|
| BMP | ❌ Nativo | Use `bmp_to_csv_nopil.py` para converter |
| PNG | ❌ Nativo | Use `bmp_to_csv_nopil.py` (requer PIL ou converter antes) |
| TIFF | ❌ Nativo | Use `bmp_to_csv_nopil.py` (requer PIL ou converter antes) |
| CSV Customizado | ✅ Nativo | Formato exato documentado acima |
| Entrada stdin | ✅ Nativo | Lê direto de stdin |
| Saída stdout | ✅ Nativo | Escreve JPEG em stdout |

---

**Conclusão**: Sua aplicação aceita **apenas CSV customizado**, não BMP diretamente. Use o conversor Python fornecido.
