from app.rag.chunking import chunk_file


def test_python_symbol_chunk(tmp_path):
    p = tmp_path / "x.py"
    p.write_text("def hello():\n    return 1\n")
    chunks = chunk_file(p, tmp_path)
    assert chunks[0].symbol == "hello"


def test_ingest_tree_ignores_generated_directories(tmp_path):
    cache = tmp_path / ".pytest_cache"
    cache.mkdir()
    (cache / "README.md").write_text("should not be indexed")

    source = tmp_path / "checkout"
    source.mkdir()
    (source / "service.py").write_text("def process_checkout():\n    return 1\n")

    from app.rag.chunking import ingest_tree

    chunks = ingest_tree(tmp_path)

    assert all(".pytest_cache" not in chunk.file_path for chunk in chunks)
    assert any(chunk.file_path == "checkout/service.py" for chunk in chunks)
