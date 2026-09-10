import ast
from pathlib import Path

FORBIDDEN_MODULES = {
    "openai",
    "openclaw",
    "whatsapp",
    "memory",
    "context_engine",
    "packages.agent_core.agent",
    "packages.agent_core.tools",
    "packages.agent_core.llm",
}


def get_imported_modules(file_path: Path) -> set[str]:
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_domain_boundary_isolation() -> None:
    domain_files = [
        Path("apps/api/db/models/project.py"),
        Path("apps/api/db/models/task.py"),
        Path("apps/api/schemas/project.py"),
        Path("apps/api/schemas/task.py"),
        Path("apps/api/repositories/project.py"),
        Path("apps/api/repositories/task.py"),
        Path("apps/api/services/project.py"),
        Path("apps/api/services/task.py"),
        Path("apps/api/api/v1/routes/projects.py"),
        Path("apps/api/api/v1/routes/tasks.py"),
    ]

    for file_path in domain_files:
        assert file_path.exists(), f"File {file_path} must exist"
        imports = get_imported_modules(file_path)

        for imp in imports:
            for forbidden in FORBIDDEN_MODULES:
                assert not imp.startswith(forbidden), (
                    f"Architectural boundary violation in {file_path}: "
                    f"imports '{imp}', which violates forbidden module '{forbidden}'"
                )
