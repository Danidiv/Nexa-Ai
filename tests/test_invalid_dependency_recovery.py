from pathlib import Path
from types import SimpleNamespace


def test_404_dependency_is_classified_as_invalid(monkeypatch, tmp_path):
    from services import real_react_builder as rb

    monkeypatch.setattr(rb.shutil, "which", lambda name: "/usr/bin/npm")

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr='npm error code E404\nnpm error 404 Not Found - GET https://registry.npmjs.org/@radix-ui%2freact-icon - Not found',
        )

    monkeypatch.setattr(rb.subprocess, "run", fake_run)
    ok, detail = rb.ensure_npm_dependency(Path(tmp_path), "@radix-ui/react-icon")
    assert ok is False
    assert detail.startswith("INVALID_NPM_PACKAGE:")


def test_missing_dependency_parser_keeps_scoped_package_root():
    from services.real_react_builder import missing_dependency_from_vite_error

    assert missing_dependency_from_vite_error(
        'Failed to resolve import "@tanstack/react-table" from "src/App.jsx"'
    ) == "@tanstack/react-table"
    assert missing_dependency_from_vite_error(
        'Failed to resolve import "chart.js/auto" from "src/App.jsx"'
    ) == "chart.js"


def test_node_modules_platform_check_rejects_windows_cache_on_linux(tmp_path, monkeypatch):
    from services.real_react_builder import _node_modules_platform_ready

    nm = tmp_path / "node_modules"
    (nm / ".bin").mkdir(parents=True)
    (nm / ".bin" / "vite").write_text("#!/bin/sh")
    (nm / "react").mkdir()
    (nm / "@rollup" / "rollup-win32-x64-gnu").mkdir(parents=True)
    (nm / "@esbuild" / "win32-x64").mkdir(parents=True)
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    assert _node_modules_platform_ready(nm) is False
