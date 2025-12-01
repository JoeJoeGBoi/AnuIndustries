from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR / "scripts"))

import download_apple_music  # noqa: E402

validate_cookies_path = download_apple_music.validate_cookies_path


def test_validate_cookies_path_missing_file(tmp_path):
    missing_path = tmp_path / "cookies.txt"

    with pytest.raises(FileNotFoundError) as excinfo:
        validate_cookies_path(missing_path)

    assert "Missing Apple Music cookies file" in str(excinfo.value)


def test_validate_cookies_path_present_file(tmp_path, monkeypatch):
    cookies_file = tmp_path / "cookies.txt"
    cookies_file.write_text("dummy\tcontent\n")

    # Point the current working directory to the temporary folder so the
    # function will resolve the default cookies.txt path there.
    monkeypatch.setenv("APPLE_MUSIC_COOKIES", "")
    monkeypatch.chdir(tmp_path)

    assert validate_cookies_path() == cookies_file.resolve()


def test_validate_cookies_path_env_override(tmp_path, monkeypatch):
    cookies_file = tmp_path / "apple_music_cookies.txt"
    cookies_file.write_text("dummy\tcontent\n")

    monkeypatch.setenv("APPLE_MUSIC_COOKIES", str(cookies_file))

    assert validate_cookies_path() == cookies_file.resolve()


def test_validate_cookies_path_script_dir_fallback(tmp_path, monkeypatch):
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_cookies = script_dir / "cookies.txt"
    script_cookies.write_text("dummy\tcontent\n")

    monkeypatch.setenv("APPLE_MUSIC_COOKIES", "")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(download_apple_music, "__file__", str(script_dir / "download_apple_music.py"))

    assert validate_cookies_path() == script_cookies.resolve()
