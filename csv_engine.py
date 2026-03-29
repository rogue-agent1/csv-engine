#!/usr/bin/env python3
"""csv_engine: CSV parser/writer with quoting and escaping."""
import sys

def parse_row(line, delimiter=",", quote='"'):
    fields = []
    current = []
    in_quotes = False
    i = 0
    while i < len(line):
        c = line[i]
        if in_quotes:
            if c == quote:
                if i + 1 < len(line) and line[i+1] == quote:
                    current.append(quote); i += 2; continue
                in_quotes = False
            else:
                current.append(c)
        else:
            if c == quote:
                in_quotes = True
            elif c == delimiter:
                fields.append("".join(current)); current = []
            elif c not in ("\r", "\n"):
                current.append(c)
        i += 1
    fields.append("".join(current))
    return fields

def parse(text, delimiter=",", has_header=True):
    lines = text.strip().split("\n")
    rows = [parse_row(l, delimiter) for l in lines if l.strip()]
    if has_header and rows:
        header = rows[0]
        return [dict(zip(header, row)) for row in rows[1:]]
    return rows

def format_field(val, delimiter=",", quote='"'):
    s = str(val)
    if delimiter in s or quote in s or "\n" in s:
        return quote + s.replace(quote, quote+quote) + quote
    return s

def format_rows(rows, delimiter=","):
    return "\n".join(delimiter.join(format_field(f, delimiter) for f in row) for row in rows)

def test():
    assert parse_row('a,b,c') == ['a', 'b', 'c']
    assert parse_row('"hello, world",b') == ['hello, world', 'b']
    assert parse_row('"say ""hi""",b') == ['say "hi"', 'b']
    assert parse_row('a,,c') == ['a', '', 'c']
    text = "name,age\nAlice,30\nBob,25"
    rows = parse(text)
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[1]["age"] == "25"
    # Format
    assert format_field("hello") == "hello"
    assert format_field("hi,there") == '"hi,there"'
    assert format_field('say "hi"') == '"say ""hi"""'
    out = format_rows([["a","b"],["1","2,3"]])
    assert out == 'a,b\n1,"2,3"'
    # TSV
    assert parse_row("a\tb\tc", delimiter="\t") == ["a", "b", "c"]
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: csv_engine.py test")
