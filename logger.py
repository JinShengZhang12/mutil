import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("chat_logs.jsonl")
STUDENT_LOG_DIR = Path("student_logs")
TEACHER_PASSWORD = "T123456"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _safe_student_id(student_id) -> str:
    text = str(student_id or "").strip()
    if not text:
        return "unknown_student"
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in text)
    return cleaned or "unknown_student"


def _append_jsonl(path: Path, payload: dict) -> None:
    _ensure_parent(path)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **(payload or {}),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_all_interactions(student_id, payload):
    safe_id = _safe_student_id(student_id)
    data = dict(payload or {})
    data.setdefault("student_id", safe_id)
    _append_jsonl(LOG_FILE, data)


def save_student_dialog(student_id, payload):
    safe_id = _safe_student_id(student_id)
    file_path = STUDENT_LOG_DIR / f"{safe_id}.jsonl"
    data = dict(payload or {})
    data.setdefault("student_id", safe_id)
    _append_jsonl(file_path, data)


def read_logs(limit=60):
    if not LOG_FILE.exists():
        return []

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 60

    if limit <= 0:
        return []

    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    records = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append({"raw": line, "error": "invalid_jsonl"})
    return records


def secure_read_logs(password):
    if password != TEACHER_PASSWORD:
        return {"success": False, "message": "密码错误", "logs": []}
    return {"success": True, "message": "读取成功", "logs": read_logs()}