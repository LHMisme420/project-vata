# humanizer.py
import re
import random
import os

def detect_language(file_path: str) -> str:
    """Simple extension-based language detector."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.py']: return 'python'
    if ext in ['.js', '.jsx', '.ts', '.tsx']: return 'javascript'
    return 'unknown'  # Can expand later (e.g., '.java', '.cpp')

def calculate_soul_score(code: str, language: str = 'python') -> int:
    """Core soul scoring heuristics – expand as needed."""
    lines = code.splitlines()
    score = 0

    # Comment density (higher = more human)
    comment_prefix = '#' if language == 'python' else '//'
    comment_count = sum(1 for line in lines if line.strip().startswith(comment_prefix))
    score += min(int(comment_count / max(1, len(lines)) * 60), 60)

    # Debug statements
    debug_kws = ['print(', 'console.log(', 'console.debug(', 'debugger;']
    debug_count = sum(1 for line in lines if any(kw in line for kw in debug_kws))
    score += min(debug_count * 8, 25)

    # Personal markers (TODO, FIXME, HACK, NOTE)
    markers = len(re.findall(r'(TODO|FIXME|HACK|NOTE):?', code, re.IGNORECASE))
    score += min(markers * 10, 30)

    # Messiness: inconsistent indentation, blank lines
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    indent_variety = len(set(indents)) if indents else 0
    blank_lines = sum(1 for line in lines if not line.strip())
    score += 15 if indent_variety > 3 else 0
    score += min(blank_lines // 5 * 5, 15)

    # Quirky/overly-descriptive variables (heuristic: long names, caps, underscores mix)
    var_patterns = r'(def|let|const|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'
    vars_found = re.findall(var_patterns, code)
    quirky = sum(1 for _, name in vars_found if len(name) > 15 or name.isupper() or '_' in name and name[0].isupper())
    score += min(quirky * 5, 20)

    return min(max(score, 0), 100)

def humanize_code(code: str, language: str = 'python', intensity: float = 0.7) -> str:
    """Inject human artifacts. Intensity 0.0–1.0 controls how aggressive."""
    lines = code.splitlines()
    new_lines = []

    comment_style = '#' if language == 'python' else '//'
    debug_stmt = 'print("debug point")' if language == 'python' else 'console.log("debug here");'

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Inject comments every ~4-8 lines
        if random.random() < intensity * 0.25 and i % random.randint(4, 8) == 0:
            comments = [
                f"{comment_style} TODO: maybe optimize later",
                f"{comment_style} HACK: this works but ugly af",
                f"{comment_style} NOTE: borrowed from old project"
            ]
            new_lines.append(random.choice(comments))

        # Add debug occasionally
        if random.random() < intensity * 0.15 and 'function' in line.lower() or 'def ' in line:
            new_lines.append('    ' + debug_stmt)  # Indent roughly

    # Occasionally mess up indentation slightly
    if random.random() < intensity * 0.1:
        for j in range(len(new_lines)):
            if random.random() < 0.05:
                new_lines[j] = ' ' + new_lines[j]  # Add extra space

    return '\n'.join(new_lines)
