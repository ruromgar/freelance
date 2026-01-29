import argparse
import ast
import logging
import sys
from collections import namedtuple
from pathlib import Path

logger = logging.getLogger(__name__)
root = Path(__file__).parent.parent
ImportInfo = namedtuple("ImportInfo", ["module", "name", "lineno"])


class ProjectGuidelinesNodeVisitor(ast.NodeVisitor):
    ALLOWED_NAMESPACES = {"api", "ninja", "tests"}
    PROHIBITED_DECORATORS = {"dramatiq.actor", "actor"}

    def __init__(self, protected_apps: set[str], file_path: Path):
        self.protected_apps = protected_apps
        self.file_path = file_path
        self.errors: list[str] = []

    def visit_Import(self, node: ast.Import):
        for n in node.names:
            self.validate_import(ImportInfo([], n.name.split("."), node.lineno))

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Import visitor."""
        if node.level > 0:
            if len(self.file_path.parents) == node.level:
                module = node.module.split(".") if node.module else []
            else:
                self.generic_visit(node)
                return
        else:
            module = node.module.split(".") if node.module else []
        for n in node.names:
            self.validate_import(ImportInfo(module, n.name.split("."), node.lineno))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for decorator in node.decorator_list:
            name = self.get_decorator_name(decorator)
            if name in self.PROHIBITED_DECORATORS:
                self.errors.append(
                    f"Prohibited decorator: {self.file_path}, {name}, "
                    f"lineno={decorator.lineno}"
                )

        self.generic_visit(node)

    def validate_import(self, imp: ImportInfo):
        try:
            if imp.module:
                module = imp.module[0]
                name = imp.module[1] if len(imp.module) > 1 else imp.name[0]
            else:
                module = imp.name[0]
                name = None if len(imp.name) == 1 else imp.name[1]

            if module in self.protected_apps and name not in self.ALLOWED_NAMESPACES:
                raise ValueError

        except (IndexError, ValueError):
            imp_str = ".".join(imp.module + imp.name)
            self.errors.append(
                f"Import not allowed: {self.file_path}, {imp_str}, lineno={imp.lineno}"
            )

    @classmethod
    def get_decorator_name(cls, decorator: ast.expr) -> str:
        if isinstance(decorator, ast.Name):
            return decorator.id

        if isinstance(decorator, ast.Attribute):
            return f"{cls.get_decorator_name(decorator.value)}.{decorator.attr}"

        if isinstance(decorator, ast.Call):
            return cls.get_decorator_name(decorator.func)

        return ""


def get_local_apps() -> set[str]:
    """Return a set of local django application names.

    Process:
        - Create a set of all the directories in the project root
        - Parse the INSTALLED_APPS from the monolith.settings
        - Return the intersection of these two sets
    """
    packages = {path.name for path in root.iterdir() if path.is_dir()}
    settings_file = root.joinpath("config/settings/base.py")
    settings = settings_file.read_text()

    start = settings.index("INSTALLED_APPS")
    start = settings.index("[", start)
    end = settings.index("]", start)

    # Keep only the app name from the configs
    # example: "push_notifications.apps.PushNotificationsConfig"
    installed_apps = {
        name.split(".", 1)[0] for name in eval(settings[start : end + 1], {}, {})
    }

    return packages.intersection(installed_apps)


def get_ast_tree(file_path: Path) -> ast.AST:
    """Parse a file path with ast."""
    with file_path.open("r") as fh:
        return ast.parse(fh.read())


def validate_guidelines(file_path: Path, protected_apps: set[str]):
    """Validate the single application deployment guidelines."""
    # Skip config files - they need to wire all apps together
    if file_path.parts[0] == "config":
        return

    # Find the app of the file and remove it from the protected
    if len(file_path.parts) == 1:
        return

    file_package = file_path.parts[0]
    if file_package in protected_apps:
        protected_apps.remove(file_package)

    # Parse with ast
    tree = get_ast_tree(file_path)

    visitor = ProjectGuidelinesNodeVisitor(protected_apps, file_path)
    visitor.visit(tree)

    if visitor.errors:
        for error in visitor.errors:
            logger.error(error)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    local_apps = get_local_apps()
    for filename in args.filenames:
        file_path = Path(filename)
        if file_path.suffix == ".py":
            validate_guidelines(file_path, set(local_apps))


if __name__ == "__main__":
    main()
