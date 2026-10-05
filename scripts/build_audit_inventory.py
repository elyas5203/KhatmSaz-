"""Build a read-only-source audit inventory; never execute application code.

Run from the repository root. Results belong in audit/RUNS.csv, not generated CSVs.
"""
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/ai/audit"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    files, items, edges, errors = [], [], [], []
    identities = Counter()

    def item(kind, path, line, name):
        identity = f"{kind}:{path}:{name}"
        identities[identity] += 1
        if identities[identity] > 1:
            identity += f":definition-{identities[identity]}"
        items.append(dict(id=digest(identity.encode())[:16], kind=kind, path=path,
                          line=line, name=name, status="NOT_RUN"))

    for path in sorted(filter(None, tracked)):
        if path.startswith(("graphify-out/", "docs/ai/audit/", ".git/")):
            continue
        p = ROOT / path
        if not p.is_file() or p.name.startswith(".env"):
            continue
        raw = p.read_bytes()
        files.append(dict(path=path, sha256=digest(raw), bytes=len(raw)))
        item("FILE", path, 1, path)
        try:
            source = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        if p.suffix == ".py":
            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                errors.append(dict(path=path, line=exc.lineno, error=exc.msg))
                continue

            class Visitor(ast.NodeVisitor):
                stack = []

                def visit_ClassDef(self, node):
                    self.definition(node, "CLASS")

                def visit_FunctionDef(self, node):
                    self.definition(node, "FUNCTION")

                visit_AsyncFunctionDef = visit_FunctionDef

                def definition(self, node, kind):
                    self.stack.append(node.name)
                    name = ".".join(self.stack)
                    item(kind, path, node.lineno, name)
                    for decorator in node.decorator_list:
                        item("DECORATOR", path, decorator.lineno,
                             name + ": " + ast.unparse(decorator))
                    self.generic_visit(node)
                    self.stack.pop()

                def visit_Import(self, node):
                    for alias in node.names:
                        edges.append(dict(path=path, line=node.lineno, source=".".join(self.stack),
                                          kind="IMPORT", target=alias.name))

                def visit_ImportFrom(self, node):
                    edges.append(dict(path=path, line=node.lineno, source=".".join(self.stack),
                                      kind="IMPORT", target="." * node.level + (node.module or "")))

                def visit_Call(self, node):
                    edges.append(dict(path=path, line=node.lineno, source=".".join(self.stack),
                                      kind="CALL_CANDIDATE", target=ast.unparse(node.func)))
                    for kw in node.keywords:
                        if kw.arg in {"callback_data", "url", "href", "web_app"}:
                            item("LINK_BUILDER", path, node.lineno,
                                 f"{'.'.join(self.stack)}:{kw.arg}:L{node.lineno}")
                    self.generic_visit(node)

            Visitor().visit(tree)
        for n, line in enumerate(source.splitlines(), 1):
            # Index locations only: do not copy URLs, tokens or query strings.
            for kind, pattern in (("URL_REFERENCE", r"https?://|tg://|bale://"),
                                  ("MARKDOWN_LINK", r"\[[^\]]*\]\([^)]+\)"),
                                  ("TEMPLATE_LINK", r"(?:href|action|src)\s*=")):
                if re.search(pattern, line):
                    item(kind, path, n, f"{kind}:L{n}")

    def write_csv(name, rows, fields):
        with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    write_csv("FILES.csv", files, ["path", "sha256", "bytes"])
    write_csv("ITEMS.csv", items, ["id", "kind", "path", "line", "name", "status"])
    write_csv("EDGES.csv", edges, ["path", "line", "source", "kind", "target"])
    graph = json.loads((ROOT / "graphify-out/graph.json").read_text(encoding="utf-8"))
    graph_files = {n.get("source_file") for n in graph["nodes"] if n.get("source_file")}
    current = {f["path"] for f in files if f["path"].startswith("src/") and f["path"].endswith(".py")}
    degree = Counter()
    for edge in graph["links"]:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    nodes = {n["id"]: n for n in graph["nodes"]}
    report = dict(
        head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
        scope="All tracked files except graph artifacts, generated audit inventories and .env files; untracked files excluded",
        counts=dict(files=len(files), items=len(items), edges=len(edges), kinds=dict(Counter(i["kind"] for i in items))),
        parse_errors=errors,
        graph=dict(built_at_commit=graph.get("built_at_commit"), nodes=len(graph["nodes"]),
                   edges=len(graph["links"]), sha256=digest((ROOT / "graphify-out/graph.json").read_bytes()),
                   missing_current_source_files=sorted(current-graph_files),
                   hubs=[dict(id=k, degree=v, file=nodes.get(k, {}).get("source_file")) for k,v in degree.most_common(30)]),
        limitations=["Historical graph is not current runtime evidence.",
                     "AST call candidates are not resolved runtime call edges.",
                     "Dynamic routes, FSM transitions and generated links require manual expansion.",
                     "NOT_RUN means inventory only; no behavior was tested."])
    (OUT / "SNAPSHOT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report["counts"]))
    if errors:
        raise SystemExit("Python parse errors recorded in SNAPSHOT.json")


if __name__ == "__main__":
    main()
