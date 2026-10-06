#!/usr/bin/env python3
"""Run isolated Hermes/OpenRouter trajectories for a fixed model panel."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import signal
import shutil
import stat
import statistics
import sys
import subprocess
import tempfile
import time
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / "benchmark"
FREEZE_PATH = BENCHMARK / "freeze.json"
TASKS_PATH = BENCHMARK / "tasks.json"
VERIFIER_PATH = BENCHMARK / "verifiers.py"
RESULTS_DIR = ROOT / "runs"
RESULTS_PATH = RESULTS_DIR / "results.jsonl"
SCORES_PATH = RESULTS_DIR / "scores.jsonl"
BLIND_DIR = RESULTS_DIR / "blind"
DOCKER_IMAGE = "nousresearch/hermes-sandbox:desktop"
AGENT_TMP_ROOT = ROOT.parent / ".coding-agent-efficiency-benchmark-tmp"
DOCKER_CONTEXT = "desktop-linux"


class BenchmarkError(Exception):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"Impossible de lire {path.relative_to(ROOT)}: {type(exc).__name__}") from exc


def tasks_by_id() -> dict[str, dict]:
    tasks = read_json(TASKS_PATH)
    result = {}
    for task in tasks:
        if task.get("id") in result:
            raise BenchmarkError(f"ID de tâche dupliqué: {task.get('id')}")
        fixture = (BENCHMARK / task["workspace"]).resolve()
        if not fixture.is_relative_to(BENCHMARK / "fixtures") or not fixture.is_dir():
            raise BenchmarkError(f"Fixture manquante ou hors périmètre pour {task.get('id')}")
        unsafe = unsafe_workspace_reason(fixture)
        if unsafe:
            raise BenchmarkError(f"Fixture dangereuse {task.get('id')}: {unsafe}")
        result[task["id"]] = task
    return result


def panel_hash() -> str:
    return panel_hash_for(BENCHMARK)


def panel_hash_for(panel_root: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    tasks_path = panel_root / "tasks.json"
    verifier_path = panel_root / "verifiers.py"
    reference_path = panel_root / "reference_solutions.json"
    paths = [tasks_path, verifier_path, reference_path]
    for path in paths:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 4 * 1024 * 1024:
            raise BenchmarkError(f"Fichier du panel non régulier ou trop volumineux: {path.relative_to(panel_root)}")
    fixtures_root = (panel_root / "fixtures").resolve()
    for task in read_json(tasks_path):
        fixture = (panel_root / task["workspace"]).resolve()
        if not fixture.is_relative_to(fixtures_root) or not fixture.is_dir():
            raise BenchmarkError(f"Fixture absente ou hors périmètre: {task.get('id')}")
        unsafe = unsafe_workspace_reason(fixture)
        if unsafe:
            raise BenchmarkError(f"Fixture dangereuse {task.get('id')}: {unsafe}")
        paths.extend(path for path in fixture.rglob("*") if path.is_file())
    for path in sorted(paths):
        digest.update(str(path.relative_to(panel_root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def prepare_run_snapshots(freeze: dict) -> tuple[str, str]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    freeze_dir = RESULTS_DIR / "freezes"
    freeze_dir.mkdir(parents=True, exist_ok=True)
    freeze_path = freeze_dir / f"{freeze['freeze_sha256']}.json"
    raw_freeze = FREEZE_PATH.read_bytes()
    if __import__("hashlib").sha256(raw_freeze).hexdigest() != freeze["freeze_sha256"]:
        raise BenchmarkError("Le freeze a changé pendant la préparation.")
    if freeze_path.exists():
        if freeze_path.read_bytes() != raw_freeze:
            raise BenchmarkError("Collision ou altération du snapshot de freeze.")
    else:
        freeze_path.write_bytes(raw_freeze)

    panel_dir = RESULTS_DIR / "panels" / freeze["task_panel_sha256"]
    if not panel_dir.exists():
        panel_dir.parent.mkdir(parents=True, exist_ok=True)
        panel_dir.mkdir()
        for filename in ("tasks.json", "verifiers.py", "reference_solutions.json"):
            shutil.copy2(BENCHMARK / filename, panel_dir / filename)
        shutil.copytree(BENCHMARK / "fixtures", panel_dir / "fixtures")
    if panel_hash_for(panel_dir) != freeze["task_panel_sha256"]:
        raise BenchmarkError("Le snapshot local du panel ne correspond pas à son empreinte gelée.")
    return str(freeze_path.relative_to(ROOT)), str(panel_dir.relative_to(ROOT))


def load_freeze(require_complete: bool = True) -> dict:
    freeze = read_json(FREEZE_PATH)
    if not require_complete:
        return freeze
    required = [
        "frozen_at_utc", "hermes_version", "run_order_seed",
        "price_snapshot", "spend_cap_usd_per_run", "total_openrouter_budget_usd",
        "task_panel_sha256", "hermes_reasoning_effort", "hermes_docker_image_id",
        "quality_threshold_score",
    ]
    missing = [key for key in required if freeze.get(key) in (None, "", "TBD")]
    models = freeze.get("openrouter_models")
    if not isinstance(models, list) or not models or any(not isinstance(m, str) or not m.strip() for m in models) or len(set(models)) != len(models):
        missing.append("openrouter_models (IDs fixes uniques)")
    if missing:
        raise BenchmarkError("Freeze incomplet : " + ", ".join(missing) + ". Compléter benchmark/freeze.json avant tout run.")
    if not isinstance(freeze["spend_cap_usd_per_run"], (int, float)) or freeze["spend_cap_usd_per_run"] <= 0:
        raise BenchmarkError("spend_cap_usd_per_run doit être strictement positif.")
    if not isinstance(freeze["total_openrouter_budget_usd"], (int, float)) or freeze["total_openrouter_budget_usd"] <= 0:
        raise BenchmarkError("total_openrouter_budget_usd doit être strictement positif.")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", freeze["hermes_docker_image_id"]):
        raise BenchmarkError("hermes_docker_image_id doit être l'ID local sha256 complet de l'image Hermes.")
    if any(not re.fullmatch(r"[A-Za-z0-9_.:-]+/[A-Za-z0-9_.:-]+", model) for model in models):
        raise BenchmarkError("Chaque modèle OpenRouter doit être un ID provider/model fixe.")
    max_budget = freeze["spend_cap_usd_per_run"] * len(tasks_by_id()) * freeze.get("repetitions", 3) * len(models)
    if round(freeze["total_openrouter_budget_usd"], 6) > round(max_budget, 6):
        raise BenchmarkError("Le budget OpenRouter total excède le plafond/run × tâches × répétitions × modèles.")
    if freeze.get("openrouter_key_limit_confirmed") is not True:
        raise BenchmarkError("Confirmer dans benchmark/freeze.json que la limite de dépense de la clé OpenRouter est réglée au budget total déclaré.")
    if freeze["task_panel_sha256"] != panel_hash():
        raise BenchmarkError("task_panel_sha256 ne correspond pas au panel courant; lancer panel-hash et mettre à jour le freeze.")
    if not isinstance(freeze.get("timeout_seconds"), int) or not 60 <= freeze["timeout_seconds"] <= 3600:
        raise BenchmarkError("timeout_seconds doit être un entier entre 60 et 3600 secondes.")
    if not isinstance(freeze.get("repetitions"), int) or not 1 <= freeze["repetitions"] <= 3:
        raise BenchmarkError("Le MVP impose entre une et trois répétitions.")
    if not isinstance(freeze["quality_threshold_score"], (int, float)) or not 1 <= freeze["quality_threshold_score"] <= 5:
        raise BenchmarkError("quality_threshold_score doit être compris entre 1 et 5.")
    if not isinstance(freeze["run_order_seed"], int):
        raise BenchmarkError("run_order_seed doit être un entier.")
    try:
        frozen_at = dt.datetime.fromisoformat(freeze["frozen_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise BenchmarkError("frozen_at_utc doit être une date ISO-8601 UTC.") from exc
    if frozen_at.utcoffset() != dt.timedelta(0):
        raise BenchmarkError("frozen_at_utc doit utiliser le fuseau UTC.")
    import hashlib

    freeze["freeze_sha256"] = hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest()
    return freeze


def local_docker_environment() -> dict[str, str]:
    env = os.environ.copy()
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH", "DOCKER_CONFIG", "CONTAINER_HOST"):
        env.pop(key, None)
    env["DOCKER_CONTEXT"] = DOCKER_CONTEXT
    return env


def docker_command(*args: str) -> list[str]:
    return ["docker", "--context", DOCKER_CONTEXT, *args]


def command_version(command: list[str], *, env: dict[str, str] | None = None) -> str:
    try:
        completed = subprocess.run(command, check=False, text=True, capture_output=True, timeout=15, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (completed.stdout or completed.stderr).strip().splitlines()[0] if completed.returncode == 0 and (completed.stdout or completed.stderr).strip() else ""


def preflight(complete: bool) -> dict:
    tasks = tasks_by_id()
    freeze = load_freeze(require_complete=complete)
    checks = {
        "tasks": len(tasks) == 6,
        "hermes": bool(command_version(["hermes", "--version"])),
    }
    if complete:
        checks["frozen_hermes_version_matches"] = freeze["hermes_version"] == command_version(["hermes", "--version"])
        docker_env = local_docker_environment()
        active_context = command_version(["docker", "context", "show"], env=docker_env)
        checks["docker_local_context"] = active_context == DOCKER_CONTEXT
        checks["docker_engine"] = bool(command_version(docker_command("info", "--format", "{{.ServerVersion}}"), env=docker_env))
        active_image_id = command_version(docker_command("image", "inspect", "--format", "{{.Id}}", DOCKER_IMAGE), env=docker_env)
        try:
            checks["docker_image"] = subprocess.run(
                docker_command("image", "inspect", DOCKER_IMAGE), env=docker_env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=20,
            ).returncode == 0
        except (OSError, subprocess.SubprocessError):
            checks["docker_image"] = False
        checks["hermes_image_id_matches"] = bool(active_image_id) and active_image_id == freeze["hermes_docker_image_id"]
        checks["hermes_provider"] = freeze.get("provider") in (None, "openrouter")
        checks["reasoning_effort"] = freeze.get("hermes_reasoning_effort") in {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
    return {"checks": checks, "freeze": freeze, "task_count": len(tasks)}


def ensure_preflight(complete: bool = True) -> dict:
    report = preflight(complete)
    failed = [name for name, passed in report["checks"].items() if not passed]
    if failed:
        raise BenchmarkError("Préflight échoué : " + ", ".join(failed) + ". Voir README.md / docs/MVP_PROTOCOL.md.")
    return report


def sanitize_environment(*, docker_image: str = DOCKER_IMAGE) -> dict[str, str]:
    env = os.environ.copy()
    # Hermes keeps provider credentials in its host API process. Its Docker
    # backend scrubs them before launching tool subprocesses.
    secret_name = re.compile(r"(API.?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE.?KEY)", re.I)
    for key in list(env):
        if secret_name.search(key) and key.upper() != "OPENROUTER_API_KEY":
            env.pop(key, None)
    env["TERMINAL_ENV"] = "docker"
    env["TERMINAL_DOCKER_IMAGE"] = docker_image
    env["TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE"] = "true"
    env["TERMINAL_DOCKER_NETWORK"] = "false"
    env["TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES"] = "false"
    env["TERMINAL_CONTAINER_PERSISTENT"] = "false"
    env["TERMINAL_DOCKER_IMAGE_PINNED"] = "1"
    env["TERMINAL_DOCKER_VOLUMES"] = "[]"
    env["TERMINAL_DOCKER_FORWARD_ENV"] = "[]"
    env["TERMINAL_DOCKER_ENV"] = "{}"
    env["TERMINAL_DOCKER_EXTRA_ARGS"] = "[]"
    env["TERMINAL_DOCKER_SHARED_CONTAINER_KEY"] = ""
    env["TERMINAL_DOCKER_RUN_AS_HOST_USER"] = "false"
    env["TERMINAL_CONTAINER_CPU"] = "1"
    env["TERMINAL_CONTAINER_MEMORY"] = "1024"
    env["TERMINAL_CONTAINER_DISK"] = "2048"
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH", "DOCKER_CONFIG", "CONTAINER_HOST"):
        env.pop(key, None)
    env["DOCKER_CONTEXT"] = DOCKER_CONTEXT
    return env


def parse_jsonl(text: str) -> list[dict]:
    events = []
    for line in text.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def hermes_usage(path: Path) -> dict:
    if not path.is_file():
        return {"input_tokens": None, "output_tokens": None, "reasoning_tokens": None, "cached_input_tokens": None, "cost_usd": None, "api_calls": None, "tool_calls": None, "retries": None}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"input_tokens": None, "output_tokens": None, "reasoning_tokens": None, "cached_input_tokens": None, "cost_usd": None, "api_calls": None, "tool_calls": None, "retries": None}
    return {
        "input_tokens": report.get("input_tokens"),
        "output_tokens": report.get("output_tokens"),
        "reasoning_tokens": report.get("reasoning_tokens"),
        "cached_input_tokens": report.get("cache_read_tokens", report.get("cached_input_tokens", report.get("cached_input_tokens_count"))),
        "cache_creation_tokens": report.get("cache_creation_tokens", report.get("cache_write_tokens")),
        "cache_charge_usd": report.get("cache_charge_usd", report.get("cache_cost_usd")),
        "cost_usd": report.get("total_including_auxiliary", report.get("total_cost_usd", report.get("estimated_cost_usd"))),
        "api_calls": report.get("api_calls"),
        "tool_calls": report.get("tool_calls"),
        "retries": report.get("retries", report.get("retry_count")),
        "served_provider": report.get("provider", report.get("provider_name")),
        "usage_status": report.get("status"),
    }


def unsafe_workspace_reason(workspace: Path) -> str | None:
    """Reject links/special files before the host copies or verifies agent output."""
    if not workspace.is_dir() or workspace.is_symlink():
        return "workspace_missing_or_replaced"
    inode_counts: dict[tuple[int, int], int] = {}
    entries = []
    file_count = 0
    total_bytes = 0
    try:
        for current, directories, filenames in os.walk(workspace, followlinks=False):
            for name in [*directories, *filenames]:
                path = Path(current) / name
                info = path.lstat()
                if stat.S_ISLNK(info.st_mode):
                    return "symlink_in_workspace"
                if stat.S_ISDIR(info.st_mode):
                    continue
                if not stat.S_ISREG(info.st_mode):
                    return "special_file_in_workspace"
                file_count += 1
                total_bytes += info.st_size
                if info.st_size > 64 * 1024 * 1024 or total_bytes > 64 * 1024 * 1024:
                    return "workspace_size_limit"
                if file_count > 10000:
                    return "workspace_file_count_limit"
                inode = (info.st_dev, info.st_ino)
                inode_counts[inode] = inode_counts.get(inode, 0) + 1
                entries.append((inode, info.st_nlink))
    except OSError:
        return "workspace_unreadable"
    if any(link_count > inode_counts[inode] for inode, link_count in entries):
        return "external_hardlink_in_workspace"
    return None


def run_verifier(task_id: str, workspace: Path, docker_image_id: str, run_id: str) -> tuple[bool, str]:
    """Run candidate imports in a networkless, read-only container, never on the host."""
    container_name = f"coding-bench-verifier-{run_id}"
    command = [
        *docker_command("run"), "--rm", "--name", container_name,
        "--network=none", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--pids-limit=64", "--memory=512m", "--cpus=1",
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=32m",
        "--user", "65534:65534",
        "--env", "PYTHONDONTWRITEBYTECODE=1", "--workdir", "/workspace",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--mount", f"type=bind,source={VERIFIER_PATH},target=/opt/verifiers.py,readonly",
        "--entrypoint", "python3", docker_image_id, "/opt/verifiers.py", task_id, "/workspace",
    ]
    try:
        completed = subprocess.run(
            command, cwd=ROOT, env=local_docker_environment(), stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=45, check=False,
        )
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(docker_command("rm", "--force", container_name), env=local_docker_environment(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=False)
        except (OSError, subprocess.SubprocessError):
            pass
        return False, "verifier_timeout"
    except (OSError, subprocess.SubprocessError):
        return False, "verifier_unavailable"
    return completed.returncode == 0, "passed" if completed.returncode == 0 else f"failed_exit_{completed.returncode}"


def execute(task: dict, system: str, model: str, trial: int, freeze: dict, *, diagnostic: bool = False, order_index: int | None = None) -> dict:
    if system != "hermes":
        raise BenchmarkError("Ce protocole lance uniquement Hermes avec OpenRouter.")
    run_id = str(uuid.uuid4())
    fixture = (BENCHMARK / task["workspace"]).resolve()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    temp_root = AGENT_TMP_ROOT / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"coding-bench-{run_id}-", dir=temp_root) as temporary:
        workspace = Path(temporary) / "workspace"
        shutil.copytree(fixture, workspace)
        meta_dir = Path(temporary) / "meta"
        meta_dir.mkdir()
        usage_path = meta_dir / "hermes-usage.json"
        command = [
            "hermes", "-z", task["prompt"], "--usage-file", str(usage_path),
            "--provider", "openrouter", "--model", model, "--in", str(workspace),
            "--reasoning", freeze["hermes_reasoning_effort"], "--safe-mode", "-t", "terminal",
        ]
        started_at = utc_now()
        started = time.monotonic()
        timed_out = False
        exit_code = None
        process = subprocess.Popen(
            command, cwd=workspace, env=sanitize_environment(docker_image=freeze["hermes_docker_image_id"]),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True,
            start_new_session=(os.name == "posix"),
        )
        try:
            process.communicate(timeout=freeze["timeout_seconds"])
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            process.communicate(timeout=10)
        finally:
            if process.poll() is not None and os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        agent_elapsed = time.monotonic() - started
        verifier_started = time.monotonic()
        unsafe_reason = unsafe_workspace_reason(workspace)
        if unsafe_reason:
            verifier_passed, verifier_status = False, unsafe_reason
        else:
            verifier_passed, verifier_status = run_verifier(task["id"], workspace, freeze["hermes_docker_image_id"], run_id)
        verifier_elapsed = time.monotonic() - verifier_started
        usage = hermes_usage(usage_path)
        over_cap = isinstance(usage.get("cost_usd"), (int, float)) and usage["cost_usd"] > freeze["spend_cap_usd_per_run"]
        artifact = RESULTS_DIR / "workspaces" / run_id
        if unsafe_reason:
            artifact = None
        else:
            shutil.copytree(workspace, artifact)
        result = {
            "run_id": run_id, "protocol_revision": freeze["protocol_revision"],
            "task_id": task["id"], "category": task["category"], "system": "hermes",
            "model": model, "provider": "openrouter", "served_provider": usage.get("served_provider"),
            "model_calls": usage.get("api_calls"), "tool_calls": usage.get("tool_calls"),
            "retries": usage.get("retries"), "trial": trial, "panel_order_index": order_index,
            "started_at_utc": started_at, "ended_at_utc": utc_now(),
            "elapsed_seconds": round(agent_elapsed + verifier_elapsed, 3),
            "agent_elapsed_seconds": round(agent_elapsed, 3), "verifier_elapsed_seconds": round(verifier_elapsed, 3),
            "agent_exit_code": exit_code, "timed_out": timed_out,
            "verifier_passed": verifier_passed, "verifier_status": verifier_status,
            "unsafe_workspace": bool(unsafe_reason), "success": verifier_passed and not timed_out,
            "rubric_score": None, "rubric_max": 5, "diagnostic": diagnostic,
            "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
            "reasoning_tokens": usage.get("reasoning_tokens"), "cached_input_tokens": usage.get("cached_input_tokens"),
            "cache_creation_tokens": usage.get("cache_creation_tokens"), "cache_charge_usd": usage.get("cache_charge_usd"),
            "cost_usd": usage.get("cost_usd"), "quality_threshold_score": freeze["quality_threshold_score"],
            "api_calls": usage.get("api_calls"), "spend_cap_usd": freeze["spend_cap_usd_per_run"],
            "spend_cap_exceeded": over_cap, "artifact_path": str(artifact.relative_to(ROOT)) if artifact else None,
            "freeze_hash": freeze["freeze_sha256"], "task_panel_sha256": panel_hash(),
            "hermes_docker_image_id": freeze["hermes_docker_image_id"],
            "freeze_snapshot_path": str(freeze["freeze_snapshot_path"]),
            "panel_snapshot_path": str(freeze["panel_snapshot_path"]),
        }
    blind = {"run_id": run_id, "task_id": task["id"], "category": task["category"],
             "rubric": task["rubric"], "rubric_max": 5, "artifact_path": result["artifact_path"],
             "diagnostic": diagnostic}
    BLIND_DIR.mkdir(parents=True, exist_ok=True)
    (BLIND_DIR / f"{run_id}.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with RESULTS_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
    return result


def result_rows() -> list[dict]:
    if not RESULTS_PATH.is_file():
        return []
    rows = []
    for line in RESULTS_PATH.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def scores_by_run() -> dict[str, dict]:
    if not SCORES_PATH.is_file():
        return {}
    scores = {}
    for line in SCORES_PATH.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        scores[item["run_id"]] = item
    return scores


def render_report() -> str:
    rows = [row for row in result_rows() if not row.get("diagnostic", False)]
    scores = scores_by_run()
    if not rows:
        return "Aucun run Hermes/OpenRouter complet enregistré (les runs diagnostic sont exclus)."
    groups: dict[tuple[str, str, str, str], list[dict]] = {}
    for row in rows:
        groups.setdefault((row["protocol_revision"], row["freeze_hash"], row["system"], row["model"]), []).append(row)
    lines = ["# Résultats Hermes/OpenRouter", "", "Coût par succès = coûts mesurés / runs réussis, échecs inclus dans le coût total.", "", "| Protocole / freeze | Modèle OpenRouter | Runs | Réussites | Taux | Coût mesuré USD | Coût / succès USD | Temps médian s | Tokens entrée/sortie/cache lecture/écriture | Score moyen / gate |", "|---|---|---:|---:|---:|---:|---:|---:|---|---:|"]
    for (revision, freeze_hash, system, model), group in sorted(groups.items()):
        successes = sum(bool(row.get("success")) for row in group)
        known_costs = [row.get("cost_usd") for row in group]
        cost = sum(known_costs) if all(isinstance(value, (int, float)) for value in known_costs) else None
        elapsed = statistics.median(row["elapsed_seconds"] for row in group)
        def total(name: str):
            values = [row.get(name) for row in group]
            return sum(values) if all(isinstance(value, int) for value in values) else "indisponible"
        rubric = [scores[row["run_id"]]["score"] for row in group if row["run_id"] in scores]
        cost_text = f"{cost:.6f}" if cost is not None else "indisponible"
        per_success = f"{cost / successes:.6f}" if cost is not None and successes else ("indéfini" if cost is not None else "indisponible")
        rubric_mean = statistics.mean(rubric) if rubric else None
        threshold = group[0]["quality_threshold_score"]
        rubric_text = f"{rubric_mean:.2f} ({'OK' if len(rubric) == len(group) and rubric_mean >= threshold else 'NON' if len(rubric) == len(group) else 'à noter'})"
        lines.append(
            f"| {revision} / {freeze_hash[:8]} | {system} / {model} | {len(group)} | {successes} | {successes / len(group):.1%} | {cost_text} | {per_success} | {elapsed:.1f} | {total('input_tokens')}/{total('output_tokens')}/{total('cached_input_tokens')}/{total('cache_creation_tokens')} | {rubric_text} |"
        )
    lines.extend(["", "Les coûts de cache restent indisponibles lorsque le harness ne les expose pas dans son rapport; le coût total mesuré inclut les appels auxiliaires Hermes lorsque signalés.", f"Runs source : `{RESULTS_PATH.relative_to(ROOT)}`", "Scores pseudonymisés : `runs/scores.jsonl`; attribuer chaque note en consultant seulement la fiche UUID et l'artefact.", ""])
    return "\n".join(lines)


def record_score(run_id: str, score: int, note: str) -> dict:
    row = next((item for item in result_rows() if item["run_id"] == run_id), None)
    if row is None:
        raise BenchmarkError(f"Run inconnu: {run_id}")
    if not (BLIND_DIR / f"{run_id}.json").is_file():
        raise BenchmarkError(f"Fiche de notation aveugle absente pour le run {run_id}")
    if not 1 <= score <= 5:
        raise BenchmarkError("Le score de rubrique doit être entre 1 et 5.")
    item = {"run_id": run_id, "score": score, "scored_at_utc": utc_now(), "note": note[:500]}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with SCORES_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    return item


def validate_panel() -> None:
    freeze = read_json(FREEZE_PATH)
    image_id = freeze.get("hermes_docker_image_id")
    if not isinstance(image_id, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
        raise BenchmarkError("Renseigner l'ID sha256 exact de l'image Hermes dans benchmark/freeze.json avant validate-panel.")
    if command_version(docker_command("image", "inspect", "--format", "{{.Id}}", DOCKER_IMAGE), env=local_docker_environment()) != image_id:
        raise BenchmarkError("L'image Docker locale ne correspond pas à l'ID gelé.")
    solutions = read_json(BENCHMARK / "reference_solutions.json")

    tasks = tasks_by_id()
    if set(tasks) != set(solutions):
        raise BenchmarkError("Le panel et les solutions de référence ne contiennent pas les mêmes tâches.")
    temp_root = RESULTS_DIR / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    for task_id, task in tasks.items():
        fixture = (BENCHMARK / task["workspace"]).resolve()
        with tempfile.TemporaryDirectory(prefix=f"panel-check-{task_id}-", dir=temp_root) as temporary:
            baseline = Path(temporary) / "baseline"
            shutil.copytree(fixture, baseline)
            baseline_passes, _ = run_verifier(task_id, baseline, image_id, str(uuid.uuid4()))
            if baseline_passes:
                raise BenchmarkError(f"L'état initial passe le vérificateur: {task_id}")
            reference = Path(temporary) / "reference"
            shutil.copytree(fixture, reference)
            (reference / "src" / "qualitykit.py").write_text(solutions[task_id], encoding="utf-8")
            reference_passes, _ = run_verifier(task_id, reference, image_id, str(uuid.uuid4()))
            if not reference_passes:
                raise BenchmarkError(f"La solution de référence échoue au vérificateur: {task_id}")
        print(f"OK {task_id}: état initial refusé, solution de référence acceptée")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("preflight", help="vérifier les prérequis et le freeze")
    sub.add_parser("validate-panel", help="vérifier les états initiaux et solutions de référence")
    sub.add_parser("panel-hash", help="afficher l'empreinte du panel versionné")
    panel = sub.add_parser("run-panel", help="exécuter le panel gelé de façon séquentielle et randomisée")
    panel.add_argument("--limit", type=int, help="limiter à N premières trajectoires (diagnostic, à exclure des résultats)")
    single = sub.add_parser("run", help="exécuter une trajectoire isolée")
    single.add_argument("task_id")
    single.set_defaults(system="hermes")
    single.add_argument("trial", type=int)
    single.add_argument("--model", required=True, help="modèle OpenRouter explicitement gelé")
    score = sub.add_parser("score", help="ajouter une note de rubrique aveugle sur 5")
    score.add_argument("run_id")
    score.add_argument("value", type=int)
    score.add_argument("--note", default="")
    sub.add_parser("report", help="agréger les mesures actuellement disponibles")
    args = parser.parse_args()
    try:
        if args.action == "preflight":
            report = preflight(complete=True)
            for name, passed in report["checks"].items():
                print(f"{'OK' if passed else 'ECHEC'} {name}")
            return 0 if all(report["checks"].values()) else 2
        if args.action == "report":
            print(render_report())
            return 0
        if args.action == "panel-hash":
            print(panel_hash())
            return 0
        if args.action == "validate-panel":
            validate_panel()
            return 0
        if args.action == "score":
            print(json.dumps(record_score(args.run_id, args.value, args.note), ensure_ascii=False))
            return 0
        ensure_preflight(complete=True)
        freeze = load_freeze()
        freeze["freeze_snapshot_path"], freeze["panel_snapshot_path"] = prepare_run_snapshots(freeze)
        tasks = tasks_by_id()
        prior_rows = result_rows()
        protocol_rows = [row for row in prior_rows if row.get("protocol_revision") == freeze["protocol_revision"]]
        other_freezes = [row for row in protocol_rows if row.get("freeze_hash") != freeze["freeze_sha256"]]
        if other_freezes:
            raise BenchmarkError("Des résultats existent sous un autre freeze pour ce protocole. Incrémenter protocol_revision et conserver les anciennes données séparément.")
        if args.action == "run":
            if args.task_id not in tasks:
                raise BenchmarkError(f"Tâche inconnue: {args.task_id}")
            if not 1 <= args.trial <= freeze["repetitions"]:
                raise BenchmarkError("trial hors plage du freeze")
            if args.model not in freeze["openrouter_models"]:
                raise BenchmarkError("--model doit correspondre à l'un des modèles OpenRouter gelés.")
            model = args.model
            duplicate = any(
                row.get("task_id") == args.task_id and row.get("system") == "hermes"
                and row.get("model") == model and row.get("trial") == args.trial
                and row.get("freeze_hash") == freeze["freeze_sha256"]
                for row in prior_rows
            )
            if duplicate:
                raise BenchmarkError("Cette trajectoire existe déjà; aucune relance automatique n'est permise.")
            result = execute(tasks[args.task_id], "hermes", model, args.trial, freeze, diagnostic=True)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 0
        jobs = []
        for task in tasks.values():
            for trial in range(1, freeze["repetitions"] + 1):
                for model in freeze["openrouter_models"]:
                    jobs.append((task, "hermes", model, trial))
        random.Random(freeze["run_order_seed"]).shuffle(jobs)
        original_order = jobs[:]
        if args.limit is not None:
            if args.limit < 1:
                raise BenchmarkError("--limit doit être positif")
            jobs = jobs[:args.limit]
        diagnostic = args.limit is not None
        if not diagnostic and any(row.get("diagnostic") for row in protocol_rows):
            raise BenchmarkError("Des runs diagnostics ont déjà consommé la même enveloppe. Incrémenter protocol_revision avant un nouveau panel complet.")
        prior_cells = {
            (row.get("task_id"), row.get("model"), row.get("trial"))
            for row in protocol_rows if not row.get("diagnostic")
        }
        prior_any_cells = {
            (row.get("task_id"), row.get("model"), row.get("trial"))
            for row in protocol_rows
        }
        all_cells = [(job[0]["id"], job[2], job[3]) for job in original_order]
        if len(prior_cells) != len([row for row in protocol_rows if not row.get("diagnostic")]):
            raise BenchmarkError("Résultats dupliqués détectés dans le panel précédent.")
        if any(cell not in all_cells for cell in prior_cells):
            raise BenchmarkError("Des résultats antérieurs ne correspondent pas au panel courant.")
        ordered_jobs = [(index, job) for index, job in enumerate(original_order, 1) if job in jobs]
        jobs_to_run = [
            (index, job) for index, job in ordered_jobs
            if (job[0]["id"], job[2], job[3]) not in prior_cells
        ]
        if args.limit is not None and any(
            (job[0]["id"], job[2], job[3]) in prior_any_cells for job in jobs
        ):
            raise BenchmarkError("Une des trajectoires diagnostiques demandées existe déjà; aucune relance n'est permise.")
        if args.limit is None and not jobs_to_run:
            print("Le panel gelé est déjà complet; aucune nouvelle trajectoire lancée.")
            return 0
        for index, job in jobs_to_run:
            result = execute(*job, freeze, diagnostic=diagnostic, order_index=index)
            print(f"{index}/{len(original_order)} {result['task_id']} {result['system']} {result['model']} trial {result['trial']}: {'PASS' if result['success'] else 'FAIL'} ({result['elapsed_seconds']:.1f}s)")
        return 0
    except BenchmarkError as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError, KeyError, TypeError, ValueError) as exc:
        print(f"Erreur d’exécution: {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
