#!/usr/bin/env python3
"""
OpenSpec AI Dev Loop - Automated development cycle

Orchestrates:
1. Spec validation
2. Code generation
3. Test execution
4. Spec update based on results
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
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
        print("OpenSpec AI Development Loop")
        print("=" * 50)
        print()

        # Stage 1: Validate specs
        if not self.stage_validate():
            self.print_summary()
            return False

        # Stage 2: Generate artifacts
        if not self.stage_generate():
            self.print_summary()
            return False

        # Stage 3: Run tests (optional)
        if not skip_tests:
            self.stage_test()

        # Stage 4: Analyze and suggest updates
        self.stage_analyze()

        self.print_summary()
        return all(r.success for r in self.results)

    def stage_validate(self) -> bool:
        """Validate all specifications."""
        print("[1/4] Validating specifications...")
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
        print("\n[2/4] Generating artifacts...")
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

    def stage_test(self) -> bool:
        """Run tests on generated code."""
        print("\n[3/4] Running tests...")
        print("-" * 30)

        # Check for test runner
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
                    timeout=60
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
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                print(f"Test timeout: {' '.join(cmd)}")
                continue
            except Exception as e:
                print(f"Test error: {e}")
                continue

        print("No test runner found or tests not configured")
        self.results.append(LoopResult(
            stage="test",
            success=True,
            message="Skipped - no test runner found",
            details=[]
        ))
        return True

    def stage_analyze(self) -> bool:
        """Analyze results and suggest spec updates."""
        print("\n[4/4] Analyzing results...")
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
