#!/usr/bin/env python3
"""
DevSpec AI Dev Loop - Automated development cycle

Orchestrates:
1. Spec validation
2. Code generation
3. Impact analysis
4. Test execution
5. Spec update based on results
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LoopResult:
    stage: str
    success: bool
    message: str
    details: List[str]


class AIDevLoop:
    def __init__(self, spec_root: str = "spec"):
        self.spec_root = Path(spec_root)
        self.results: List[LoopResult] = []

    def run(self, skip_tests: bool = False) -> bool:
        """Run the complete AI development loop."""
        print("=" * 50)
        print("DevSpec AI Development Loop")
        print("=" * 50)
        print()

        if not self.stage_validate():
            self.print_summary()
            return False

        if not self.stage_generate():
            self.print_summary()
            return False

        affected_tests: Optional[List[str]] = None
        if not skip_tests:
            affected_tests = self.stage_impact_analysis()

        if not skip_tests:
            if not self.stage_test(affected_tests):
                self.print_summary()
                return False

        self.stage_analyze()

        self.print_summary()
        return all(r.success for r in self.results)

    def stage_validate(self) -> bool:
        """Validate all specifications."""
        print("[1/5] Validating specifications...")
        print("-" * 30)

        linter_path = Path(__file__).parent / "spec-linter.py"
        if linter_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(linter_path), str(self.spec_root)],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)

                success = result.returncode == 0
                self.results.append(LoopResult(
                    stage="validate",
                    success=success,
                    message="Specification validation complete",
                    details=result.stdout.split("\n")
                ))
                return success
            except Exception as e:
                print(f"Error running linter: {e}")

        # Fallback to basic validation
        checks = []
        index = self.spec_root / "index.md"
        if index.exists():
            checks.append("[x] index.md exists")
        else:
            checks.append("[ ] index.md missing")

        vision = self.spec_root / "core" / "vision.md"
        if vision.exists():
            checks.append("[x] vision.md exists")
        else:
            checks.append("[ ] vision.md missing")

        arch = self.spec_root / "core" / "architecture.md"
        if arch.exists():
            checks.append("[x] architecture.md exists")
        else:
            checks.append("[ ] architecture.md missing")

        for check in checks:
            print(check)

        success = all("[x]" in c for c in checks)
        self.results.append(LoopResult(
            stage="validate",
            success=success,
            message="Basic validation complete",
            details=checks
        ))
        return success

    def stage_generate(self) -> bool:
        """Generate code artifacts from specs."""
        print("\n[2/5] Generating artifacts...")
        print("-" * 30)

        compiler_path = Path(__file__).parent / "spec-compiler.py"
        if compiler_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(compiler_path), str(self.spec_root)],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)

                success = result.returncode == 0
                self.results.append(LoopResult(
                    stage="generate",
                    success=success,
                    message="Artifact generation complete",
                    details=result.stdout.split("\n")
                ))
                return True
            except Exception as e:
                print(f"Error running compiler: {e}")

        print("Compiler not available, skipping artifact generation")
        self.results.append(LoopResult(
            stage="generate",
            success=True,
            message="Skipped - no compiler available",
            details=[]
        ))
        return True

    def stage_impact_analysis(self) -> Optional[List[str]]:
        """Run impact analysis to determine which tests are affected."""
        print("\n[3/5] Running impact analysis...")
        print("-" * 30)

        analyzer_path = Path(__file__).parent / "impact-analyzer.py"
        if not analyzer_path.exists():
            print("Impact analyzer not available, skipping")
            self.results.append(LoopResult(
                stage="impact",
                success=True,
                message="Skipped - impact analyzer not available",
                details=[]
            ))
            return None

        try:
            result = subprocess.run(
                [sys.executable, str(analyzer_path), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            import json
            report = json.loads(result.stdout)

            affected = [t["path"] for t in report.get("affected_tests", [])]
            changed_count = len(report.get("changed_files", []))
            ai_needed = report.get("ai_suggestion_needed", False)

            print(f"Changed files: {changed_count}")
            print(f"Affected tests: {len(affected)}")
            if ai_needed:
                print("⚡ Cross-module changes detected — AI Layer 3 analysis recommended")
                for c in report.get("cross_module_changes", []):
                    print(f"  {c}")

            if report.get("fallback"):
                print("⚠️  Impact analysis failed, falling back to full test run")
                self.results.append(LoopResult(
                    stage="impact",
                    success=True,
                    message=f"Fallback to full test run: {report.get('error', 'unknown')}",
                    details=[]
                ))
                return None

            self.results.append(LoopResult(
                stage="impact",
                success=True,
                message=f"Identified {len(affected)} affected tests from {changed_count} changed files",
                details=affected
            ))
            return affected if affected else None

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Failed to parse impact report: {e}")
            print("Falling back to full test run")
            self.results.append(LoopResult(
                stage="impact",
                success=True,
                message=f"Parse error, fallback to full test run: {e}",
                details=[]
            ))
            return None
        except subprocess.TimeoutExpired:
            print("Impact analysis timed out, falling back to full test run")
            self.results.append(LoopResult(
                stage="impact",
                success=True,
                message="Timeout, fallback to full test run",
                details=[]
            ))
            return None
        except Exception as e:
            print(f"Impact analysis error: {e}")
            print("Falling back to full test run")
            self.results.append(LoopResult(
                stage="impact",
                success=True,
                message=f"Error, fallback to full test run: {e}",
                details=[]
            ))
            return None

    def stage_test(self, affected_tests: Optional[List[str]] = None) -> bool:
        """Run tests. If affected_tests provided, run targeted tests only."""
        print("\n[4/5] Running tests...")
        print("-" * 30)

        if affected_tests:
            return self._run_targeted_tests(affected_tests)

        test_commands = [
            ["npm", "test"],
            ["yarn", "test"],
            ["pnpm", "test"],
            ["pytest"],
            ["go", "test", "./..."],
        ]

        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"Tests passed: {' '.join(cmd)}")
                    self.results.append(LoopResult(
                        stage="test",
                        success=True,
                        message=f"Tests passed with {cmd[0]}",
                        details=result.stdout.split("\n")
                    ))
                    return True
                else:
                    # Test runner found but tests failed — this is blocking
                    print(f"Tests FAILED: {' '.join(cmd)}")
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(result.stderr)
                    self.results.append(LoopResult(
                        stage="test",
                        success=False,
                        message=f"Tests failed with {cmd[0]} (exit={result.returncode})",
                        details=(result.stdout + "\n" + result.stderr).split("\n")
                    ))
                    return False
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                print(f"Test timeout: {' '.join(cmd)}")
                self.results.append(LoopResult(
                    stage="test",
                    success=False,
                    message=f"Test timed out with {cmd[0]}",
                    details=[]
                ))
                return False
            except Exception as e:
                print(f"Test error: {e}")
                continue

        # No test runner found — warn (not silent)
        print("WARNING: No test runner found. Configure a test runner for TDD enforcement.")
        print("  Supported: npm test, yarn test, pnpm test, pytest, go test")
        self.results.append(LoopResult(
            stage="test",
            success=True,
            message="WARNING: No test runner found — configure one for TDD enforcement",
            details=["No test runner detected. See spec/workflow/testing-strategy.md"]
        ))
        return True

    def _run_targeted_tests(self, affected_tests: List[str]) -> bool:
        """Run only the specified affected tests (targeted test execution)."""
        print(f"  Running {len(affected_tests)} targeted test(s)...")
        for t in affected_tests:
            print(f"    → {t}")
        print()

        # Group tests by runner type
        py_tests = [t for t in affected_tests if t.endswith('.py')]
        ts_js_tests = [t for t in affected_tests if t.endswith(('.test.ts', '.test.tsx', '.test.js', '.test.jsx'))]
        go_tests = [t for t in affected_tests if t.endswith('_test.go')]

        any_ran = False
        all_passed = True

        # Python tests via pytest
        if py_tests:
            any_ran = True
            existing = [t for t in py_tests if Path(t).exists()]
            if existing:
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", "--tb=short", "-q"] + existing,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    print(result.stdout)
                    if result.returncode != 0:
                        if result.stderr:
                            print(result.stderr)
                        self.results.append(LoopResult(
                            stage="test",
                            success=False,
                            message=f"Targeted pytest failed ({len(existing)} files)",
                            details=result.stdout.split("\n")
                        ))
                        all_passed = False
                except FileNotFoundError:
                    print("  pytest not found, skipping Python tests")
                except subprocess.TimeoutExpired:
                    print("  pytest timed out")
                    self.results.append(LoopResult(
                        stage="test",
                        success=False,
                        message="Targeted pytest timed out",
                        details=[]
                    ))
                    all_passed = False
            else:
                print(f"  Skipped {len(py_tests)} Python test(s) — files not found")

        # TypeScript/JavaScript tests via npx jest (or npm test with filter)
        if ts_js_tests:
            any_ran = True
            existing = [t for t in ts_js_tests if Path(t).exists()]
            if existing:
                try:
                    result = subprocess.run(
                        ["npx", "jest", "--no-coverage"] + existing,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    print(result.stdout)
                    if result.returncode != 0:
                        if result.stderr:
                            print(result.stderr)
                        self.results.append(LoopResult(
                            stage="test",
                            success=False,
                            message=f"Targeted jest failed ({len(existing)} files)",
                            details=result.stdout.split("\n")
                        ))
                        all_passed = False
                except FileNotFoundError:
                    print("  jest/npx not found, skipping JS/TS tests")
                except subprocess.TimeoutExpired:
                    print("  jest timed out")
                    self.results.append(LoopResult(
                        stage="test",
                        success=False,
                        message="Targeted jest timed out",
                        details=[]
                    ))
                    all_passed = False
            else:
                print(f"  Skipped {len(ts_js_tests)} JS/TS test(s) — files not found")

        # Go tests
        if go_tests:
            any_ran = True
            # Go tests are run per package (directory)
            go_packages = list({str(Path(t).parent) for t in go_tests if Path(t).exists()})
            if go_packages:
                pkg_args = ['./' + p + '/...' for p in go_packages]
                try:
                    result = subprocess.run(
                        ["go", "test"] + pkg_args,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    print(result.stdout)
                    if result.returncode != 0:
                        if result.stderr:
                            print(result.stderr)
                        self.results.append(LoopResult(
                            stage="test",
                            success=False,
                            message=f"Targeted go test failed ({len(go_packages)} packages)",
                            details=result.stdout.split("\n")
                        ))
                        all_passed = False
                except FileNotFoundError:
                    print("  go not found, skipping Go tests")
                except subprocess.TimeoutExpired:
                    print("  go test timed out")
                    self.results.append(LoopResult(
                        stage="test",
                        success=False,
                        message="Targeted go test timed out",
                        details=[]
                    ))
                    all_passed = False
            else:
                print(f"  Skipped {len(go_tests)} Go test(s) — files not found")

        if not any_ran:
            print("  No targeted tests could be executed (files not found or runners unavailable)")
            print("  Falling back to full test run...")
            return self.stage_test(affected_tests=None)

        if all_passed:
            self.results.append(LoopResult(
                stage="test",
                success=True,
                message=f"Targeted tests passed ({len(affected_tests)} files)",
                details=affected_tests
            ))

        return all_passed

    def stage_analyze(self) -> bool:
        """Analyze results and suggest spec updates."""
        print("\n[5/5] Analyzing results...")
        print("-" * 30)

        suggestions = []

        # Check for failed stages
        failed_stages = [r for r in self.results if not r.success]
        if failed_stages:
            for stage in failed_stages:
                suggestions.append(f"Fix issues in {stage.stage} stage")

        # Check for incomplete tasks
        features_path = self.spec_root / "features"
        if features_path.exists():
            import re
            for feature_dir in features_path.iterdir():
                if feature_dir.is_dir():
                    tasks_file = feature_dir / "tasks.md"
                    if tasks_file.exists():
                        content = tasks_file.read_text()
                        incomplete = re.findall(r"- \[ \] (.+)", content)
                        for task in incomplete:
                            suggestions.append(f"Complete task in {feature_dir.name}: {task}")

        if suggestions:
            print("Suggested actions:")
            for s in suggestions:
                print(f"  - {s}")
        else:
            print("No issues found. Specs are healthy!")

        self.results.append(LoopResult(
            stage="analyze",
            success=True,
            message=f"Analysis complete. {len(suggestions)} suggestions.",
            details=suggestions
        ))
        return True

    def print_summary(self):
        """Print loop summary."""
        print("\n" + "=" * 50)
        print("Loop Summary")
        print("=" * 50)

        for result in self.results:
            status = "PASS" if result.success else "FAIL"
            print(f"  [{status}] {result.stage}: {result.message}")

        all_success = all(r.success for r in self.results)
        print()
        if all_success:
            print("All stages completed successfully!")
        else:
            print("Some stages failed. Review the output above.")


def main():
    spec_root = sys.argv[1] if len(sys.argv) > 1 else "spec"
    skip_tests = "--skip-tests" in sys.argv

    loop = AIDevLoop(spec_root)
    success = loop.run(skip_tests=skip_tests)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
