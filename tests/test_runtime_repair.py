from pathlib import Path

from services.real_react_multifile_builder import (
    PlannedComponent,
    _install_runtime_reporter,
    _runtime_target_path,
    _retry_component_with_runtime_error,
)


def test_runtime_error_maps_to_exact_component():
    plan = [
        PlannedComponent("App.jsx", "entry", "App"),
        PlannedComponent("components/MenuCard.jsx", "menu card", "MenuCard"),
    ]
    event = {
        "message": "Cannot read properties of undefined (reading 'div')",
        "stack": "at MenuCard (http://localhost:1234/src/components/MenuCard.jsx:5:13)",
        "filename": "http://localhost:1234/src/components/MenuCard.jsx",
    }
    assert _runtime_target_path(plan, event) == "components/MenuCard.jsx"


def test_runtime_reporter_is_injected_with_task_id(tmp_path):
    project = tmp_path / "app"
    project.mkdir()
    (project / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
    _install_runtime_reporter(project, "react-test-123")
    html = (project / "index.html").read_text(encoding="utf-8")
    assert "AZIZ_RUNTIME_REPORTER" in html
    assert "react-test-123" in html
    assert "/api/runtime-errors/" in html
    assert "hadError" in html


def test_runtime_repair_prompt_is_targeted_only():
    class FakeGateway:
        def __init__(self):
            self.messages = None

        def chat(self, messages, **kwargs):
            self.messages = messages
            return "function MenuCard() { return <div>fixed</div>; }\nexport default MenuCard;"

    gateway = FakeGateway()
    target = PlannedComponent("components/MenuCard.jsx", "menu card", "MenuCard")
    plan = [target, PlannedComponent("App.jsx", "entry", "App")]
    result = _retry_component_with_runtime_error(
        gateway,
        plan,
        target,
        "coffee shop",
        {
            "message": "Cannot read properties of undefined (reading 'div')",
            "stack": "at MenuCard (MenuCard.jsx:5:13)",
        },
        "function MenuCard(){ return broken; }\nexport default MenuCard;",
    )
    assert "export default MenuCard" in result
    prompt = gateway.messages[-1]["content"]
    assert "Repair ONLY this component" in prompt
    assert "components/MenuCard.jsx" in prompt
    assert "Do not change imports or invent files" in prompt


def test_runtime_reporter_has_parent_message_fallback(tmp_path):
    project = tmp_path / 'project'
    project.mkdir()
    (project / 'index.html').write_text('<html><head></head><body></body></html>', encoding='utf-8')
    _install_runtime_reporter(project, 'runtime-postmessage-test')
    html = (project / 'index.html').read_text(encoding='utf-8')
    assert 'AZIZ_RUNTIME_REPORT' in html
    assert 'window.parent.postMessage' in html
    assert 'Do not abort reporting when the preview has no referrer' in html
    assert 'runtime_token' in html
