#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import time

# ── Project paths ──
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR   = os.path.join(SCRIPT_DIR, "benchmarks")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
PIN_TOOL    = os.path.join(SCRIPT_DIR, "obj-intel64", "MyPinTool.so")
PIN_EXE     = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", "pin"))

BENCHMARKS = {
    "bench_string_search": ("bench_string_search.c", []),
    "bench_qsort":         ("bench_qsort.c",         []),
    "bench_matrix_mul":    ("bench_matrix_mul.c",    []),
    "bench_sha":           ("bench_sha.c",           []),
    "bench_bitcount":      ("bench_bitcount.c",      []),
    "bench_fft":           ("bench_fft.c",           ["-lm"]),
    "bench_jpeg_dct":      ("bench_jpeg_dct.c",      ["-lm"]),
}

def banner(text, char="═", width=85):
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")

def run_cmd(cmd, label, cwd=None):
    print(f"  $ {' '.join(cmd)}")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=cwd or SCRIPT_DIR, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            print(f"    {line}")
    if result.returncode != 0:
        print(f"  ✗ {label} FAILED (exit code {result.returncode})")
        if result.stderr.strip():
            for line in result.stderr.strip().split('\n'):
                print(f"    [stderr] {line}")
        return False, elapsed
    return True, elapsed

def step_compile(bench_name, source_file, extra_flags, out_dir):
    src = os.path.join(BENCH_DIR, source_file)
    binary = os.path.join(out_dir, bench_name)
    if not os.path.exists(src):
        return None
    cmd = ["gcc", "-O0", "-g", "-o", binary, src] + extra_flags
    ok, _ = run_cmd(cmd, "Compilation")
    return binary if ok else None

def step_pin_profile(binary, trace_out):
    if not os.path.exists(PIN_EXE) or not os.path.exists(PIN_TOOL):
        return False
    cmd = [PIN_EXE, "-t", PIN_TOOL, "-o", trace_out, "--", binary]
    ok, _ = run_cmd(cmd, "PIN Profiling")
    return ok

def step_analyzer(trace_file, bench_name, top_n, out_dir):
    report_path = os.path.join(out_dir, "ai_report.md")
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, "analyzer.py"), "-t", trace_file, "-n", str(top_n), "-b", bench_name, "-o", report_path]
    ok, _ = run_cmd(cmd, "Analyzer")
    return ok

def step_auto_extractor(trace_file, source_file, bench_name, out_dir):
    src = os.path.join(BENCH_DIR, source_file)
    optimized = os.path.join(out_dir, f"{bench_name}_OPTIMIZED.c")
    report = os.path.join(out_dir, "ai_patch_report.md")
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, "auto_extractor.py"), "-t", trace_file, "-s", src, "-o", optimized, "-r", report]
    ok, _ = run_cmd(cmd, "Auto-Extractor")
    return ok

def step_validate(bench_name, extra_flags, out_dir):
    """Profiles the AI-optimized code and captures errors for the UI."""
    opt_src = os.path.join(out_dir, f"{bench_name}_OPTIMIZED.c")
    opt_bin = os.path.join(out_dir, f"{bench_name}_opt_bin")
    opt_trace = os.path.join(out_dir, "trace_optimized.out")
    log_file = os.path.join(out_dir, "compilation_log.txt")

    if not os.path.exists(opt_src): return False

    # Compile and capture stderr to a file
    cmd_compile = ["gcc", "-O0", "-g", "-o", opt_bin, opt_src] + extra_flags
    result = subprocess.run(cmd_compile, capture_output=True, text=True)
    
    if result.returncode != 0:
        with open(log_file, "w") as f:
            f.write(result.stderr) # Save the error for the UI to show
        print(f"  ✗ Compilation of Optimized Code FAILED.")
        return False
    
    # If successful, remove old logs and profile
    if os.path.exists(log_file): os.remove(log_file)
    cmd_pin = [PIN_EXE, "-t", PIN_TOOL, "-o", opt_trace, "--", opt_bin]
    ok_pin, _ = run_cmd(cmd_pin, "Profiling Optimized Binary")
    return ok_pin

def print_summary(results):
    banner("PIPELINE SUMMARY", "━")
    print(f"  {'Benchmark':<25} {'Compile':>9} {'PIN':>9} {'Analyzer':>9} {'Patch':>9} {'Validate':>9}")
    print(f"  {'─' * 25} {'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9}")
    for name, statuses in results.items():
        row = f"  {name:<25}"
        for step in ["compile", "pin", "analyzer", "extractor", "validate"]:
            status = statuses.get(step, "skip")
            if status == "ok": icon = "  ✅"
            elif status == "fail": icon = "  ❌"
            elif status == "skip": icon = "  ⏭️ "
            else: icon = "  ❓"
            row += f"{icon:>9}"
        print(row)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmarks", nargs="*", default=None)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--skip-pin", action="store_true")
    parser.add_argument("--skip-ai", action="store_true")
    args = parser.parse_args()

    selected = args.benchmarks if args.benchmarks else list(BENCHMARKS.keys())
    results = {}

    for bench_name in selected:
        if bench_name not in BENCHMARKS: continue
        source_file, extra_flags = BENCHMARKS[bench_name]
        out_dir = os.path.join(RESULTS_DIR, bench_name)
        os.makedirs(out_dir, exist_ok=True)
        trace_file = os.path.join(out_dir, "trace.out")

        banner(f"Benchmark: {bench_name}", "─")
        status = {}

        if not args.skip_pin:
            binary = step_compile(bench_name, source_file, extra_flags, out_dir)
            status["compile"] = "ok" if binary else "fail"
            if binary:
                ok = step_pin_profile(binary, trace_file)
                status["pin"] = "ok" if ok else "fail"
        else:
            status["compile"] = "skip"
            status["pin"] = "skip"

        if not args.skip_ai and status.get("pin", "skip") in ["ok", "skip"]:
            ok1 = step_analyzer(trace_file, bench_name, args.top, out_dir)
            status["analyzer"] = "ok" if ok1 else "fail"
            
            ok2 = step_auto_extractor(trace_file, source_file, bench_name, out_dir)
            status["extractor"] = "ok" if ok2 else "fail"
            
            # New Validation Pass
            if ok2:
                print("\n  🧪 Step 5: Validating Optimization (Re-profiling)...")
                ok3 = step_validate(bench_name, extra_flags, out_dir)
                status["validate"] = "ok" if ok3 else "fail"
            else:
                status["validate"] = "skip"
        else:
            status["analyzer"] = "skip"
            status["extractor"] = "skip"
            status["validate"] = "skip"

        results[bench_name] = status

    print_summary(results)

if __name__ == "__main__":
    main()