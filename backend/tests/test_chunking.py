from app.rag.chunking import chunk_file
def test_python_symbol_chunk(tmp_path):
    p=tmp_path/"x.py"; p.write_text("def hello():\n    return 1\n")
    chunks=chunk_file(p,tmp_path)
    assert chunks[0].symbol=="hello"
