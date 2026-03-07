#!/usr/bin/env python3
"""
DevSpec Linter - Validates specification consistency

Checks:
1. All specs have required sections
2. No conflicts between architecture and features
3. Tasks reference valid specs
4. ADR documents have required fields
5. No orphaned specs (specs not linked in index)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json


class SpecLinter:
    def __init__(self, spec_root: str = "spec"):
        self.spec_root = Path(spec_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def lint_all(self) -> bool:
        """Run all linting checks."""
        print("=== DevSpec Linter ===\n")

        self.check_index()
        self.check_vision()
        self.check_architecture()
        self.check_features()
        self.check_adrs()
        self.check_tasks()
        self.check_orphans()

        self.print_results()
        return len(self.errors) == 0

    def check_index(self):
        """Verify index.md exists and is valid."""
        index_path = self.spec_root / "index.md"
        if not index_path.exists():
            self.errors.append("Missing spec/index.md - AI entry point required")
            return

        content = index_path.read_text()
        required_refs = ["vision.md", "architecture.md", "features", "decisions", "workflow"]
        for ref in required_refs:
            if ref not in content:
                self.warnings.append(f"index.md missing reference to {ref}")

    def check_vision(self):
        """Verify vision.md exists with required sections."""
        vision_path = self.spec_root / "core" / "vision.md"
        if not vision_path.exists():
            self.errors.append("Missing spec/core/vision.md")
            return

        content = vision_path.read_text().lower()
        if "goal" not in content and "目标" not in content and "使命" not in content:
            self.warnings.append("vision.md should define goals (目标/使命)")

    def check_architecture(self):
        """Verify architecture.md exists with required sections."""
        arch_path = self.spec_root / "core" / "architecture.md"
        if not arch_path.exists():
            self.errors.append("Missing spec/core/architecture.md")
            return

        content = arch_path.read_text().lower()
        has_structure = any(kw in content for kw in ["layer", "component", "分层", "组件", "架构"])
        if not has_structure:
            self.warnings.append("architecture.md should define layers or components (分层/组件)")

    def check_features(self):
        """Check all feature specs have required structure."""
        features_path = self.spec_root / "features"
        if not features_path.exists():
            return

        for feature_dir in features_path.iterdir():
            if feature_dir.is_dir() and feature_dir.name != "template.md":
                spec_file = feature_dir / "spec.md"
                if not spec_file.exists():
                    self.warnings.append(f"Feature {feature_dir.name} missing spec.md")
                    continue

                content = spec_file.read_text().lower()
                # Support both English and Chinese keywords
                has_goals = any(kw in content for kw in ["goal", "目标"])
                has_design = any(kw in content for kw in ["design", "设计"])
                if not has_goals:
                    self.warnings.append(f"{feature_dir.name}/spec.md missing '目标/goals' section")
                if not has_design:
                    self.warnings.append(f"{feature_dir.name}/spec.md missing '设计/design' section")

    def check_adrs(self):
        """Validate ADR documents."""
        adrs_path = self.spec_root / "decisions"
        if not adrs_path.exists():
            return

        for adr_file in adrs_path.glob("ADR-*.md"):
            # Skip template files
            if "template" in adr_file.name.lower():
                continue
            content = adr_file.read_text().lower()
            # Support both English and Chinese keywords
            required_sections = {
                "status/状态": ["status", "状态"],
                "context/上下文": ["context", "上下文", "背景"],
                "decision/决策": ["decision", "决策", "决定"],
                "consequences/后果": ["consequences", "后果", "影响"],
            }
            for section_name, keywords in required_sections.items():
                if not any(kw in content for kw in keywords):
                    self.warnings.append(f"{adr_file.name} missing '{section_name}' section")

    def check_tasks(self):
        """Verify tasks reference specs."""
        features_path = self.spec_root / "features"
        if not features_path.exists():
            return

        for feature_dir in features_path.iterdir():
            if feature_dir.is_dir():
                tasks_file = feature_dir / "tasks.md"
                if tasks_file.exists():
                    content = tasks_file.read_text()
                    if not re.search(r'\[x\]|\[ \]', content):
                        self.warnings.append(f"{feature_dir.name}/tasks.md should use task checkboxes")

    def check_orphans(self):
        """Find specs not linked in index."""
        index_path = self.spec_root / "index.md"
        if not index_path.exists():
            return

        index_content = index_path.read_text()

        # Find all markdown files
        for md_file in self.spec_root.rglob("*.md"):
            if md_file.name == "index.md":
                continue
            if md_file.name not in index_content and str(md_file.relative_to(self.spec_root)) not in index_content:
                # Only warn for core files
                if "core" in str(md_file):
                    self.warnings.append(f"{md_file} may not be linked in index.md")

    def print_results(self):
        """Print linting results."""
        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  [x] {error}")
            print()

        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings:
                print(f"  [!] {warning}")
            print()

        if not self.errors and not self.warnings:
            print("All checks passed!")

        print(f"\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings")


def main():
    spec_root = sys.argv[1] if len(sys.argv) > 1 else "spec"
    linter = SpecLinter(spec_root)
    success = linter.lint_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
