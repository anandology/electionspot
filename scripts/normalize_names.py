"""Normalize names.
"""

import re

re_paren = re.compile(r"\(.*\)")
re_dot_nospace = re.compile(r"\.([^ ])")
re_initial = re.compile(r"([A-Z]) ")
re_many_spaces = re.compile(r" +")

def action(pattern, replacement):
    rx = re.compile(pattern)
    def f(name):
        return rx.sub(replacement, name)
    return f

def matcher(sign_func):
    d = {}
    def f(name):
        sign = sign_func(name)
        return d.setdefault(sign, name)
    return f

re_sign1 = re.compile(r'\.|,| ')
def sign1(name):
    "match order"
    tokens = [t.lower() for t in re_sign1.split(name)]
    return "".join(sorted(tokens))

def sign2(name):
    """sort all chars"""
    chars = re_sign1.sub('', name).lower()
    return "".join(sorted(chars))

actions = [
    action(r'\(.*\)', ''), # remove parentheses
    action(r'\.([^ ])', r'. \1'), # space after dot
    action(r'([A-Z]) +', r'\1. '), # dot space after initial
    action(r' +', r' '), # strip multiple spaces
    matcher(sign1), # handle reorders
    matcher(sign2), # handle space-sensitivity (e.g. Lal Krishna, Lalkrishna)
]

def normalize(name):
    """
        >>> normalize('hello world (in parenthesis)')
        'hello world'
        >>> normalize('H.World')
        'H. World'
        >>> normalize('H World')
        'H. World'
        >>> normalize('H World')
        'H. World'
    """
    for a in actions:
        name = a(name)
    return name.strip()

def normalize_names(names):
    return (normalize(name) for name in names)

def normalize_column(filename, col):
    for line in open(filename):
        tokens = line.strip().split("\t")
        tokens[col] = normalize(tokens[col])
        print "\t".join(tokens)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        normalize_column(sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) == 2:
        for name in open(sys.argv[1]).read().split("\n"):
            print normalize(name)
