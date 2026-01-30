import tokenize
from io import BytesIO
from collections import Counter

def fingerprint(code: str):
    tokens = tokenize.tokenize(BytesIO(code.encode()).readline)
    token_types = Counter()
    token_strings = Counter()

    for tok in tokens:
        token_types[tok.type] += 1
        if tok.string.isidentifier():
            token_strings[tok.string] += 1

    return {
        "token_type_distribution": dict(token_types),
        "identifier_frequency": dict(token_strings)
    }
