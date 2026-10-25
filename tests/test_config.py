import pytest

from artio.config import load_config


def test_load_config_from_path(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("robot:\n  name: test\n", encoding="utf-8")
    assert load_config(cfg)["robot"]["name"] == "test"


def test_missing_config_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ARTIO_CONFIG", raising=False)
    with pytest.raises(FileNotFoundError):
        load_config()
