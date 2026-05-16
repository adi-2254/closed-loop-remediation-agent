import streamlit as st
import subprocess
import os
import time
import pandas as pd

# ==========================================
# 1. ENTERPRISE PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Architecture Profiling Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. MODERN COLOR GRADING & CSS INJECTION
# ==========================================
# Inspired by ultra-modern developer tools (Vercel/Linear)
st.markdown("""
    <style>
    /* Global Background and Fonts */
    .stApp { background-color: #09090b; color: #fafafa; font-family: 'Inter', sans-serif; }
    
    /* Subtle Headers */
    h1, h2, h3 { font-weight: 600 !important; tracking: -0.02em; }
    
    /* Metric Cards (The dark boxes) */
    [data-testid="stMetric"] { 
        background-color: #18181b; 
        border: 1px solid #27272a; 
        padding: 24px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Green Delta Accent */
    [data-testid="stMetricDelta"] svg { display: none; } /* Hide default arrow */
    [data-testid="stMetricDelta"] { color: #10b981 !important; font-weight: 600; font-size: 1.1rem;}
    
    /* Primary Action Button */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #fafafa; 
        color: #09090b; 
        font-weight: 600; 
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background-color: #e4e4e7; transform: translateY(-1px); }
    
    /* Expander Styling */
    .streamlit-expanderHeader { background-color: #18181b; border-radius: 8px; border: 1px solid #27272a; }
    
    /* Hide standard Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CORE DATA PARSERS
# ==========================================
def parse_trace_data(trace_path):
    data = []
    if not os.path.exists(trace_path) or os.path.getsize(trace_path) == 0: return data
    try:
        with open(trace_path, 'r') as f:
            lines = f.readlines()
            start = 0
            for i, line in enumerate(lines):
                if "---" in line:
                    start = i + 1
                    break
            for line in lines[start:]:
                if "===" in line or not line.strip(): break
                parts = line.split()
                if len(parts) >= 3:
                    count = int(parts[0])
                    func = parts[-1].lstrip('%')
                    data.append({"Function": func, "Instructions": count})
    except: pass
    return data

def generate_differential_matrix(orig_data, opt_data):
    if not orig_data or not opt_data: return pd.DataFrame()
    
    opt_dict = {d["Function"]: d["Instructions"] for d in opt_data}
    matrix = []
    
    for d in orig_data:
        func = d["Function"]
        orig_count = d["Instructions"]
        opt_count = opt_dict.get(func, 0) 
        reduction = orig_count - opt_count
        pct = (reduction / orig_count * 100) if orig_count > 0 else 0.0
        
        matrix.append({
            "Function Core": func,
            "Baseline (Inst)": orig_count,
            "Optimized (Inst)": opt_count,
            "Delta (Δ)": reduction,
            "Reduction %": pct
        })
        
    df = pd.DataFrame(matrix)
    df = df.sort_values(by="Delta (Δ)", ascending=False)
    return df

def run_pipeline(benchmarks):
    cmd = ["python3", "run_pipeline.py", "--benchmarks"] + benchmarks
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log_placeholder = st.empty()
    full_log = ""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None: break
        if output:
            full_log += output
            log_placeholder.code(full_log)
    return process.poll()

# ==========================================
# 4. SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Engine Config")
    st.markdown("<span style='color: #a1a1aa; font-size: 0.9rem;'>Target Workloads</span>", unsafe_allow_html=True)
    available_benchmarks = ["bench_string_search", "bench_jpeg_dct", "bench_qsort", "bench_matrix_mul", "bench_sha", "bench_fft"]
    selected_benchmarks = st.multiselect("", options=available_benchmarks, default=["bench_string_search"], label_visibility="collapsed")
    
    st.markdown("<br><span style='color: #a1a1aa; font-size: 0.9rem;'>OpenAI API Key</span>", unsafe_allow_html=True)
    api_key = st.text_input("", type="password", value=os.getenv("OPENAI_API_KEY", ""), label_visibility="collapsed")
    
    st.markdown("---")
    st.caption("Architecture Profiling Pipeline v2.1\nPowered by Intel Pin & GPT-4o")

# ==========================================
# 5. MAIN DASHBOARD UI
# ==========================================
st.markdown("## ⚡ Profiling & Remediation Engine")
st.markdown("<p style='color: #a1a1aa; margin-bottom: 2rem;'>Automated dynamic instrumentation and AI-driven algorithmic optimization.</p>", unsafe_allow_html=True)

col_ctrl, col_dash = st.columns([1, 3])

# -- CONTROL CENTER --
with col_ctrl:
    st.markdown("#### Execution")
    if st.button("Initialize Pipeline"):
        if not api_key: st.error("API Key required.")
        else:
            os.environ["OPENAI_API_KEY"] = api_key
            with st.status("Executing Multi-Pass Pipeline...", expanded=True):
                run_pipeline(selected_benchmarks)
            st.success("Telemetry Synced.")
            time.sleep(1.5)
            st.rerun()

# -- TELEMETRY DASHBOARD --
with col_dash:
    st.markdown("#### Performance Telemetry")
    if not selected_benchmarks: st.info("Select a workload from the sidebar.")
    
    for bench in selected_benchmarks:
        res_path = f"results/{bench}"
        orig_trace = os.path.join(res_path, "trace.out")
        opt_trace = os.path.join(res_path, "trace_optimized.out")
        comp_log = os.path.join(res_path, "compilation_log.txt")
        
        orig_data = parse_trace_data(orig_trace)
        opt_data = parse_trace_data(opt_trace)
        
        with st.expander(f"Workload: {bench}", expanded=True):
            if orig_data:
                old_total = sum(d['Instructions'] for d in orig_data)
                new_total = sum(d['Instructions'] for d in opt_data) if opt_data else 0
                
                # TOP METRICS ROW
                m1, m2, m3 = st.columns(3)
                m1.metric("Critical Bottleneck", orig_data[0]["Function"])
                m2.metric("Baseline Execution Cost", f"{old_total:,}")
                
                if opt_data and new_total > 0:
                    delta = ((old_total - new_total) / old_total) * 100
                    m3.metric("System Optimization Delta", f"-{delta:.2f}%", f"↓ {old_total - new_total:,} inst")
                elif os.path.exists(comp_log):
                    m3.error("Validation Failed")
                else:
                    m3.warning("Awaiting Validation")

                st.markdown("<br>", unsafe_allow_html=True)
                
                # DATA TABS
                tab_matrix, tab_report, tab_health = st.tabs([
                    "Differential Matrix", 
                    "AI Architecture Report", 
                    "System Health"
                ])
                
                with tab_matrix:
                    if opt_data:
                        df = generate_differential_matrix(orig_data, opt_data)
                        st.dataframe(
                            df, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "Baseline (Inst)": st.column_config.NumberColumn(format="%d"),
                                "Optimized (Inst)": st.column_config.NumberColumn(format="%d"),
                                "Delta (Δ)": st.column_config.NumberColumn(format="%d"),
                                "Reduction %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)
                            }
                        )
                    else:
                        st.info("Complete a validation pass to generate the differential matrix.")

                with tab_report:
                    report = os.path.join(res_path, "ai_patch_report.md")
                    if os.path.exists(report):
                        with open(report, "r") as f: st.markdown(f.read())
                    else:
                        st.info("No AI report available.")
                
                with tab_health:
                    if os.path.exists(comp_log):
                        st.error("AI Compilation Error Detected:")
                        with open(comp_log, "r") as f: st.code(f.read(), language="bash")
                    else:
                        st.success("System integrity verified. Zero compilation faults.")
            else:
                st.info("Initialize the pipeline to generate baseline telemetry.")