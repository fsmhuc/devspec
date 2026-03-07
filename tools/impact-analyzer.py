#!/usr/bin/env python3
"""
DevSpec Impact Analyzer - 波及分析引擎

Three-layer impact analysis model:
  Layer 1 (deterministic): git diff → changed files → convention-based test mapping
  Layer 2 (deterministic): spec-graph feature→module mapping → dependent feature tests
  Layer 3 (probabilistic):  AI Agent reads diff, identifies cross-module side effects
                            (executed by the Agent, not by this script)

Usage:
    python3 tools/impact-analyzer.py [--base <ref>] [--config <path>] [--format json|text]
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AffectedTest:
    """A single test file identified as affected by the change."""
    path: str
    reason: str
    type: str = "regression"  # regression | spec_update
    layer: int = 1            # which layer identified it (1, 2, or 3)
    confidence: str = "high"  # high | medium | low


@dataclass
class ImpactReport:
    """Result of impact analysis."""
    changed_files: List[str]
    affected_tests: List[AffectedTest]
    ai_suggestion_needed: bool = False
    cross_module_changes: List[str] = field(default_factory=list)
    base_ref: str = "HEAD~1"
    fallback: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "changed_files": self.changed_files,
            "affected_tests": [asdict(t) for t in self.affected_tests],
            "ai_suggestion_needed": self.ai_suggestion_needed,
            "cross_module_changes": self.cross_module_changes,
            "base_ref": self.base_ref,
            "fallback": self.fallback,
            "error": self.error,
        }

    @property
    def test_paths(self) -> List[str]:
        """Deduplicated list of test file paths."""
        seen: Set[str] = set()
        paths: List[str] = []
        for t in self.affected_tests:
            if t.path not in seen:
                seen.add(t.path)
                paths.append(t.path)
        return paths


# ---------------------------------------------------------------------------
# Default convention mapping rules
# ---------------------------------------------------------------------------

DEFAULT_MAPPING_RULES = [
    # Python: src/**/*.py → tests/**/test_{basename}.py
    {"pattern": r"^(?:src/)?(.+?)/?([^/]+)\.py$", "test_pattern": "tests/**/test_{basename}.py"},
    # TypeScript/JavaScript: src/**/*.ts → tests/**/{basename}.test.ts
    {"pattern": r"^(?:src/)?(.+?)/?([^/]+)\.ts$", "test_pattern": "tests/**/{basename}.test.ts"},
    {"pattern": r"^(?:src/)?(.+?)/?([^/]+)\.tsx$", "test_pattern": "tests/**/{basename}.test.tsx"},
    {"pattern": r"^(?:src/)?(.+?)/?([^/]+)\.js$", "test_pattern": "tests/**/{basename}.test.js"},
    {"pattern": r"^(?:src/)?(.+?)/?([^/]+)\.jsx$", "test_pattern": "tests/**/{basename}.test.jsx"},
    # Go: lib/**/*.go → lib/**/*_test.go
    {"pattern": r"^(.+?)/?([^/]+)\.go$", "test_pattern": "{dir}/{basename}_test.go"},
]


# ---------------------------------------------------------------------------
# ImpactAnalyzer
# ---------------------------------------------------------------------------

class ImpactAnalyzer:
    """Deterministic impact analysis engine (Layer 1 + Layer 2)."""

    def __init__(
        self,
        spec_root: str = "spec",
        config_path: Optional[str] = None,
    ):
        self.spec_root = Path(spec_root)
        self.project_root = Path.cwd()
        self.mapping_rules = self._load_config(config_path)

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_config(self, config_path: Optional[str]) -> List[dict]:
        """Load mapping rules from .devspec/impact.yml or use defaults."""
        candidates = [
            config_path,
            str(self.project_root / ".devspec" / "impact.yml"),
            str(self.project_root / ".devspec" / "impact.yaml"),
            str(self.project_root / ".devspec" / "impact.json"),
        ]
        for path in candidates:
            if path and Path(path).exists():
                return self._parse_config(Path(path))
        return DEFAULT_MAPPING_RULES

    @staticmethod
    def _parse_config(path: Path) -> List[dict]:
        """Parse config file (YAML or JSON)."""
        content = path.read_text()
        if path.suffix == ".json":
            data = json.loads(content)
        else:
            # Minimal YAML-like parser for the simple structure we need
            # Full YAML support would need PyYAML — keep dependency-free
            try:
                import yaml  # type: ignore
                data = yaml.safe_load(content)
            except ImportError:
                # Fallback: treat as JSON
                data = json.loads(content)
        return data.get("mapping_rules", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, base_ref: str = "HEAD~1") -> ImpactReport:
        """Run Layer 1 + Layer 2 analysis and produce an ImpactReport."""
        try:
            changed_files = self.get_git_diff(base_ref)
        except Exception as e:
            return ImpactReport(
                changed_files=[],
                affected_tests=[],
                fallback=True,
                base_ref=base_ref,
                error=f"git diff failed: {e}",
            )

        if not changed_files:
            return ImpactReport(
                changed_files=[],
                affected_tests=[],
                base_ref=base_ref,
            )

        # Layer 1: convention-based test mapping
        layer1_tests = self.map_by_convention(changed_files)

        # Layer 2: spec-graph dependency mapping
        layer2_tests = self.map_by_spec_graph(changed_files)

        # Merge (deduplicate by path — keep the one with lower layer number)
        merged = self._merge_tests(layer1_tests, layer2_tests)

        # Determine if AI Agent should do Layer 3
        cross_module = self._detect_cross_module_changes(changed_files)

        return ImpactReport(
            changed_files=changed_files,
            affected_tests=merged,
            ai_suggestion_needed=len(cross_module) > 0,
            cross_module_changes=cross_module,
            base_ref=base_ref,
        )

    # ------------------------------------------------------------------
    # Layer 1: git diff + convention mapping
    # ------------------------------------------------------------------

    def get_git_diff(self, base_ref: str = "HEAD~1") -> List[str]:
        """Get list of changed files from git diff."""
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", base_ref],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git diff failed: {result.stderr.strip()}")
        return [f for f in result.stdout.strip().split("\n") if f]

    def map_by_convention(self, changed_files: List[str]) -> List[AffectedTest]:
        """Layer 1: Map changed source files to test files by naming convention."""
        tests: List[AffectedTest] = []
        for src_file in changed_files:
            if self._is_test_file(src_file):
                continue
            if not self._is_code_file(src_file):
                continue

            matched = self._find_convention_tests(src_file)
            for test_path in matched:
                tests.append(AffectedTest(
                    path=test_path,
                    reason=f"命名约定匹配: {src_file}",
                    type="regression",
                    layer=1,
                    confidence="high",
                ))
        return tests

    def _find_convention_tests(self, src_file: str) -> List[str]:
        """Find test files matching a source file by convention rules."""
        found: List[str] = []
        src_path = Path(src_file)
        basename = src_path.stem
        dir_part = str(src_path.parent)

        for rule in self.mapping_rules:
            pattern = rule.get("pattern", "")
            test_pattern = rule.get("test_pattern", "")

            match = re.match(pattern, src_file)
            if not match:
                continue

            glob_pattern = test_pattern.replace("{basename}", basename)
            glob_pattern = glob_pattern.replace("{dir}", dir_part)

            for test_path in self.project_root.glob(glob_pattern):
                if test_path.is_file():
                    found.append(str(test_path.relative_to(self.project_root)))

        return found

    # ------------------------------------------------------------------
    # Layer 2: spec-graph dependency mapping
    # ------------------------------------------------------------------

    def map_by_spec_graph(self, changed_files: List[str]) -> List[AffectedTest]:
        """Layer 2: Use spec feature dependencies to find affected tests."""
        tests: List[AffectedTest] = []

        feature_map = self._build_feature_file_map()
        if not feature_map:
            return tests

        affected_features: Set[str] = set()
        for src_file in changed_files:
            for feature, files in feature_map.items():
                if any(src_file.startswith(f) or f in src_file for f in files):
                    affected_features.add(feature)

        for src_file in changed_files:
            match = re.match(r"spec/features/([^/]+)/", src_file)
            if match:
                affected_features.add(match.group(1))

        if not affected_features:
            return tests

        dependency_graph = self._build_dependency_graph()
        all_affected: Set[str] = set(affected_features)
        for feature in affected_features:
            dependents = dependency_graph.get(feature, [])
            all_affected.update(dependents)

        for feature in all_affected:
            feature_tests = self._find_feature_tests(feature)
            for test_path in feature_tests:
                reason = (
                    f"规格依赖: 功能 '{feature}' 受影响"
                    if feature in affected_features
                    else f"规格依赖: 功能 '{feature}' 依赖于已变更的功能"
                )
                tests.append(AffectedTest(
                    path=test_path,
                    reason=reason,
                    type="regression",
                    layer=2,
                    confidence="medium",
                ))

        return tests

    def _build_feature_file_map(self) -> Dict[str, List[str]]:
        """Extract feature → source file mappings from spec files."""
        feature_map: Dict[str, List[str]] = {}
        features_path = self.spec_root / "features"
        if not features_path.exists():
            return feature_map

        for feature_dir in features_path.iterdir():
            if not feature_dir.is_dir():
                continue
            feature_name = feature_dir.name
            spec_file = feature_dir / "spec.md"
            if not spec_file.exists():
                continue

            content = spec_file.read_text()
            files: List[str] = []
            path_patterns = re.findall(
                r'(?:src|lib|app|pkg|internal|cmd)/[\w/.-]+\.\w+', content
            )
            files.extend(path_patterns)
            feature_map[feature_name] = files

        return feature_map

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build feature dependency graph: feature → list of features that depend on it."""
        deps: Dict[str, List[str]] = {}
        features_path = self.spec_root / "features"
        if not features_path.exists():
            return deps

        for feature_dir in features_path.iterdir():
            if not feature_dir.is_dir():
                continue
            feature_name = feature_dir.name
            spec_file = feature_dir / "spec.md"
            if not spec_file.exists():
                continue

            content = spec_file.read_text()
            dep_section = re.search(
                r'##\s*(?:依赖|Dependencies)(.*?)(?=\n##|\Z)', content, re.DOTALL
            )
            if not dep_section:
                continue

            dep_text = dep_section.group(1)
            for other_dir in features_path.iterdir():
                if other_dir.is_dir() and other_dir.name != feature_name:
                    if other_dir.name in dep_text:
                        deps.setdefault(other_dir.name, []).append(feature_name)

        return deps

    def _find_feature_tests(self, feature: str) -> List[str]:
        """Find test files associated with a feature."""
        found: List[str] = []
        patterns = [
            f"tests/**/test_{feature}*.py",
            f"tests/**/{feature}*.test.ts",
            f"tests/**/{feature}*.test.js",
            f"tests/{feature}/**",
        ]
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                if path.is_file():
                    found.append(str(path.relative_to(self.project_root)))
        return found

    # ------------------------------------------------------------------
    # Cross-module detection (triggers Layer 3)
    # ------------------------------------------------------------------

    def _detect_cross_module_changes(self, changed_files: List[str]) -> List[str]:
        """Detect changes that may have cross-module side effects."""
        cross_module: List[str] = []

        cross_module_patterns = [
            # Shared config / global state
            (r'(?:config|settings|env|constants)\.\w+$', "全局配置变更"),
            # Interface / protocol / schema definitions
            (r'(?:interface|schema|proto|types|models)\.\w+$', "接口/类型定义变更"),
            # Shared utilities
            (r'(?:utils?|helpers?|common|shared)/.*\.\w+$', "共享工具模块变更"),
            # Database migrations
            (r'(?:migrations?|alembic)/.*\.\w+$', "数据库迁移变更"),
            # API route definitions
            (r'(?:routes?|api|endpoints?)/.*\.\w+$', "API 路由变更"),
            # Middleware / interceptors
            (r'(?:middleware|interceptors?|hooks?)/.*\.\w+$', "中间件变更"),
        ]

        for src_file in changed_files:
            if self._is_test_file(src_file):
                continue
            for pattern, desc in cross_module_patterns:
                if re.search(pattern, src_file, re.IGNORECASE):
                    cross_module.append(f"{src_file} — {desc}")
                    break

        return cross_module

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_test_file(path: str) -> bool:
        """Check if a file is a test file."""
        name = Path(path).name
        return (
            name.startswith("test_")
            or name.endswith("_test.py")
            or name.endswith("_test.go")
            or ".test." in name
            or ".spec." in name
            or "/tests/" in path
            or path.startswith("tests/")
            or "/__tests__/" in path
        )

    @staticmethod
    def _is_code_file(path: str) -> bool:
        """Check if a file is a source code file."""
        code_exts = {
            ".py", ".ts", ".tsx", ".js", ".jsx",
            ".go", ".rs", ".java", ".kt", ".cs",
            ".rb", ".php", ".swift", ".c", ".cpp", ".h",
        }
        return Path(path).suffix.lower() in code_exts

    @staticmethod
    def _merge_tests(
        layer1: List[AffectedTest],
        layer2: List[AffectedTest],
    ) -> List[AffectedTest]:
        """Merge test lists, deduplicate by path (prefer lower layer)."""
        seen: Dict[str, AffectedTest] = {}
        for t in layer1:
            if t.path not in seen:
                seen[t.path] = t
        for t in layer2:
            if t.path not in seen:
                seen[t.path] = t
        return list(seen.values())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_text(report: ImpactReport) -> str:
    """Format report as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 50)
    lines.append("DevSpec 波及分析报告")
    lines.append("=" * 50)
    lines.append(f"\n基准: {report.base_ref}")
    lines.append(f"变更文件数: {len(report.changed_files)}")
    lines.append(f"受影响测试数: {len(report.affected_tests)}")

    if report.error:
        lines.append(f"\n⚠️  错误: {report.error}")

    if report.fallback:
        lines.append("\n⚠️  波及分析失败，将回退到全量测试")

    if report.changed_files:
        lines.append("\n--- 变更文件 ---")
        for f in report.changed_files:
            lines.append(f"  {f}")

    if report.affected_tests:
        lines.append("\n--- 受影响的测试 ---")
        for t in report.affected_tests:
            marker = "🔴" if t.type == "regression" else "🔵"
            lines.append(f"  {marker} [{t.type}] {t.path}")
            lines.append(f"     原因: {t.reason}")
            lines.append(f"     层级: Layer {t.layer} | 置信度: {t.confidence}")

    if report.ai_suggestion_needed:
        lines.append("\n--- 需要 AI Agent 分析 (Layer 3) ---")
        lines.append("以下变更可能有跨模块影响，建议 Agent 进行补充分析:")
        for c in report.cross_module_changes:
            lines.append(f"  ⚡ {c}")

    lines.append("")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DevSpec Impact Analyzer — 波及分析引擎")
    parser.add_argument("--base", default="HEAD~1", help="Git diff base reference (default: HEAD~1)")
    parser.add_argument("--config", default=None, help="Path to impact config file")
    parser.add_argument("--spec-root", default="spec", help="Spec root directory (default: spec)")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    args = parser.parse_args()

    analyzer = ImpactAnalyzer(
        spec_root=args.spec_root,
        config_path=args.config,
    )
    report = analyzer.analyze(base_ref=args.base)

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(format_text(report))

    # Exit code: 0 = ok, 1 = analysis failed (fallback)
    sys.exit(1 if report.fallback else 0)


if __name__ == "__main__":
    main()
