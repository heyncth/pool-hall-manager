from poolhall.storage import load_json, read_text, save_json, write_text


def test_save_load_roundtrip(tmp_path):
    path = tmp_path / "data.json"
    save_json(path, {"a": [1, 2]})
    assert load_json(path) == {"a": [1, 2]}


def test_load_missing_returns_default(tmp_path):
    assert load_json(tmp_path / "nope.json", default=[]) == []


def test_load_broken_returns_default(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json")
    assert load_json(path, default=None) is None


def test_write_read_text(tmp_path):
    path = tmp_path / "f.txt"
    write_text(path, "hello")
    assert read_text(path) == "hello"
    assert read_text(tmp_path / "missing.txt") is None

def test_save_overwrites(tmp_path):
    path = tmp_path / "data.json"
    save_json(path, {"v": 1})
    save_json(path, {"v": 2})
    assert load_json(path) == {"v": 2}
