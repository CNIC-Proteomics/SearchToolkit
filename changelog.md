___
## 1.3

### Date 📅 *2025_01*

### Changes in detail

+ 'mz_extractor': Change *ProcessPoolExecutor* to *ThreadPoolExecutor*.

#### Difference Between `ThreadPoolExecutor` and `ProcessPoolExecutor`

The primary difference between `ThreadPoolExecutor` and `ProcessPoolExecutor` lies in how they handle parallelism and resource sharing.

#### Key Differences
| **Feature**               | **ThreadPoolExecutor**                                | **ProcessPoolExecutor**                              |
|---------------------------|-------------------------------------------------------|------------------------------------------------------|
| **Concurrency Model**      | Threads (same memory space)                           | Processes (separate memory spaces)                   |
| **Best for**               | I/O-bound tasks (e.g., file I/O, network calls)       | CPU-bound tasks (e.g., number crunching, heavy computations) |
| **Memory Sharing**         | Threads share memory (no need for IPC)                | Processes do not share memory (requires IPC)         |
| **Overhead**               | Lower overhead (less memory, faster startup)          | Higher overhead (more memory usage, slower startup)  |
| **Global Interpreter Lock (GIL)** | GIL can be a limiting factor in multi-threading    | No GIL restrictions (each process has its own Python interpreter) |
| **Synchronization Issues** | Needs careful synchronization to avoid race conditions | No shared memory, so no race conditions (but IPC is needed) |


___
## 1.2
```
DATE: 2024_12
```

### Changes in detail

+ Update the needed columns for MSFragger detection


___
## 1.1
```
DATE: 2024_11
```

### Highlights

+ Search Adaptation: Added a module that inserts the ScanID into search engine results.

### Changes in detail

+ Created a 'SearchToolkit' repository to house the 'mz_extractor' program and other tools that adapt search engine results.


___
## 1.0
```
DATE: 2024_01
```

### Highlights

Add the intensities into identification file from the mzML reporting the ion isotopic distribution.

Fixing a bug in the mz extraction for experiments with high resolution (greater than 30K), in the Quant package.

