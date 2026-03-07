#!/usr/bin/env python3
"""
DevSpec Compiler - Transforms specs into actionable artifacts

Generates:
- Implementation stubs from specs
- API schemas from interfaces
- Documentation from specs
- Test templates from tasks
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FeatureSpec:
    name: str
    goals: List[str]
    design: str
    interfaces: List[str]
    dependencies: List[str]
    tasks: List[str]


class SpecCompiler:
    def __init__(self, spec_root: str = "spec", output_dir: str = "generated"):
        self.spec_root = Path(spec_root)
        self.output_dir = Path(output_dir)

    def compile_all(self):
        """Compile all specs to artifacts."""
        print("=== DevSpec Compiler ===\n")

        self.output_dir.mkdir(exist_ok=True)

        # Generate implementation stubs
        self.generate_stubs()

        # Generate API schemas
        self.generate_schemas()

        # Generate documentation
        self.generate_docs()

        # Generate test templates
        self.generate_tests()

        print(f"\nGenerated artifacts in {self.output_dir}/")

    def parse_feature_spec(self, spec_path: Path) -> Optional[FeatureSpec]:
        """Parse a feature specification file."""
        if not spec_path.exists():
            return None

        content = spec_path.read_text()

        # Extract sections
        goals = self._extract_list(content, "goals")
        design = self._extract_section(content, "design")
        interfaces = self._extract_list(content, "interfaces")
        dependencies = self._extract_list(content, "dependencies")
        tasks = self._extract_tasks(spec_path.parent / "tasks.md")

        return FeatureSpec(
            name=spec_path.parent.name,
            goals=goals,
            design=design,
            interfaces=interfaces,
            dependencies=dependencies,
            tasks=tasks
        )

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a section from markdown content."""
        pattern = rf"##\s*{section_name}\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract list items from a section."""
        section = self._extract_section(content, section_name)
        items = re.findall(r"[-*]\s*(.+)", section)
        return [item.strip() for item in items]

    def _extract_tasks(self, tasks_path: Path) -> List[str]:
        """Extract tasks from tasks.md."""
        if not tasks_path.exists():
            return []

        content = tasks_path.read_text()
        tasks = re.findall(r"-\s*\[([ x])\]\s*(.+)", content)
        return [{"done": checked == "x", "task": task} for checked, task in tasks]

    def generate_stubs(self):
        """Generate implementation stubs from feature specs."""
        stubs_dir = self.output_dir / "stubs"
        stubs_dir.mkdir(exist_ok=True)

        features_path = self.spec_root / "features"
        if not features_path.exists():
            return

        for feature_dir in features_path.iterdir():
            if feature_dir.is_dir():
                spec = self.parse_feature_spec(feature_dir / "spec.md")
                if spec:
                    stub_file = stubs_dir / f"{spec.name}.ts"
                    stub_content = self._generate_stub_content(spec)
                    stub_file.write_text(stub_content)
                    print(f"Generated stub: {stub_file}")

    def _generate_stub_content(self, spec: FeatureSpec) -> str:
        """Generate TypeScript stub from spec."""
        lines = [
            f"/**",
            f" * {spec.name}",
            f" * Auto-generated from spec/features/{spec.name}/spec.md",
            f" *",
            f" * Goals:",
        ]
        for goal in spec.goals:
            lines.append(f" * - {goal}")
        lines.extend([
            f" */",
            f"",
            f"export class {self._to_pascal_case(spec.name)} {{",
            f"  // TODO: Implement based on design spec",
            f"  // Design: {spec.design[:100]}...",
            f"",
        ])

        for task in spec.tasks:
            status = "DONE" if task.get("done") else "TODO"
            lines.append(f"  // [{status}] {task.get('task')}")

        lines.extend([
            f"}}",
            f"",
        ])
        return "\n".join(lines)

    def _to_pascal_case(self, name: str) -> str:
        """Convert kebab-case to PascalCase."""
        return "".join(word.capitalize() for word in name.split("-"))

    def generate_schemas(self):
        """Generate API schemas from interfaces."""
        schemas_dir = self.output_dir / "schemas"
        schemas_dir.mkdir(exist_ok=True)

        # Generate OpenAPI stub
        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Schema",
                "version": "1.0.0"
            },
            "paths": {}
        }

        features_path = self.spec_root / "features"
        if features_path.exists():
            for feature_dir in features_path.iterdir():
                if feature_dir.is_dir():
                    spec = self.parse_feature_spec(feature_dir / "spec.md")
                    if spec and spec.interfaces:
                        openapi["paths"][f"/{spec.name}"] = {
                            "get": {
                                "summary": f"Get {spec.name}",
                                "responses": {"200": {"description": "Success"}}
                            }
                        }

        import json
        schema_file = schemas_dir / "openapi.json"
        schema_file.write_text(json.dumps(openapi, indent=2))
        print(f"Generated schema: {schema_file}")

    def generate_docs(self):
        """Generate documentation from specs."""
        docs_dir = self.output_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Generate feature documentation
        features_path = self.spec_root / "features"
        if features_path.exists():
            for feature_dir in features_path.iterdir():
                if feature_dir.is_dir():
                    spec = self.parse_feature_spec(feature_dir / "spec.md")
                    if spec:
                        doc_content = self._generate_doc_content(spec)
                        doc_file = docs_dir / f"{spec.name}.md"
                        doc_file.write_text(doc_content)
                        print(f"Generated doc: {doc_file}")

    def _generate_doc_content(self, spec: FeatureSpec) -> str:
        """Generate documentation markdown."""
        lines = [
            f"# {spec.name}",
            f"",
            f"## Overview",
            f"",
            spec.design if spec.design else "No design specified.",
            f"",
            f"## Goals",
            f"",
        ]
        for goal in spec.goals:
            lines.append(f"- {goal}")

        lines.extend([
            f"",
            f"## Tasks",
            f"",
        ])
        for task in spec.tasks:
            status = "x" if task.get("done") else " "
            lines.append(f"- [{status}] {task.get('task')}")

        return "\n".join(lines)

    def generate_tests(self):
        """Generate test templates from tasks."""
        tests_dir = self.output_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        features_path = self.spec_root / "features"
        if features_path.exists():
            for feature_dir in features_path.iterdir():
                if feature_dir.is_dir():
                    spec = self.parse_feature_spec(feature_dir / "spec.md")
                    if spec and spec.tasks:
                        test_content = self._generate_test_content(spec)
                        test_file = tests_dir / f"{spec.name}.test.ts"
                        test_file.write_text(test_content)
                        print(f"Generated test: {test_file}")

    def _generate_test_content(self, spec: FeatureSpec) -> str:
        """Generate test file from spec tasks."""
        lines = [
            f"/**",
            f" * Tests for {spec.name}",
            f" * Auto-generated from spec/features/{spec.name}/tasks.md",
            f" */",
            f"",
            f'describe("{spec.name}", () => {{',
            f"",
        ]

        for task in spec.tasks:
            test_name = task.get("task", "").replace(" ", "_")
            lines.extend([
                f'  test("{task.get("task")}", () => {{',
                f"    // TODO: Implement test",
                f"    expect(true).toBe(true);",
                f"  }});",
                f"",
            ])

        lines.extend([
            f"}});",
            f"",
        ])
        return "\n".join(lines)


def main():
    spec_root = sys.argv[1] if len(sys.argv) > 1 else "spec"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "generated"

    compiler = SpecCompiler(spec_root, output_dir)
    compiler.compile_all()


if __name__ == "__main__":
    main()
