"""Acceptance checks for the synthetic MVP panel; never copy into agent workspaces."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


def load_module(workspace: Path):
    source = workspace / "src" / "qualitykit.py"
    spec = importlib.util.spec_from_file_location("qualitykit_candidate", source)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load candidate module: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(task_id: str, workspace: Path) -> None:
    module = load_module(workspace)
    if task_id == "bug-normalize-label":
        assert module.normalize_label("  Hello,\t  world!\n ") == "Hello, world!"
        assert module.normalize_label("Already tidy") == "Already tidy"
    elif task_id == "bug-parse-duration":
        for raw, expected in [("12s", 12), ("3M", 180), (" 2h ", 7200), ("0s", 0)]:
            assert module.parse_duration(raw) == expected
        for raw in ["", "-1s", "1.5h", "2d", "3ms", "1 h", "s1"]:
            try:
                module.parse_duration(raw)
            except ValueError:
                continue
            raise AssertionError(f"parse_duration({raw!r}) must raise ValueError")
    elif task_id == "feature-integer-summary":
        assert module.summarize_values(iter([2, 4, 9])) == {
            "count": 3, "min": 2, "max": 9, "mean": 5.0,
        }
        assert module.summarize_values(iter([])) == {
            "count": 0, "min": None, "max": None, "mean": None,
        }
    elif task_id == "feature-slugify":
        assert module.slugify("  Crème brûlée & Tea! ") == "creme-brulee-tea"
        assert module.slugify("東京") == ""
        assert module.slugify("a---b") == "a-b"
    elif task_id == "maintenance-stable-dedupe":
        assert module.deduplicate_names([" Ada ", "ADA", "Grace", "", " grace "]) == ["Ada", "Grace"]
        assert module.deduplicate_names(iter(["A", "a", "B"])) == ["A", "B"]
        class CountingString(str):
            lower_calls = 0

            def strip(self):
                return self

            def lower(self):
                type(self).lower_calls += 1
                return super().lower()

        names = [CountingString(f"person-{number}") for number in range(1000)]
        module.deduplicate_names(names)
        assert CountingString.lower_calls <= 2 * len(names), "deduplication must not rescan every prior name"
    elif task_id == "maintenance-safe-mean":
        assert math.isclose(module.mean(iter([1, 2, 8])), 11 / 3)
        try:
            module.mean(iter([]))
        except ValueError:
            pass
        else:
            raise AssertionError("mean(empty) must raise ValueError")
    else:
        raise ValueError(f"unknown task ID: {task_id}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verifiers.py TASK_ID WORKSPACE")
    verify(sys.argv[1], Path(sys.argv[2]).resolve())
    print("PASS")
