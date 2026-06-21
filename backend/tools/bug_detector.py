import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import config

# ── LLM ─────────────────────────────────────────────────────────

def get_llm():
    return ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.1,
        max_output_tokens=2048
    )

# ── Pattern-based Bug Detection ──────────────────────────────────

PYTHON_BUG_PATTERNS = [
    {
        "pattern": r'except\s*:',
        "message": "Bare except clause — catches all exceptions including KeyboardInterrupt. Use 'except Exception as e' instead.",
        "severity": "warning"
    },
    {
        "pattern": r'==\s*None',
        "message": "Use 'is None' instead of '== None' for None comparisons.",
        "severity": "warning"
    },
    {
        "pattern": r'!=\s*None',
        "message": "Use 'is not None' instead of '!= None' for None comparisons.",
        "severity": "warning"
    },
    {
        "pattern": r'print\s*\(',
        "message": "print() found — consider using logging module in production code.",
        "severity": "info"
    },
    {
        "pattern": r'eval\s*\(',
        "message": "eval() is dangerous — can execute arbitrary code. Avoid in production.",
        "severity": "critical"
    },
    {
        "pattern": r'exec\s*\(',
        "message": "exec() is dangerous — can execute arbitrary code. Avoid in production.",
        "severity": "critical"
    },
    {
        "pattern": r'password\s*=\s*["\']',
        "message": "Hardcoded password detected — use environment variables instead.",
        "severity": "critical"
    },
    {
        "pattern": r'api_key\s*=\s*["\']',
        "message": "Hardcoded API key detected — use environment variables instead.",
        "severity": "critical"
    },
    {
        "pattern": r'except\s+Exception\s*:(?!\s*#)',
        "message": "Exception caught but not logged or re-raised — silent failure risk.",
        "severity": "warning"
    },
    {
        "pattern": r'time\.sleep\s*\(\s*[5-9]\d*',
        "message": "Long sleep detected — consider async/await or background tasks.",
        "severity": "info"
    }
]

JS_BUG_PATTERNS = [
    {
        "pattern": r'==(?!=)',
        "message": "Use '===' instead of '==' for strict equality comparison.",
        "severity": "warning"
    },
    {
        "pattern": r'!=(?!=)',
        "message": "Use '!==' instead of '!=' for strict inequality comparison.",
        "severity": "warning"
    },
    {
        "pattern": r'var\s+',
        "message": "Avoid 'var' — use 'const' or 'let' instead.",
        "severity": "warning"
    },
    {
        "pattern": r'console\.log\(',
        "message": "console.log() found — remove before production deployment.",
        "severity": "info"
    },
    {
        "pattern": r'eval\s*\(',
        "message": "eval() is dangerous — avoid in production.",
        "severity": "critical"
    }
]

def detect_pattern_bugs(code: str, language: str) -> list:
    """Run regex-based bug pattern detection."""
    bugs = []
    patterns = PYTHON_BUG_PATTERNS if language == "python" else JS_BUG_PATTERNS

    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        for pattern_info in patterns:
            if re.search(pattern_info["pattern"], line):
                bugs.append({
                    "line": i,
                    "code_snippet": line.strip(),
                    "message": pattern_info["message"],
                    "severity": pattern_info["severity"]
                })

    return bugs

# ── AI-powered Bug Analysis ──────────────────────────────────────

def detect_bugs_with_ai(code: str, language: str, pattern_bugs: list) -> str:
    """Use Gemini to do deep bug analysis beyond pattern matching."""
    llm = get_llm()

    pattern_summary = ""
    if pattern_bugs:
        pattern_summary = "\n".join(
            [f"- Line {b['line']}: {b['message']} ({b['severity']})" for b in pattern_bugs]
        )
        pattern_summary = f"\n\nPattern-based issues already found:\n{pattern_summary}"

    prompt = f"""You are an expert bug detector. Analyze this {language} code for bugs beyond pattern matching:

```{language}
{code}
```
{pattern_summary}

Find and report:
1. **Logic Bugs** — incorrect logic, off-by-one errors, wrong conditions
2. **Runtime Errors** — potential crashes, unhandled exceptions, null references
3. **Edge Cases** — missing boundary checks, empty input handling
4. **Security Issues** — injection risks, insecure operations (if any not already found)

For each bug provide: location, description, and exact fix.
If no additional bugs found, say "No additional bugs detected beyond pattern analysis."
"""

    result = llm.invoke([
        SystemMessage(content="You are a senior software engineer specializing in bug detection and code security."),
        HumanMessage(content=prompt)
    ])

    return result.content

# ── Main Entry Point ─────────────────────────────────────────────

def run_bug_detection(code: str, language: str = "python") -> dict:
    """
    Full bug detection pipeline:
    1. Pattern-based detection
    2. AI-powered deep analysis
    """
    # Step 1 — Pattern bugs
    pattern_bugs = detect_pattern_bugs(code, language)

    # Step 2 — AI deep analysis
    ai_analysis = detect_bugs_with_ai(code, language, pattern_bugs)

    # Severity summary
    critical = [b for b in pattern_bugs if b["severity"] == "critical"]
    warnings = [b for b in pattern_bugs if b["severity"] == "warning"]
    info = [b for b in pattern_bugs if b["severity"] == "info"]

    return {
        "language": language,
        "pattern_bugs": pattern_bugs,
        "ai_analysis": ai_analysis,
        "summary": {
            "total_pattern_issues": len(pattern_bugs),
            "critical": len(critical),
            "warnings": len(warnings),
            "info": len(info)
        }
    }