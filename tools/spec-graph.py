#!/usr/bin/env python3
"""
OpenSpec Graph - Generates visualization of spec hierarchy

Outputs:
- ASCII tree view
- JSON dependency graph
- Mermaid diagram
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class SpecNode:
    name: str
    path: str
    node_type: str  # vision, architecture, feature, decision, task
    children: List['SpecNode'] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class SpecGraph:
    def __init__(self, spec_root: str = "spec"):
        self.spec_root = Path(spec_root)
        self.root: SpecNode = SpecNode("OpenSpec", "spec", "root")

    def build_graph(self) -> SpecNode:
        """Build the spec hierarchy graph."""
        # Vision
        vision_path = self.spec_root / "core" / "vision.md"
        if vision_path.exists():
            self.root.children.append(SpecNode("Vision", str(vision_path), "vision"))

        # Architecture
        arch_path = self.spec_root / "core" / "architecture.md"
        if arch_path.exists():
            arch_node = SpecNode("Architecture", str(arch_path), "architecture")
            self.root.children.append(arch_node)

        # Features
        features_path = self.spec_root / "features"
        if features_path.exists():
            features_node = SpecNode("Features", str(features_path), "features")
            for feature_dir in sorted(features_path.iterdir()):
                if feature_dir.is_dir():
                    feature_node = SpecNode(
                        feature_dir.name,
                        str(feature_dir / "spec.md"),
                        "feature"
                    )
                    # Add tasks
                    tasks_path = feature_dir / "tasks.md"
                    if tasks_path.exists():
                        feature_node.children.append(
                            SpecNode("Tasks", str(tasks_path), "task")
                        )
                    features_node.children.append(feature_node)
            self.root.children.append(features_node)

        # Decisions
        decisions_path = self.spec_root / "decisions"
        if decisions_path.exists():
            decisions_node = SpecNode("Decisions", str(decisions_path), "decisions")
            for adr in sorted(decisions_path.glob("ADR-*.md")):
                decisions_node.children.append(
                    SpecNode(adr.stem, str(adr), "decision")
                )
            self.root.children.append(decisions_node)

        return self.root

    def print_ascii_tree(self, node: SpecNode = None, prefix: str = "", is_last: bool = True):
        """Print ASCII tree visualization."""
        if node is None:
            node = self.root
            print("OpenSpec Hierarchy\n")

        connector = "└── " if is_last else "├── "
        type_emoji = {
            "vision": "🎯",
            "architecture": "🏗️",
            "feature": "📦",
            "task": "✅",
            "decision": "📝",
            "features": "📚",
            "decisions": "📋",
            "root": "📁"
        }
        emoji = type_emoji.get(node.node_type, "📄")
        print(f"{prefix}{connector}{emoji} {node.name}")

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            is_last_child = i == len(node.children) - 1
            self.print_ascii_tree(child, new_prefix, is_last_child)

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram."""
        lines = [
            "graph TD",
            "    Root[OpenSpec Framework]",
            "    Root --> Vision[Vision]",
            "    Root --> Arch[Architecture]",
            "    Root --> Features[Features]",
            "    Root --> Decisions[Decisions]",
            "",
            "    style Root fill:#e1f5fe",
            "    style Vision fill:#c8e6c9",
            "    style Arch fill:#fff9c4",
            "    style Features fill:#f3e5f5",
            "    style Decisions fill:#ffe0b2",
        ]

        # Add features
        features_path = self.spec_root / "features"
        if features_path.exists():
            for i, feature_dir in enumerate(sorted(features_path.iterdir())):
                if feature_dir.is_dir():
                    safe_name = feature_dir.name.replace("-", "_")
                    lines.append(f"    Features --> F{i}[{feature_dir.name}]")
                    lines.append(f"    style F{i} fill:#bbdefb")

        lines.append("")
        return "\n".join(lines)

    def generate_json(self) -> dict:
        """Generate JSON representation of the graph."""
        def node_to_dict(node: SpecNode) -> dict:
            return {
                "name": node.name,
                "path": node.path,
                "type": node.node_type,
                "children": [node_to_dict(c) for c in node.children]
            }

        return node_to_dict(self.root)


def main():
    spec_root = sys.argv[1] if len(sys.argv) > 1 else "spec"
    output_format = sys.argv[2] if len(sys.argv) > 2 else "tree"

    graph = SpecGraph(spec_root)
    graph.build_graph()

    if output_format == "tree":
        graph.print_ascii_tree()
    elif output_format == "mermaid":
        print(graph.generate_mermaid())
    elif output_format == "json":
        import json
        print(json.dumps(graph.generate_json(), indent=2))
    else:
        print(f"Unknown format: {output_format}")
        print("Usage: spec-graph.py [spec_root] [tree|mermaid|json]")


if __name__ == "__main__":
    main()
