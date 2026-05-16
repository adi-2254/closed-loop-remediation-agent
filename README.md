# Autonomous Systems Profiler ⚡

An automated, closed-loop agent that bridges the gap between binary-level execution and source-level algorithmic remediation. Designed to dynamically profile C/C++ binaries, surgically extract bottleneck functions, and autonomously optimize algorithmic complexity using Large Language Models (LLMs).

**Developed by:** Aditya Raj & Aakash Jaisinghani  
**Supervised by:** Prof. Neeraj Goel  

---

## 📖 Overview

Standard compilers rely on static heuristics (e.g., `-O3`) that optimize instruction scheduling but fail to resolve fundamental algorithmic inefficiencies (e.g., executing an $O(N^2)$ algorithm instead of $O(N \log N)$). 

This project introduces a **Zero-Trust Autonomous Agent** that:
1. **Profiles** execution at the instruction level using dynamic binary instrumentation (Intel Pin).
2. **Extracts** the bottleneck function from the source code deterministically using an Abstract Syntax Tree (AST).
3. **Remediates** the algorithm using GPT-4o to achieve lower time complexity.
4. **Validates** the optimization by recompiling and re-profiling the patched binary to mathematically prove the instruction reduction.

Tested and proven against industry-standard **MiBench** workloads (String Search, Bitwise Operations, Matrix Mathematics, and Signal Processing).

---

## ✨ Key Features

* **Dynamic Binary Instrumentation:** Uses Intel Pin to bypass statistical sampling errors (unlike `gprof`), capturing a bit-accurate execution weight of every function.
* **AST Surgical Isolation:** Utilizes `pycparser` to parse C grammar and extract targeted functions safely, avoiding the pitfalls of regular expression boundary matching.
* **Autonomous Feedback Loop:** Implements a strict validation gate. If an AI patch fails to compile or degrades performance, the system rejects it and triggers a self-refinement retry.
* **Enterprise Telemetry Dashboard:** A sleek, dark-mode Streamlit UI that visualizes the AI architecture reports and generates a Differential Matrix comparing baseline vs. optimized instruction counts.

---

## ⚙️ Architecture Data Flow

1. **`run_pipeline.py`** compiles the baseline binary (`-O0` to isolate algorithmic logic).
2. **`MyPinTool.so`** instruments the binary during runtime, generating a `trace.out` profile.
3. **`analyzer.py`** parses the trace to identify the heaviest CPU bottleneck.
4. **`auto_extractor.py`** builds an AST, extracts the bottleneck, queries the OpenAI API for an algorithmic rewrite, and splices the new code into `[benchmark]_OPTIMIZED.c`.
5. The pipeline re-compiles the optimized code and runs a secondary validation trace (`trace_optimized.out`).
6. **`app.py`** renders the UI, calculating the exact performance delta (Δ).

---

## 🛠️ Prerequisites & Dependencies

### System Requirements
* **OS:** Linux (Ubuntu 20.04/22.04 recommended)
* **Compiler:** `gcc` and `g++`
* **Intel Pin:** [Download Intel Pin](https://software.intel.com/content/www/us/en/develop/articles/pin-a-dynamic-binary-instrumentation-tool.html) (Ensure the `PIN_ROOT` environment variable is set or the path is correctly mapped in `run_pipeline.py`).

### Python Packages
Requires **Python 3.8+**. Install the necessary pip packages:

```bash
pip install streamlit pandas openai pycparser
