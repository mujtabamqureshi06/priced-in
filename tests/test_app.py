from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_app_runs_both_cases() -> None:
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=300)
    at.run()
    assert not at.exception
    options = list(at.sidebar.selectbox[0].options)
    at.sidebar.selectbox[0].select(options[1]).run()
    assert not at.exception
