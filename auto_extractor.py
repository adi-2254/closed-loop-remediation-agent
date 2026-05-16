import os
import re
import sys
import argparse
from openai import OpenAI

try:
    from pycparser import c_parser, c_ast, c_generator
    HAS_PYCPARSER = True
except ImportError:
    HAS_PYCPARSER = False

def parse_trace_candidates(trace_file, max_candidates=20):
    if not os.path.exists(trace_file): return []
    with open(trace_file, 'r') as f:
        lines = f.readlines()
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("---------"):
            start_idx = i + 1
            break
    SKIP_PREFIXES = ('_', '.', '__')
    SKIP_SUBSTRINGS = ('xsub', 'xmul', 'xadd', 'xdiv', 'f64x', 'f32x', 'sincosf', 'sincosdf', 'sincosl')
    candidates = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("====="): break
        parts = stripped.split()
        if len(parts) < 3: continue
        func_name = parts[-1]
        if func_name == '%': continue
        if func_name.startswith('%'): func_name = func_name[1:]
        if any(func_name.startswith(p) for p in SKIP_PREFIXES): continue
        if any(s in func_name for s in SKIP_SUBSTRINGS): continue
        candidates.append(func_name)
        if len(candidates) >= max_candidates: break
    return candidates

def find_best_bottleneck(trace_file, source_file):
    candidates = parse_trace_candidates(trace_file)
    if not candidates: return None
    with open(source_file, 'r') as f:
        source_text = f.read()
    for name in candidates:
        pattern = re.compile(r'\b' + re.escape(name) + r'\s*\([^)]*\)\s*\{', re.DOTALL)
        if pattern.search(source_text): return name
    return candidates[0]

def _clean_c_for_pycparser(input_file, temp_file):
    with open(input_file, 'r') as f: code = f.read()
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'^\s*#.*$', '', code, flags=re.MULTILINE)
    with open(temp_file, 'w') as f: f.write(code)

def _extract_via_ast(source_file, target_func):
    temp_file = source_file + ".tmp_ast.c"
    try:
        _clean_c_for_pycparser(source_file, temp_file)
        parser = c_parser.CParser()
        with open(temp_file, 'r') as f:
            ast = parser.parse(f.read(), filename='<none>')
        class FuncVisitor(c_ast.NodeVisitor):
            def __init__(self): self.target_node = None
            def visit_FuncDef(self, node):
                if node.decl.name == target_func: self.target_node = node
        visitor = FuncVisitor()
        visitor.visit(ast)
        if visitor.target_node:
            gen = c_generator.CGenerator()
            return gen.visit(visitor.target_node)
    except Exception:
        pass
    finally:
        if os.path.exists(temp_file): os.remove(temp_file)
    return None

def _extract_via_regex(source_file, target_func):
    with open(source_file, 'r') as f: source = f.read()
    pattern = re.compile(r'((?:[\w\s\*]+)\b' + re.escape(target_func) + r'\s*\([^)]*\)\s*\{)', re.DOTALL)
    match = pattern.search(source)
    if not match: return None
    start = match.start()
    brace_count = 0
    idx = match.end() - 1
    for i in range(idx, len(source)):
        if source[i] == '{': brace_count += 1
        elif source[i] == '}':
            brace_count -= 1
            if brace_count == 0: return source[start:i+1]
    return None

def extract_function_source(source_file, target_func):
    if HAS_PYCPARSER:
        code = _extract_via_ast(source_file, target_func)
        if code: return code
    return _extract_via_regex(source_file, target_func)

def get_ai_optimization(func_name, source_code):
    client = OpenAI()
    prompt = (
        f"Optimize this C function identified as a CPU bottleneck: `{func_name}`.\n\n"
        f"```c\n{source_code}\n```\n\n"
        f"Provide algorithmic diagnosis and an optimized C replacement using identical signature.\n"
        f"STRICT RULE: Do not include ANY tutorial comments, inline explanations, or filler text within the generated C code block. Output only clean, minimal logic."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Return optimized C code in fenced blocks. Act as a senior systems architect."}, 
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {e}"

def apply_ai_patch(source_file, output_file, target_func, ai_report):
    # Regex to capture the C code block from the markdown report securely
    matches = re.findall(r'```(?:[cC])?\s*\n(.*?)```', ai_report, re.DOTALL)
    if not matches:
        print(f"  [Auto-Extractor] ERROR: No valid C code block found in AI report.")
        return False
        
    new_code = matches[-1].strip()
    
    with open(source_file, 'r') as f: lines = f.readlines()
    start_line, end_line, brace_count, found_first_brace = -1, -1, 0, False
    
    for i, line in enumerate(lines):
        if target_func in line and "(" in line and ";" not in line:
            if start_line == -1: start_line = i
        if start_line != -1 and end_line == -1:
            brace_count += line.count('{') - line.count('}')
            if '{' in line: found_first_brace = True
            if found_first_brace and brace_count == 0:
                end_line = i
                break
                
    if start_line == -1 or end_line == -1:
        print(f"  [Auto-Extractor] ERROR: Could not map precise line bounds for function '{target_func}'.")
        return False
        
    patched = lines[:start_line] + [new_code + "\n\n"] + lines[end_line + 1:]
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w') as f: f.writelines(patched)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--trace", required=True)
    parser.add_argument("-s", "--source", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-r", "--report", required=True)
    args = parser.parse_args()

    bottleneck = find_best_bottleneck(args.trace, args.source)
    if not bottleneck: sys.exit(1)
    
    source_code = extract_function_source(args.source, bottleneck)
    if not source_code: sys.exit(1)
    
    report = get_ai_optimization(bottleneck, source_code)
    
    os.makedirs(os.path.dirname(args.report) or '.', exist_ok=True)
    with open(args.report, 'w') as f: f.write(report)
    
    # CRITICAL: If patching fails, exit with error so the pipeline knows it failed
    success = apply_ai_patch(args.source, args.output, bottleneck, report)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()