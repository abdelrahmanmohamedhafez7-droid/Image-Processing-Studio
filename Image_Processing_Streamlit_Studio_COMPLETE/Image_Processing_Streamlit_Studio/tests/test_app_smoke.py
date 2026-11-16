"""Pure-Python Streamlit call-path smoke test.

This is NOT a browser screenshot or visual layout test. It exercises render
paths while Streamlit is unavailable in the offline validation environment.
"""
import importlib.util
from pathlib import Path
import sys
import types

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class Context:
    def metric(self, *args, **kwargs):
        return None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.session_state = {}
        self.sidebar = Context()
        self.current_module = None
        self.saw_images = 0
        self.saw_css = []
        self.downloads = 0

    def set_page_config(self, *args, **kwargs):
        assert kwargs.get("layout") == "wide"

    def columns(self, widths, **kwargs):
        return [Context() for _ in range(widths if isinstance(widths, int) else len(widths))]

    def container(self, **kwargs):
        return Context()

    def expander(self, *args, **kwargs):
        return Context()

    def radio(self, label, options, **kwargs):
        return self.current_module if self.current_module in options else options[0]

    def selectbox(self, label, options, index=0, **kwargs):
        return options[index]

    def slider(self, label, *args, **kwargs):
        return args[2] if len(args) >= 3 else kwargs.get("value", args[0])

    def select_slider(self, label, options, **kwargs):
        return kwargs.get("value", options[0])

    def number_input(self, label, **kwargs):
        return kwargs.get("value", 0)

    def file_uploader(self, label, **kwargs):
        return None

    def markdown(self, body, **kwargs):
        if "--ip-bg" in body:
            self.saw_css.append(body)

    def button(self, label, **kwargs):
        assert label
        return False

    def image(self, img, **kwargs):
        assert isinstance(img, np.ndarray) and img.size
        self.saw_images += 1

    def download_button(self, label, data, **kwargs):
        assert len(data) > 20
        self.downloads += 1

    def __getattr__(self, key):
        if key in {"caption", "divider", "subheader", "write", "metric", "dataframe", "line_chart", "code", "error", "info"}:
            return lambda *a, **k: None
        if key == "stop":
            raise AssertionError("Unexpected st.stop")
        raise AttributeError(key)


def test_every_module_comparison_renders_with_both_palette_settings(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    monkeypatch.syspath_prepend(str(ROOT))
    module_name="ip_lab_ui_smoke_module"
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "app.py")
    app = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = app
    try:
        spec.loader.exec_module(app)
        for dark in (True, False):
            for section, groups in app.SECTIONS.items():
                for group in groups:
                    fake.session_state.clear()
                    fake.session_state["dark_mode"] = dark
                    fake.session_state["section"] = section
                    fake.session_state[f"choice::{group}"] = "Compare All"
                    fake.current_module = group
                    start = fake.saw_images
                    app.main()
                    # Original + all result variants, across all nine groups.
                    assert fake.saw_images - start >= 2
        assert len(fake.saw_css) == 18
        assert fake.downloads == 36  # original and ZIP per full-comparison render
        assert any("#F5F8FD" in css for css in fake.saw_css)
        assert any("#081321" in css for css in fake.saw_css)
        assert all(not label.startswith("Task ") for label in app.SECTIONS)
    finally:
        sys.modules.pop(module_name, None)


def test_individual_mode_shows_only_original_and_selected_output(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    monkeypatch.syspath_prepend(str(ROOT))
    name = "ip_lab_single_view_smoke"
    spec = importlib.util.spec_from_file_location(name, ROOT / "app.py")
    app = importlib.util.module_from_spec(spec)
    sys.modules[name] = app
    try:
        spec.loader.exec_module(app)
        fake.session_state["section"] = "Point Operations"
        fake.session_state["dark_mode"] = False
        fake.current_module = "Arithmetic"
        fake.session_state["choice::Arithmetic"] = "Division (/)"
        app.main()
        assert fake.saw_images == 2
        assert fake.downloads == 2  # one original, one processed
        app.switch_theme()
        assert fake.session_state["dark_mode"] is True
    finally:
        sys.modules.pop(name, None)
