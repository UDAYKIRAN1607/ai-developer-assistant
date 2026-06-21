import ast
import re
from backend.agents.code_analysis_agent import run_code_analysis, detect_language

# ── AST-based Python Analyzer ────────────────────────────────────

def analyze_python_ast(code: str) -> dict:
    """
    Parse Python code using AST and extract structure info.
    Returns functions, classes, imports, and syntax errors.
    """
    result = {
        "syntax_valid": True,
        "syntax_error": None,
        "functions": [],
        "classes": [],
        "imports": [],
        "line_count": len(code.splitlines())
    }

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            # Extract function definitions
            if isinstance(node, ast.FunctionDef):
                result["functions"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args]
                })
            # Extract class definitions
            elif isinstance(node, ast.ClassDef):
                result["classes"].append({
                    "name": node.name,
                    "line": node.lineno
                })
            # Extract imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                result["imports"].append(f"{node.module}")

    except SyntaxError as e:
        result["syntax_valid"] = False
        result["syntax_error"] = f"Line {e.lineno}: {e.msg}"

    return result

# ── Complexity Analyzer ──────────────────────────────────────────

def analyze_complexity(code: str, language: str) -> dict:
    """
    Basic complexity metrics — line count, nesting depth, function count.
    """
    lines = code.splitlines()
    non_empty_lines = [l for l in lines if l.strip()]

    # Estimate max nesting depth by indentation
    max_depth = 0
    for line in lines:
        if line.strip():
            depth = (len(line) - len(line.lstrip())) // 4
            max_depth = max(max_depth, depth)

    # Count functions/methods
    if language == "python":
        func_count = len(re.findall(r'^\s*def\s+', code, re.MULTILINE))
    elif language in ["javascript", "typescript"]:
        func_count = len(re.findall(r'function\s+\w+|=>\s*{|=\s*function', code))
    elif language == "java":
        func_count = len(re.findall(r'(public|private|protected)\s+\w+\s+\w+\s*\(', code))
    else:
        func_count = 0

    return {
        "total_lines": len(lines),
        "non_empty_lines": len(non_empty_lines),
        "max_nesting_depth": max_depth,
        "function_count": func_count,
        "complexity_rating": (
            "Low" if max_depth <= 2 and func_count <= 5 else
            "Medium" if max_depth <= 4 and func_count <= 10 else
            "High"
        )
    }

# ── Main Tool Entry Point ────────────────────────────────────────

def run_full_code_analysis(code: str, language: str = None, task: str = "analyze") -> dict:
    """
    Full pipeline:
    1. Detect language if not provided
    2. Run AST analysis (Python only for now)
    3. Run complexity analysis
    4. Run Gemini-powered AI analysis
    """
    # Step 1 — Detect language
    detected_language = language or detect_language(code)

    # Step 2 — AST analysis (Python only)
    ast_result = {}
    if detected_language == "python":
        ast_result = analyze_python_ast(code)

    # Step 3 — Complexity
    complexity = analyze_complexity(code, detected_language)

    # Step 4 — AI analysis via Gemini
    ai_result = run_code_analysis(code=code, language=detected_language, task=task)

    return {
        "language": detected_language,
        "task": task,
        "ast_analysis": ast_result,
        "complexity": complexity,
        "ai_analysis": ai_result["analysis"]
    }