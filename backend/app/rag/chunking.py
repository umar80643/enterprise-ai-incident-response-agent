import ast, hashlib
from pathlib import Path
from dataclasses import dataclass

SUPPORTED={".py",".md",".txt",".json",".yaml",".yml",".java",".js",".ts",".tsx"}

@dataclass
class Chunk:
    id:str; file_path:str; line_start:int; line_end:int; symbol:str|None; language:str; text:str; chunk_type:str="code"

def _id(path,start,end,text):
    return hashlib.sha1(f"{path}:{start}:{end}:{text}".encode()).hexdigest()[:16]

def chunk_file(path: Path, root: Path) -> list[Chunk]:
    rel=str(path.relative_to(root))
    text=path.read_text(encoding="utf-8", errors="ignore")
    lines=text.splitlines()
    lang=path.suffix.lstrip(".")
    out=[]
    if path.suffix==".py":
        try:
            tree=ast.parse(text)
            for node in tree.body:
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    start=node.lineno; end=getattr(node,"end_lineno",start)
                    body="\n".join(lines[start-1:end])
                    out.append(Chunk(_id(rel,start,end,body),rel,start,end,node.name,lang,body))
        except SyntaxError: pass
    if not out:
        step=60
        for i in range(0,len(lines),step):
            body="\n".join(lines[i:i+step])
            if body.strip():
                out.append(Chunk(_id(rel,i+1,min(i+step,len(lines)),body),rel,i+1,min(i+step,len(lines)),None,lang,body,"documentation" if path.suffix in {".md",".txt"} else "code"))
    return out

def ingest_tree(root: Path) -> list[Chunk]:
    chunks=[]
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED and ".git" not in p.parts and "node_modules" not in p.parts:
            chunks.extend(chunk_file(p,root))
    return chunks
