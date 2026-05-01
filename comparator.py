import json
import logging
import os
from typing import Optional

import config

logger = logging.getLogger(__name__)


def load_snapshot() -> Optional[dict]:
    if not os.path.exists(config.SNAPSHOT_FILE):
        return None
    try:
        with open(config.SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load snapshot: {e}")
        return None


def save_snapshot(events: list[dict]):
    data = {e["id"]: e for e in events}
    with open(config.SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compare(old: dict, new: list[dict]) -> list[dict]:
    """
    Returns list of changes, each change is:
    { type: "new"|"cancelled"|"changed", event: {...}, old_event: {...}|None, changes: [...] }
    """
    new_map = {e["id"]: e for e in new}
    changes = []

    # Новые и изменённые
    for ev_id, ev in new_map.items():
        if ev_id not in old:
            changes.append({"type": "new", "event": ev, "old_event": None, "changes": []})
        else:
            old_ev = old[ev_id]
            diffs = []
            if ev["date_start"] != old_ev["date_start"] or ev["date_end"] != old_ev["date_end"]:
                diffs.append(("дата", f"{old_ev['date_start']}–{old_ev['date_end']}", f"{ev['date_start']}–{ev['date_end']}"))
            if ev["time_start"] != old_ev["time_start"]:
                diffs.append(("время", old_ev["time_start"], ev["time_start"]))
            if ev["title"] != old_ev["title"]:
                diffs.append(("название", old_ev["title"], ev["title"]))
            if ev["format"] != old_ev["format"]:
                diffs.append(("формат", old_ev["format"], ev["format"]))
            if diffs:
                changes.append({"type": "changed", "event": ev, "old_event": old_ev, "changes": diffs})

    # Отменённые
    for ev_id, old_ev in old.items():
        if ev_id not in new_map:
            changes.append({"type": "cancelled", "event": old_ev, "old_event": None, "changes": []})

    return changes


def format_change_message(change: dict) -> str:
    ev = change["event"]
    t = change["type"]

    date_str = ev["date_start"]
    if ev.get("date_end") and ev["date_end"] != ev["date_start"]:
        date_str += f"–{ev['date_end']}"

    time_str = ev.get("time_start", "")
    if ev.get("timezone"):
        time_str += f" {ev['timezone']}"

    header = f"📅 <b>{ev['title']}</b>\n🗓 {date_str}"
    if time_str:
        header += f" | ⏰ {time_str}"
    if ev.get("responsible"):
        header += f"\n👤 {ev['responsible']}"

    if t == "new":
        return f"🆕 <b>Новое мероприятие</b>\n{header}"

    elif t == "cancelled":
        return f"❌ <b>Мероприятие отменено</b>\n{header}"

    elif t == "changed":
        lines = [f"✏️ <b>Изменение в мероприятии</b>\n{header}\n"]
        for field, old_val, new_val in change["changes"]:
            lines.append(f"• {field}: <s>{old_val}</s> → <b>{new_val}</b>")
        return "\n".join(lines)

    return ""
