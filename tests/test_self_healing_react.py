from pathlib import Path

from services.real_react_multifile_builder import (
    PlannedComponent,
    validate_and_repair_imports,
)


class FakeGateway:
    def __init__(self):
        self.calls = 0

    def chat(self, messages, **kwargs):
        self.calls += 1
        return """
function PricingCard({ tier, price }) {
  return <article><h2>{tier}</h2><p>{price}</p></article>;
}
export default PricingCard;
"""


def test_wrong_relative_import_is_repaired_without_model_call():
    gateway = FakeGateway()
    plan = [
        PlannedComponent("App.jsx", "entry", "App"),
        PlannedComponent("components/Header.jsx", "header", "Header"),
        PlannedComponent("components/Footer.jsx", "footer", "Footer"),
    ]
    contents = {
        "App.jsx": "import Header from './components/Header.jsx'; export default function App(){return <Header/>}",
        "components/Header.jsx": "export default function Header(){return <header/>}",
        "components/Footer.jsx": "import Header from '../Header.jsx'; export default function Footer(){return <Header/>}",
    }

    validate_and_repair_imports(gateway, plan, contents, "test")

    assert "./Header.jsx" in contents["components/Footer.jsx"]
    assert gateway.calls == 0


def test_missing_component_is_added_and_generated():
    gateway = FakeGateway()
    plan = [
        PlannedComponent("App.jsx", "entry", "App"),
        PlannedComponent("components/Header.jsx", "header", "Header"),
    ]
    contents = {
        "App.jsx": (
            "import Header from './components/Header.jsx'; "
            "import PricingCard from './components/PricingCard.jsx'; "
            "export default function App(){return <><Header/><PricingCard/></>}"
        ),
        "components/Header.jsx": "export default function Header(){return <header/>}",
    }

    plan = validate_and_repair_imports(gateway, plan, contents, "pricing page")

    assert "components/PricingCard.jsx" in [p.path for p in plan]
    assert "components/PricingCard.jsx" in contents
    assert gateway.calls == 1


def test_scaffold_reuses_template_node_modules_without_npm_install(tmp_path, monkeypatch):
    import services.real_react_builder as builder

    template = tmp_path / "template"
    template.mkdir()
    (template / "node_modules").mkdir()
    for name in (
        "package.json",
        "vite.config.js",
        "tsconfig.json",
        "tailwind.config.js",
        "postcss.config.js",
        "index.html",
    ):
        (template / name).write_text("{}", encoding="utf-8")
    (template / "src").mkdir()
    (template / "src" / "main.tsx").write_text("", encoding="utf-8")
    (template / "src" / "index.css").write_text("", encoding="utf-8")
    (template / "src" / "lib").mkdir()
    (template / "src" / "lib" / "utils.ts").write_text("", encoding="utf-8")
    (template / "src" / "components" / "ui").mkdir(parents=True)

    monkeypatch.setattr(builder, "TEMPLATE_DIR", template)
    project = builder.scaffold_react_project("no-install-test", workspace_dir=str(tmp_path / "workspace"))

    assert (project / "node_modules").exists()
    assert (project / "node_modules").is_symlink() or (project / "node_modules").is_dir()
    assert (project / "node_modules").resolve() == (template / "node_modules").resolve()


def test_tsx_import_repair_uses_tsx_extension():
    gateway = FakeGateway()
    plan = [
        PlannedComponent("App.tsx", "entry", "App"),
        PlannedComponent("components/Header.tsx", "header", "Header"),
    ]
    contents = {
        "App.tsx": "import Header from './Header.tsx'; export default function App(){return <Header/>}",
        "components/Header.tsx": "import App from '../App.tsx'; export default function Header(){return <App/>}",
    }
    # The first import is intentionally wrong: App.tsx cannot resolve
    # ./Header.tsx from src/. The basename uniquely identifies the planned
    # components/Header.tsx file, so the deterministic repair should fix it.
    from services.real_react_multifile_builder import validate_and_repair_imports
    validate_and_repair_imports(gateway, plan, contents, "test", component_extension=".tsx")
    assert "./components/Header.tsx" in contents["App.tsx"]


def test_oversized_react_plan_is_automatically_replanned_to_ten_files():
    import json
    from services.real_react_multifile_builder import generate_plan

    oversized = [{"path": "App.jsx", "purpose": "entry"}] + [
        {"path": f"components/Section{i}.jsx", "purpose": f"section {i}"}
        for i in range(1, 11)
    ]
    compact = [
        {"path": "App.jsx", "purpose": "entry"},
        {"path": "components/Hero.jsx", "purpose": "hero"},
        {"path": "components/Sections.jsx", "purpose": "features and how it works"},
        {"path": "components/Pricing.jsx", "purpose": "pricing"},
        {"path": "components/SocialProof.jsx", "purpose": "trusted companies and testimonials"},
        {"path": "components/FAQ.jsx", "purpose": "faq"},
    ]

    class PlanningGateway:
        def __init__(self):
            self.calls = 0
        def chat(self, messages, **kwargs):
            self.calls += 1
            return json.dumps(oversized if self.calls == 1 else compact)

    gateway = PlanningGateway()
    plan = generate_plan(gateway, "Build a SaaS landing page with many sections")
    assert len(plan) == 6
    assert plan[0].path == "App.jsx"
    assert gateway.calls == 2


def test_oversized_react_plan_retries_compression():
    import json
    from services.real_react_multifile_builder import generate_plan

    oversized = [{"path": "App.jsx", "purpose": "entry"}] + [
        {"path": f"components/Section{i}.jsx", "purpose": f"section {i}"}
        for i in range(1, 11)
    ]
    still_large = [{"path": "App.jsx", "purpose": "entry"}] + [
        {"path": f"components/Merged{i}.jsx", "purpose": f"merged {i}"}
        for i in range(1, 11)
    ]
    compact = [
        {"path": "App.jsx", "purpose": "entry"},
        {"path": "components/MainSections.jsx", "purpose": "merged sections"},
    ]

    class PlanningGateway:
        def __init__(self):
            self.calls = 0
        def chat(self, messages, **kwargs):
            self.calls += 1
            return json.dumps([oversized, still_large, compact][self.calls - 1])

    gateway = PlanningGateway()
    plan = generate_plan(gateway, "Build a large landing page")
    assert len(plan) == 2
    assert gateway.calls == 3


def test_alias_directory_import_is_rewritten_to_explicit_index():
    class AliasGateway(FakeGateway):
        def chat(self, messages, **kwargs):
            self.calls += 1
            return """
export const Card = ({ children }) => <div>{children}</div>;
export const Button = ({ children }) => <button>{children}</button>;
"""
    gateway = AliasGateway()
    plan = [
        PlannedComponent("App.jsx", "entry", "App"),
        PlannedComponent("components/PricingTable.jsx", "pricing", "PricingTable"),
    ]
    contents = {
        "App.jsx": "import PricingTable from './components/PricingTable.jsx'; export default function App(){return <PricingTable/>}",
        "components/PricingTable.jsx": (
            "import { Card, Button } from '@/components/ui/'; "
            "export default function PricingTable(){return <Card><Button>Buy</Button></Card>}"
        ),
    }
    validate_and_repair_imports(gateway, plan, contents, "saas landing page")
    assert '@/components/ui/index.jsx' in contents["components/PricingTable.jsx"]
    assert contents["components/ui/index.jsx"].startswith("export { Badge")


def test_alias_import_resolves_existing_scaffold_ui_without_duplicate_generation():
    gateway = FakeGateway()
    plan = [PlannedComponent("App.jsx", "entry", "App")]
    contents = {
        "App.jsx": (
            "import { Badge } from '@/components/ui/badge'; "
            "export default function App(){return <Badge>New</Badge>}"
        ),
    }
    validate_and_repair_imports(gateway, plan, contents, "test")
    assert "components/ui/badge.jsx" not in contents
    assert gateway.calls == 0


def test_missing_avatar_uses_deterministic_ui_fallback_without_model_call():
    from services.real_react_multifile_builder import resolve_missing_local_resources

    gateway = FakeGateway()
    plan = [PlannedComponent("App.jsx", "entry", "App")]
    contents = {
        "App.jsx": (
            "import { Avatar, AvatarFallback } from '@/components/ui/avatar'; "
            "export default function App(){return <Avatar><AvatarFallback>A</AvatarFallback></Avatar>}"
        )
    }
    resolve_missing_local_resources(gateway, plan, contents, "landing page")
    # Avatar is a deterministic scaffold resource, so the resolver must not
    # ask the Mistral model to invent/repair it. The real scaffold copy is
    # installed into src/components/ui/avatar.jsx before Vite runs.
    assert "components/ui/avatar.jsx" not in contents
    assert gateway.calls == 0
