import os

def get_language(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.py']: return 'python'
    elif ext in ['.js', '.ts']: return 'javascript'
    else: return None  # Or raise error
