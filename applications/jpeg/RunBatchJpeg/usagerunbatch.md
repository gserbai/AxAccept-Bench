# Running in batch-Jpeg 

## Single Execution

You can run a single execution of the JPEG encoder through AxPike:

```bash
axpike --adele=mem_read_prob:1.4e-1,linesz:32 \
       --adele-activate=0:AXRAM \
       --dc=128:8:32 \
       --ic=256:4:32 \
       --l2=1024:4:32 \
       pk ./applications/jpeg/src/toojpeg_encoder 100 < input.csv > output.jpeg
```

This command:

1. Executes the JPEG encoder
2. Injects memory approximation faults
3. Produces a JPEG image as output

---

# Approximation Parameters

Approximation is controlled through the `--adele` parameter.

Example:

```
--adele=mem_read_prob:1.4e-1,linesz:32
```

Parameter description:

| Parameter     | Description                                     |
| ------------- | ----------------------------------------------- |
| mem_read_prob | Probability of memory read approximation        |
| linesz        | Cache line size used by the approximation model |

Examples of error configurations variable with size image in relation memory:

```
1e-2   → Low approximation
1e-1   → Medium approximation
1.4e-1 → Higher approximation
```

Each configuration can generate a **different experimental dataset**.

---

# Batch Execution

To process a large dataset automatically, use one of the batch scripts.

## Python Batch Script

Run:

```bash
python axaccept_batch.py
```

The script will:

1. Search for `.csv` files inside:

```
src/dataset_csv/
```

2. Execute the JPEG encoder through AxPike for each file.

3. Store generated images in:

```
src/dataset_error_rate_1.4e-1/
```

The folder structure of the dataset is preserved during execution. 

---

## Shell Batch Script

Alternatively, you can use the shell script:

```bash
bash axaccept_batch.sh
```

This script recursively scans the dataset directory and executes the simulator for each input image. 

---

# Changing the Approximation Error Rate

To evaluate different approximation levels, modify the parameter:

```
mem_read_prob
```

Example:

```
--adele=mem_read_prob:1e-2
--adele=mem_read_prob:1e-1
--adele=mem_read_prob:1.4e-1
```



