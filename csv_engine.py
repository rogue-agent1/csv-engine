#!/usr/bin/env python3
"""csv_engine - CSV parser with SQL-like query operations."""
import sys, re

class Table:
    def __init__(self, headers, rows):
        self.headers = headers; self.rows = rows
    def select(self, *cols):
        idx = [self.headers.index(c) for c in cols if c in self.headers]
        return Table([self.headers[i] for i in idx], [[r[i] for i in idx] for r in self.rows])
    def where(self, col, op, val):
        idx = self.headers.index(col)
        ops = {"=": lambda a,b: a==b, ">": lambda a,b: float(a)>float(b), "<": lambda a,b: float(a)<float(b)}
        return Table(self.headers, [r for r in self.rows if ops.get(op, ops["="])(r[idx], val)])
    def order_by(self, col, desc=False):
        idx = self.headers.index(col)
        try:
            return Table(self.headers, sorted(self.rows, key=lambda r: float(r[idx]), reverse=desc))
        except:
            return Table(self.headers, sorted(self.rows, key=lambda r: r[idx], reverse=desc))
    def limit(self, n): return Table(self.headers, self.rows[:n])
    def group_by(self, col, agg_col, fn="count"):
        idx = self.headers.index(col); aidx = self.headers.index(agg_col)
        groups = {}
        for r in self.rows: groups.setdefault(r[idx], []).append(r[aidx])
        fns = {"count": len, "sum": lambda v: sum(float(x) for x in v), "avg": lambda v: sum(float(x) for x in v)/len(v)}
        return Table([col, f"{fn}({agg_col})"], [[k, str(round(fns[fn](v),2))] for k, v in groups.items()])
    def __repr__(self):
        widths = [max(len(h), max((len(str(r[i])) for r in self.rows), default=0)) for i, h in enumerate(self.headers)]
        lines = [" | ".join(h.ljust(w) for h, w in zip(self.headers, widths))]
        lines.append("-+-".join("-"*w for w in widths))
        for r in self.rows: lines.append(" | ".join(str(v).ljust(w) for v, w in zip(r, widths)))
        return "\n".join(lines)

def parse_csv(text, delim=","):
    lines = text.strip().split("\n")
    hdrs = [h.strip().strip('"') for h in lines[0].split(delim)]
    rows = [[c.strip().strip('"') for c in l.split(delim)] for l in lines[1:] if l.strip()]
    return Table(hdrs, rows)

def main():
    data = "name,age,city,salary\nAlice,30,NYC,85000\nBob,25,SF,92000\nCharlie,35,NYC,78000\nDiana,28,LA,95000\nEve,32,SF,88000"
    t = parse_csv(data)
    print("CSV engine demo\n")
    print(t.where("city","=","NYC").select("name","salary"))
    print(f"\nTop earners:")
    print(t.order_by("salary", desc=True).limit(3).select("name","salary"))
    print(f"\nBy city (avg salary):")
    print(t.group_by("city","salary","avg"))

if __name__ == "__main__":
    main()
